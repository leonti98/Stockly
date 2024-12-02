from flask import jsonify
from helpers import apology, login_required, lookup, usd
from cs50 import SQL
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, date, time

db = SQL("sqlite:///finance.db")

user_id = 1
user_symbol = "GAGAGA"


# existing_stocks = db.execute("""
#             SELECT
#                 stock_symbol
#             FROM
#                 stocks         
#             """,)

# in_database = False
# for i in range(len(existing_stocks)):
#     if user_symbol == existing_stocks[i]["stock_symbol"]:
#         in_database = True
#         break

# if not in_database:
#     # db.execute("""
#     #         INSERT INTO stocks (stock_symbol) 
#     #         VALUES(?) 
#     #         """,
#     #         user_symbol
#     # )
#     print("add to db")
# else:
#     print("dont")
    
# stocks = db.execute(
#             """
#             SELECT
#                 stock_symbol,
#                 SUM(quantity) AS quantity,
#                 transaction_type
#             FROM
#                 users_stocks
#                 INNER JOIN stocks ON users_stocks.stock_id = stocks.stock_id
#             WHERE
#                 user_id = ?
#                 AND stock_symbol = ?
#             GROUP BY
#                 stock_symbol,
#                 transaction_type
#             ORDER BY
#                 transaction_type ASC
#             """,
#             user_id, symbol
#         )

# if len(stocks) == 2:
#     quantity = stocks[0]["quantity"] - stocks[1]["quantity"]
#     try:
#         current_price = lookup(symbol)
#         if current_price:
#             current_price = current_price["price"]
#     except:
#         current_price = 0
# elif len(stocks) == 1:
#     quantity = stocks[0]["quantity"]
#     try:
#         current_price = lookup(symbol)
#         if current_price:
#             current_price = current_price["price"]
#     except:
#         current_price = 0
# else:
#     current_price = 0
#     quantity = 0

# stock_info = {"quantity": quantity, "current_price": current_price}


# print(jsonify(stock_info))


# if stocks:
#     print("not NULL")
# else:
#     print("NULL")
# 


# current_cash = db.execute(
#         """
#         SELECT cash
#         FROM users
#         WHERE id = ?
#         """,
#         1
#     )

# print(current_cash)


# current_password = db.execute(
#             """
#             SELECT hash 
#             FROM users 
#             WHERE id = ?
#             """,
#             1
#             )

# print(current_password)
# print(check_password_hash(current_password[0]['hash'], 'qweasd12'))

# for stock in user_stocks:
#     print('\n', stock)
    


# stock = "TSLA"
# transactions = db.execute("""
#     SELECT
#         stock_symbol, SUM(quantity) AS quantity, transaction_type AS transaction_amount
#     FROM
#         users_stocks
#         INNER JOIN stocks ON users_stocks.stock_id = stocks.stock_id
#     WHERE
#         user_id = ? AND stock_symbol = ?
#     GROUP BY
#         stock_symbol, transaction_type
#     ORDER BY
#         transaction_type ASC""",
#         user_id, stock)

# buy_transactions = transactions[0]['quantity']
# sell_transactions = transactions[1]['quantity']

# stock_availability = buy_transactions - sell_transactions

# print(jsonify(stock_availability))

# sold_stocks = db.execute(
#         """SELECT stock_symbol,
#             ROUND(AVG(transaction_amount), 2) AS avg_price,
#             SUM(quantity) AS total_quantity,
#             ROUND(SUM(transaction_amount * quantity), 2) AS total_sale 
#             FROM 
#             users_stocks 
#             INNER JOIN 
#             stocks ON users_stocks.stock_id = stocks.stock_id 
#             WHERE 
#             user_id = ? AND transaction_type = 's'
#             GROUP BY 
#             stock_symbol""",
#         user_id,
#     )
# for stock in sold_stocks:   
#     print(stock['total_quantity'], stock['total_sale'])


# current_datetime = datetime.now()
# current_time = current_datetime.strftime("%H:%M:%S")
# current_date = current_datetime.date()
# print(current_datetime)
# print(type(current_datetime))
# print(current_datetime.year)
# print(current_datetime.month)
# print(current_datetime.day)
# print(current_datetime.hour)
# print(current_datetime.minute)
# current_date = date.today()
# print(current_date)
# current_time = current_datetime.strftime("%Y:%M:%S")
# print(current_time)
# print(current_date)

# user_id = "1"
# stocks = db.execute("SELECT stock_symbol FROM stocks WHERE stock_id IN (SELECT stock_id FROM users_stocks)")
# print(stocks)
# stocks = db.execute("SELECT stock_symbol, transaction_amount, quantity FROM users_stocks INNER JOIN stocks ON users_stocks.stock_id = stocks.stock_id")
# for stock in stocks:
#     print(stock)

# grouped_stocks = db.execute("SELECT stock_symbol, ROUND(AVG(transaction_amount), 2) AS avg_price, SUM(quantity) AS total_quantity, ROUND(SUM(transaction_amount * quantity)) FROM users_stocks INNER JOIN stocks ON users_stocks.stock_id = stocks.stock_id GROUP BY stock_symbol")
# print(grouped_stocks)
# for stock in grouped_stocks:
#     print(stock)

# user_stocks = db.execute("""SELECT 
#                          stock_symbol,
#                          ROUND(AVG(transaction_amount), 2) AS avg_price,
#                          SUM(quantity) AS total_quantity,
#                          ROUND(SUM(transaction_amount * quantity), 2) AS total_value 
#                          FROM 
#                             users_stocks 
#                          INNER JOIN 
#                             stocks ON users_stocks.stock_id = stocks.stock_id 
#                          WHERE 
#                             user_id = ? 
#                          GROUP BY 
#                             stock_symbol""", user_id)
# current_stocks = {}
# for stock in user_stocks:
#     if stock["stock_symbol"] not in current_stocks:
#         current_stock_info = lookup(stock["stock_symbol"])
#         if current_stock_info:
#             current_price = current_stock_info["price"]
#             stock["current_price"] = current_price

# for stock in user_stocks:
#     print(stock)
    
# existing_users = db.execute("SELECT * FROM users")
# print(existing_users)
# for user in existing_users:
#     print(user["username"])

# db.execute("UPDATE users SET cash = 10000 WHERE id = 1")

# user_stocks = db.execute("""SELECT DISTINCT 
#                                     stock_symbol 
#                                 FROM 
#                                     stocks 
#                                 WHERE 
#                                     stock_id IN (
#                                         SELECT 
#                                             stock_id 
#                                         FROM 
#                                             users_stocks 
#                                         WHERE 
#                                             user_id = ?)""", 
#                                         user_id)
# for stock in user_stocks:
#     print(stock["stock_symbol"])
    
# print(user_stocks["AAPL"])
