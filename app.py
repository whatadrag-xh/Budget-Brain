from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify
from database import get_summary, get_all_transactions, add_transaction, delete_transaction
from analysis import generate_all_charts
from ai_agent import chat
from inference import detect_anomalies, forecast_next_month

app = Flask(__name__)

@app.route("/")
def index():
    summary = get_summary()
    transactions = get_all_transactions()
    anomalies = detect_anomalies()
    forecast = forecast_next_month()
    return render_template("index.html", summary=summary, transactions=transactions, anomalies=anomalies, forecast=forecast)

@app.route("/add", methods=["POST"])
def add():
    date = request.form["date"]
    description = request.form["description"]
    category = request.form["category"]
    amount = request.form["amount"]
    type = request.form["type"]
    print(f"DEBUG: date={date}, desc={description}, amount={amount}, cat={category}, type={type}")
    add_transaction(date, description, amount, category, type)
    return redirect(url_for("index"))

@app.route("/delete/<int:id>", methods=["POST"])
def delete(id):
    delete_transaction(id)
    return redirect(url_for("index"))

@app.route("/analysis")
def analysis():
    charts = generate_all_charts()
    return render_template("analysis.html", charts=charts)

@app.route("/charts/<filename>")
def serve_chart(filename):
    return send_file(f"charts/{filename}")

@app.route("/chat", methods=["GET"])
def chat_page():
    return render_template("chat.html")

@app.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.get_json()
    message = data["message"]
    history = data["history"]
    reply = chat(message, history)
    return jsonify({"response": reply})

if __name__ == "__main__":
    app.run(debug=True)