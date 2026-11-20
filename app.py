from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "guardian_secret"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///guardian.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))


class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    location = db.Column(db.String(200))
    details = db.Column(db.Text)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        fullname = request.form["fullname"]
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])

        user = User(
            fullname=fullname,
            email=email,
            password=password
        )

        db.session.add(user)
        db.session.commit()

        return redirect("/login")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session["user"] = user.fullname
            return redirect("/dashboard")

    return render_template("login.html")


@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect("/login")

    return render_template(
        "dashboard.html",
        name=session["user"]
    )


@app.route("/report", methods=["GET", "POST"])
def report():

    if request.method == "POST":

        data = Report(
            name=request.form["name"],
            location=request.form["location"],
            details=request.form["details"]
        )

        db.session.add(data)
        db.session.commit()

        return redirect("/dashboard")

    return render_template("report.html")

@app.route("/sos")
def sos():

    if "user" not in session:
        return redirect("/login")

    return render_template("sos.html")

@app.route("/admin")
def admin():

    users = User.query.all()
    reports = Report.query.all()

    return render_template(
        "admin.html",
        users=users,
        reports=reports
    )


@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")


if __name__ == "__main__":

    with app.app_context():
        db.create_all()

    app.run(debug=True)