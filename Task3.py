from flask import Flask, abort, render_template, request, redirect, url_for, session, abort
from sqlalchemy import create_engine, text

app = Flask(__name__)
app.secret_key = "b0c2e4d9b7fa3a534ad12cf9fbc94856e1"  

engine = create_engine("sqlite:///members.db", echo=False)

def mask(s: str) -> str:
    return "*" * len(s)

@app.get("/users/<username>")
def show_user(username):
    if session.get("username") != username:
        return redirect(url_for("login_form"))
    
    with engine.begin() as conn:
        row = conn.execute(
            text("""
                SELECT username, email, password, date_of_birth
                FROM users
                WHERE username = :u
            """),
            {"u": username},
        ).first()

    if not row:
        abort(404, description="User not found")

    return f"""
    <!doctype html>
    <html><head><meta charset="utf-8"><title>User {row.username}</title></head>
    <body>
      <h2>User details</h2>
      <table border="1" cellpadding="6">
        <tr><th>Username</th><td>{row.username}</td></tr>
        <tr><th>Email</th><td>{row.email}</td></tr>
        <tr><th>Password</th><td>{mask(row.password)}</td></tr>
        <tr><th>Date of Birth</th><td>{row.date_of_birth}</td></tr>
      </table>
    </body></html>
    """, 200, {"Content-Type": "text/html"}

@app.get("/login")
def login_form():
    return render_template("login.html", error=None)

@app.post("/login")
def login_submit():
    username = request.form.get("username")
    password = request.form.get("password")

    with engine.begin() as conn:
        row = conn.execute(
            text("SELECT username, password FROM users WHERE username = :u"),
            {"u": username},
        ).first()

    if row and row.password == password:
        session["username"] = row.username
        return redirect(url_for("show_user", username=row.username))
    else:
        return render_template("login.html", error="Invalid username or password.")

@app.get("/logout")
def logout():
    session.clear()
    return redirect(url_for("login_form"))

if __name__ == "__main__":
    app.run(debug=True)
