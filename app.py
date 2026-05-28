from flask import Flask, render_template
from database import get_summary, get_all_transactions

app = Flask(__name__)

@app.route("/")
def index():
    summary = get_summary()
    transactions = get_all_transactions()
    return render_template("index.html", summary=summary, transactions=transactions )

if __name__ == "__main__":
    app.run(debug = True)