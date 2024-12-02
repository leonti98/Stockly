from ast import And, Div
from crypt import methods
import os
from pickle import FALSE, TRUE

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from sqlalchemy import Select
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime


from helpers import apology, login_required, lookup, usd

db = SQL("sqlite:///finance.db")

"""Sell shares of stock"""
user_id = 1
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
        stock_symbol, transaction_type
    ORDER BY
        stock_symbol, transaction_type ASC""",
    user_id,
)
if not user_stocks:
    user_stocks = [{}]
    
for stock in user_stocks:
    print(stock)

for i in range(len(user_stocks)):
        if user_stocks[i]["transaction_type"] == "b":
            current_info = lookup(user_stocks[i]["stock_symbol"])
            if current_info:
                current_price = current_info["price"]
                user_stocks[i]["current_price"] = current_price
        else:            
            user_stocks[i - 1]["quantity"] -= user_stocks[i]["quantity"]
            

# if method post   
user_selected_stock = "AMZN"

for stock in user_stocks:
    if stock["transaction_type"] == "b" and stock["stock_symbol"] == user_selected_stock:
        selected_stock = stock
        break

print (selected_stock)

selected_quantity = 100

if selected_quantity < 0 or selected_quantity > selected_stock["quantity"]:
    print("not enough")
else:
    print("sell")
    

print(type(selected_stock["current_price"]))
print(type(selected_stock["current_price"]))

    