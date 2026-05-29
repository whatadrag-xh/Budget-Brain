from flask import Flask, render_template, request, redirect, url_for, send_file
from database import get_summary, get_all_transactions, add_transaction, delete_transaction
from analysis import generate_all_charts

app = Flask(__name__)

@app.route("/")
def index():
    summary = get_summary()
    transactions = get_all_transactions()
    return render_template("index.html", summary=summary, transactions=transactions )

@app.route("/add", methods=["POST"])
def add():
    date= request.form["date"]
    description= request.form["description"]
    category= request.form["category"]
    amount= request.form["amount"]
    type= request.form["type"]
    add_transaction(date, description, category, amount, type)
    return redirect(url_for("index"))

@app.route("/delete/<int:id>", methods=["POST"])
def delete(id):
    delete_transaction(id)
    return redirect(url_for("index"))

@app.route("/analysis")
def analysis():
    charts= generate_all_charts()
    return render_template("analysis.html", charts=charts)

@app.route("/charts/<filename>")
def serve_chart(filename):
    return send_file(f"charts/{filename}")

if __name__ == "__main__":
    app.run(debug = True)