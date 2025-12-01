import sqlite3
from flask import Flask, render_template

app = Flask(__name__)
app.secret_key = 'your_very_secret_key'
Data = 'db.db'


def get_db_connection():

    conn = sqlite3.connect(Data)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():

    conn = get_db_connection()

    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()
    print("С БД всё хорошо.")



@app.route('/')
def index():
    return render_template('login.html')




if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=8000, debug=True)