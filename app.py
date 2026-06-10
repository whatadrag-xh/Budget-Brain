from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify, flash
from database import get_summary, get_all_transactions, add_transaction, delete_transaction
from analysis import generate_all_charts
from ai_agent import chat
from inference import detect_anomalies, forecast_next_month
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from user_model import User
from database import create_user, get_user_by_username, get_user_by_id
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.secret_key = "your_secret_key"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    user = get_user_by_id(user_id)
    if user:
        return User.from_db(user)
    return None

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        if get_user_by_username(username):
            flash("Username already exists.", "error")
            return render_template("register.html")
        password = request.form["password"]
        password_hash = generate_password_hash(password)
        create_user(username, password_hash)
        flash("Account created! Please log in.", "success")
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = get_user_by_username(username)
        if user and check_password_hash(user["password_hash"], password):
            login_user(User.from_db(user))
            return redirect(url_for("index"))
        else: 
            flash("Invalid username or password", "error")
        return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route("/")
@login_required
def index():
    summary = get_summary(current_user.id)
    transactions = get_all_transactions(current_user.id)
    anomalies = detect_anomalies()
    forecast = forecast_next_month()
    return render_template("index.html", summary=summary, transactions=transactions, anomalies=anomalies, forecast=forecast)

@app.route("/add", methods=["POST"])
@login_required
def add():
    date = request.form["date"]
    description = request.form["description"]
    category = request.form["category"]
    amount = request.form["amount"]
    type = request.form["type"]
    add_transaction(date, description, amount, category, type, current_user.id)
    return redirect(url_for("index"))

@app.route("/delete/<int:id>", methods=["POST"])
@login_required
def delete(id):
    delete_transaction(id, current_user.id)
    return redirect(url_for("index"))

@app.route("/analysis")
@login_required
def analysis():
    charts = generate_all_charts()
    return render_template("analysis.html", charts=charts)

@app.route("/charts/<filename>")
def serve_chart(filename):
    return send_file(f"charts/{filename}")

@app.route("/chat", methods=["GET"])
@login_required
def chat_page():
    return render_template("chat.html")

@app.route("/api/chat", methods=["POST"])
@login_required
def api_chat():
    data = request.get_json()
    message = data["message"]
    history = data["history"]
    reply = chat(message, history)
    return jsonify({"response": reply})

if __name__ == "__main__":
    app.run(debug=True)