from flask import Flask, request, jsonify
import sqlite3

app = Flask(_name_)

def get_connection():
    return sqlite3.connect("school_data.db")

@app.route("/add_absence", methods=["POST"])
def add_absence():
    data = request.json

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO attendance (student_id, date, day, session, period, allowed)
        VALUES (?, ?, ?, ?, ?, 0)
    """, (
        data["student_id"],
        data["date"],
        data["day"],
        data["session"],
        data["period"]
    ))

    conn.commit()
    conn.close()

    return jsonify({"status": "ok"})

@app.route("/")
def home():
    return "Server is running 🚀"