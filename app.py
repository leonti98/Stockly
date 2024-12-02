import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
import numpy as np

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    user_id = session["user_id"]
    user_info = db.execute(
        """
    SELECT
        username, cash
    FROM
        users
    WHERE
        id = ?""",
        user_id,
    )
    # Get necessarry data from database
    user_info[0]["grand_total"] = user_info[0]["cash"]
    user_stocks = db.execute(
        """
        SELECT
            stock_symbol,
            SUM(quantity) AS quantity,
            ROUND(AVG(transaction_amount), 2) AS avg_price,
            transaction_type,
            ROUND(SUM(transaction_amount * quantity), 2) AS total_transaction_amount
        FROM
            users_stocks
            INNER JOIN stocks ON users_stocks.stock_id = stocks.stock_id
        WHERE
            user_id = ?
        GROUP BY
            stock_symbol, transaction_type
        ORDER BY
            stock_symbol, transaction_type ASC""",
        user_id,
    )
    if not user_stocks:
        return render_template(
            "/index.html", stocks=[], user_info=user_info, totals=[], grand_total=0
        )

    for i in range(len(user_stocks)):
        current_info = lookup(user_stocks[i]["stock_symbol"])
        if current_info:
            current_price = current_info["price"]
            user_stocks[i]["current_price"] = current_price
            user_stocks[i]["total_current_value"] = (
                user_stocks[i]["quantity"] * current_price
            )

        if user_stocks[i]["transaction_type"] == "s":
            user_stocks[i - 1]["total_transaction_amount"] -= user_stocks[i][
                "total_transaction_amount"
            ]
            user_stocks[i - 1]["quantity"] -= user_stocks[i]["quantity"]
            user_stocks[i - 1]["total_current_value"] -= user_stocks[i][
                "total_current_value"
            ]

    stocks = []
    quantities = []
    averages = []
    stocks_value = 0
    totals = {"quantity": 0, "weighted_avg": 0, "total_value": 0, "total_paid": 0}
    for stock in user_stocks:
        if stock["transaction_type"] == "b" and stock["quantity"] != 0:
            stocks.append(stock)
            stocks_value += stock["total_current_value"]
            totals["quantity"] += stock["quantity"]
            totals["total_value"] += stock["total_current_value"]
            totals["total_paid"] += stock["total_transaction_amount"]
            quantities.append(stock["quantity"])
            averages.append(stock["avg_price"])
    try:
        weighted_avg = np.average(averages, weights=quantities)
        totals["weighted_avg"] = weighted_avg  # type: ignore
    except:
        weighted_avg = 0
    grand_total = totals["total_value"] + user_info[0]["cash"]
    return render_template(
        "/index.html",
        stocks=stocks,
        user_info=user_info,
        stocks_value=stocks_value,
        totals=totals,
        grand_total=grand_total,
    )


@app.route("/search")
@login_required
def search():
    q = request.args.get("q")
    if q:
        stocks = db.execute(
            """
        SELECT
            stock_symbol
        FROM
            stocks
        WHERE
            stock_symbol LIKE ?
        ORDER BY
            stock_symbol ASC LIMIT 15""",
            q + "%",
        )
    else:
        stocks = []
    return jsonify(stocks)


@app.route("/userStocks")
@login_required
def userStocks():
    symbol = request.args.get("stock")
    stocks = db.execute(
        """
    SELECT
        stock_symbol,
        SUM(quantity) AS quantity,
        transaction_type
    FROM
        users_stocks
        INNER JOIN stocks ON users_stocks.stock_id = stocks.stock_id
    WHERE
        user_id = ?
        AND stock_symbol = ?
    GROUP BY
        stock_symbol,
        transaction_type
    ORDER BY
        transaction_type ASC
    """,
        session["user_id"],
        symbol,
    )

    if len(stocks) == 2:
        quantity = stocks[0]["quantity"] - stocks[1]["quantity"]
        try:
            current_price = lookup(symbol)
            if current_price:
                current_price = current_price["price"]
        except:
            current_price = 0
    elif len(stocks) == 1:
        quantity = stocks[0]["quantity"]
        try:
            current_price = lookup(symbol)
            if current_price:
                current_price = current_price["price"]
        except:
            current_price = 0
    else:
        current_price = 0
        quantity = 0

    stock_info = {"quantity": quantity, "current_price": current_price}

    return jsonify(stock_info)


