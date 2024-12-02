import csv
from cs50 import SQL

db = SQL("sqlite:///finance.db")

with open("Book1.csv", newline="",) as file:
    rows = csv.reader(file, dialect='excel')
    for row in rows:
        db.execute("INSERT INTO stocks (stock_symbol) VALUES(?)", row[0])