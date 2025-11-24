from flask import Flask, abort
from sqlalchemy import create_engine, text

app = Flask(__name__)
engine = create_engine("sqlite:///members.db", echo=False)

def mask(s: str) -> str:
    return "*" * len(s)

@app.get("/users/<username>")
def show_user(username):
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
    """, 200

if __name__ == "__main__":
    app.run(debug=True)