@app.route("/availability")
def availability():
    user_id = session["user_id"]
    stock = request.args.get("stock")
    if stock:
        transactions = db.execute(
            """
        SELECT
            stock_symbol, SUM(quantity) AS quantity, transaction_type
        FROM
            users_stocks
            INNER JOIN stocks ON users_stocks.stock_id = stocks.stock_id
        WHERE
            user_id = ? AND stock_symbol = ?
        GROUP BY
            stock_symbol, transaction_type
        ORDER BY
            stock_symbol, transaction_type ASC""",
            user_id,
            stock,
        )
        buy_transactions = transactions[0]["quantity"]
        stock_availability = buy_transactions
        if len(transactions) == 2:
            sell_transactions = transactions[1]["quantity"]
            stock_availability -= sell_transactions
    else:
        return []
    return jsonify(stock_availability)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":
        # verify stock and quantity
        user_symbol = request.form.get("symbol")
        stock_quantity = request.form.get("shares")
        if not user_symbol:
            return apology("Please specify stock symbol")
        elif not stock_quantity:
            return apology("Please indicate quantity")
        if "." in stock_quantity:
            return apology("Input must be integer")
        try:
            stock_quantity = int(stock_quantity)
        except:
            return apology("Input must be numeric")
        if stock_quantity <= 0:
            return apology("you must input positive number")

        # Check if provided stock symbol exists
        user_symbol = user_symbol.upper()
        stock_info = lookup(user_symbol)
        if stock_info:
            stock_price = stock_info["price"]
            stock_symbol = stock_info["symbol"]
            existing_stocks = db.execute(
                """
            SELECT
                stock_symbol
            FROM
                stocks
            """,
            )
            # Check if stock is in database
            in_database = False
            for i in range(len(existing_stocks)):
                if user_symbol == existing_stocks[i]["stock_symbol"]:
                    in_database = True
                    break
            if not in_database:
                db.execute(
                    """
                        INSERT INTO stocks (stock_symbol)
                        VALUES(?)
                        """,
                    stock_symbol,
                )
            db_stock_id = db.execute(
                """
            SELECT
                stock_id
            FROM
                stocks
            WHERE
                stock_symbol = ?""",
                stock_symbol,
            )
            if not db_stock_id:
                return apology(f"Stock {user_symbol} not found")
        else:
            return apology(f"Stock {user_symbol} not found")

        # Update users cash balance
        user_id = session["user_id"]
        user_cash = db.execute(
            """
                                SELECT
                                    cash
                                FROM
                                    users
                                WHERE
                                    id = ?""",
            user_id,
        )
        if user_cash:
            current_user_cash = float(user_cash[0]["cash"])
            stock_quantity = int(stock_quantity)
            total_for_stocks = stock_price * stock_quantity
            updated_user_cash = current_user_cash - total_for_stocks
            if updated_user_cash < 0:
                return apology("Not enough money on the balance")
            db.execute(
                """
            UPDATE
                users
            SET
                cash = ?
            WHERE
                id = ?""",
                updated_user_cash,
                user_id,
            )

        # Add stock purchase to database
        current_datetime = datetime.now()
        current_time = current_datetime.strftime("%H:%M:%S")
        current_date = current_datetime.date()
        db.execute(
            """
        INSERT INTO users_stocks (
            user_id,
            stock_id,
            transaction_amount,
            quantity,
            transaction_type,
            date,
            time)
        VALUES(?, ?, ?, ?, ?, ?, ?)""",
            user_id,
            db_stock_id[0]["stock_id"],
            stock_price,
            stock_quantity,
            "b",
            current_date,
            current_time,
        )
        return redirect("/")

    # If method = "get" pass info to populate purchase history table
    user_id = session["user_id"]
    user_stocks = db.execute(
        """
    SELECT
        stock_symbol,
        transaction_amount,
        quantity,
        date,
        time,
        transaction_type
    FROM
        users_stocks
    INNER JOIN
        stocks ON users_stocks.stock_id = stocks.stock_id
    WHERE
        user_id = ? AND transaction_type = 'b'
    ORDER BY date DESC, time DESC
    LIMIT 10""",
        user_id,
    )
    current_stocks = {}
    for stock in user_stocks:
        if stock["stock_symbol"] not in current_stocks:
            current_stock_info = lookup(stock["stock_symbol"])
            if current_stock_info:
                current_price = current_stock_info["price"]
                current_stocks[current_stock_info["symbol"]] = current_price
    return render_template(
        "buy.html", user_stocks=user_stocks, current_stocks=current_stocks
    )


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    user_id = session["user_id"]
    # Get necessarry data from database
    user_stocks = db.execute(
        """SELECT stock_symbol, transaction_amount, quantity, date, time, transaction_type
        FROM users_stocks
        INNER JOIN stocks ON users_stocks.stock_id = stocks.stock_id
        WHERE user_id = ?
        ORDER BY date DESC, time DESC
        LIMIT 10""",
        user_id,
    )
    current_stocks = {}
    for stock in user_stocks:
        if stock["stock_symbol"] not in current_stocks:
            current_stock_info = lookup(stock["stock_symbol"])
            if current_stock_info:
                current_price = current_stock_info["price"]
                stock["price"] = current_price
    return render_template("/history.html", user_stocks=user_stocks)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        # Ensure username was submitted
        if not username:
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not password:
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":
        stock_info = lookup(request.form.get("symbol"))
        if stock_info:
            return render_template("/quoted.html", stock_info=stock_info)
        else:
            return apology(
                f"Could not find stock with name {request.form.get('symbol')}"
            )
    else:
        return render_template("/quote.html")


@app.route("/quoted")
@login_required
def quoted():
    return render_template("/quoted.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        new_username = request.form.get("username")
        new_password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        existing_usernames = db.execute(
            """
                                        SELECT
                                            username
                                        FROM
                                            users
                                        """
        )
        # Endusre username was submitted
        if not new_username:
            return apology("must provide username", 400)
        elif new_username in existing_usernames:
            return apology(f"username {new_username} already exists", 400)
        # Ensure password was submitted
        elif not new_password:
            return apology("must provide password", 400)
        # Ensure password confirmation exists
        elif not confirmation:
            return apology("must confirm password", 400)
        elif confirmation != new_password:
            return apology("Password does not match confirmation", 400)
        else:
            hashed_pass = generate_password_hash(new_password)
            existing_users = db.execute("SELECT * FROM users")
            for user in existing_users:
                if user["username"] == new_username:
                    return apology(f"username '{new_username}' already exists", 400)
        db.execute(
            "INSERT INTO users (username, hash) VALUES (?, ?)",
            new_username,
            hashed_pass,
        )

        return render_template("/login.html", registered=True)
    return render_template("/register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""

    if request.method == "POST":
        user_selected_stock = request.form.get("symbol")
        if not user_selected_stock:
            return apology("Input stock symbol")
        else:
            user_selected_stock.upper()

        selected_stock = db.execute(
            """
                   SELECT
                        users_stocks.stock_id,
                        stock_symbol,
                        SUM(quantity) AS quantity,
                        transaction_type
                    FROM
                        users_stocks
                        INNER JOIN stocks ON users_stocks.stock_id = stocks.stock_id
                    WHERE
                        user_id = ?
                        AND stock_symbol = ?
                    GROUP BY
                        stock_symbol,
                        transaction_type
                    ORDER BY
                        transaction_type ASC
                   """,
            session["user_id"],
            user_selected_stock,
        )

        if len(selected_stock) == 2:
            selected_stock[0]["quantity"] = (
                selected_stock[0]["quantity"] - selected_stock[1]["quantity"]
            )
            stock = selected_stock[0]
        elif len(selected_stock) == 1:
            stock = selected_stock[0]
        else:
            return apology("Stop hacking :@")

        current_price = lookup(user_selected_stock)
        if current_price:
            current_price = current_price["price"]
            stock["current_price"] = current_price
        else:
            return apology("can't get current stock price")

        selected_quantity = request.form.get("shares")
        if selected_quantity:
            try:
                selected_quantity = int(selected_quantity)
            except:
                return apology("selected quantity must be integer")
        if selected_quantity <= 0 or selected_quantity > stock["quantity"]:  # type: ignore
            return apology(
                f"You don't have {selected_quantity} shares of {user_selected_stock}"
            )

        current_datetime = datetime.now()
        current_time = current_datetime.strftime("%H:%M:%S")
        current_date = current_datetime.date()

        db.execute(
            """
            INSERT INTO
                users_stocks (
                    user_id,
                    stock_id,
                    transaction_amount,
                    quantity,
                    transaction_type,
                    date,
                    time
                )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            session["user_id"],
            stock["stock_id"],
            stock["current_price"],
            selected_quantity,
            "s",
            current_date,
            current_time,
        )

        user_cash = db.execute(
            "SELECT cash FROM users WHERE id = ?", session["user_id"]
        )
        if user_cash:
            current_user_cash = float(user_cash[0]["cash"])
            total_for_stocks = stock["current_price"] * selected_quantity
            updated_user_cash = round(current_user_cash + total_for_stocks, 2)
            db.execute(
                """
                        UPDATE users
                        SET
                            cash = ?
                        WHERE
                            id = ?

                       """,
                updated_user_cash,
                session["user_id"],
            )
        else:
            return apology("can't update users cash balance")

        return redirect("/")

    user_id = session["user_id"]
    user_stocks = db.execute(
        """
            SELECT
                stock_symbol,
                stocks.stock_id,
                SUM(quantity) AS quantity,
                transaction_type
            FROM
                users_stocks
                INNER JOIN stocks ON users_stocks.stock_id = stocks.stock_id
            WHERE
                user_id = ?
            GROUP BY
                stock_symbol,
                transaction_type
            ORDER BY
                stock_symbol,
                transaction_type ASC""",
        user_id,
    )

    if user_stocks:
        for i in range(len(user_stocks)):
            if user_stocks[i]["transaction_type"] == "s":
                user_stocks[i - 1]["quantity"] -= user_stocks[i]["quantity"]

    left_stocks = []
    left_stocks = [
        stock
        for stock in user_stocks
        if stock["transaction_type"] == "b" and stock["quantity"] > 0
    ]

    return render_template("/sell.html", user_stocks=left_stocks)


@app.route("/changePassword", methods=["POST", "GET"])
def changePassword():
    if request.method == "POST":
        current_password = db.execute(
            """
            SELECT hash
            FROM users
            WHERE id = ?
            """,
            session["user_id"],
        )

        users_password = request.form.get("userPassword")
        new_password = request.form.get("newPassword")
        confirmation = request.form.get("verifyPassword")
        # Endusre username was submitted
        if not users_password:
            return apology("must provide current password", 403)
        # Ensure password was submitted
        elif not new_password:
            return apology("must provide new password", 403)
        # Ensure password confirmation exists
        elif not confirmation:
            return apology("must confirm password", 403)
        elif confirmation != new_password:
            return apology("Password does not match confirmation", 403)
        elif check_password_hash(current_password[0]["hash"], users_password) == False:
            return apology("wrong current password")
        else:
            hashed_pass = generate_password_hash(new_password)
            db.execute(
                """
                UPDATE users
                SET hash = ?
                WHERE id = ?
                """,
                hashed_pass,
                session["user_id"],
            )
        return redirect("/")

    return render_template("/changePassword.html")


@app.route("/addcash", methods=["POST", "GET"])
def addcash():
    current_cash = db.execute(
        """
        SELECT cash
        FROM users
        WHERE id = ?
        """,
        session["user_id"],
    )

    if request.method == "POST":
        cash_to_add = request.form.get("cashToAdd")
        if cash_to_add:
            try:
                cash_to_add = float(cash_to_add)
                cash_to_set = cash_to_add + current_cash[0]["cash"]
            except:
                return apology("something went wrong")
        else:
            cash_to_set = current_cash[0]["cash"]
        db.execute(
            """
                   UPDATE users
                   SET cash = ?
                   WHERE id = ?
                   """,
            cash_to_set,
            session["user_id"],
        )
        return render_template("/addcash.html", current_cash=cash_to_set)

    return render_template("/addcash.html", current_cash=current_cash[0]["cash"])
