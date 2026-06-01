from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn
def init_db():
    conn=get_db_connection()
    try:
        conn.execute('''CREATE TABLE IF NOT EXISTS assignments
                     (id INTEGER PRIMARY KEY,name TEXT,due_date TEXT,subject TEXT)''')
        conn.commit()
    except Exception as e:
        print(f"DB Error: {e}")
    finally:
        conn.close()
init_db()
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        name = request.form['assignment_name']
        due_date = request.form['due_date']
        subject = request.form['subject']

        conn = get_db_connection()
        conn.execute('INSERT INTO assignments (name, due_date, subject) VALUES (?, ?, ?)',
            (name, due_date, subject))
        conn.commit()
        conn.close()
        return redirect('/')

    conn = get_db_connection()
    assignments = conn.execute('SELECT * FROM assignments ORDER BY due_date').fetchall()
    conn.close()

    return render_template('index.html', assignments=assignments)
@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    conn=get_db_connection()
    conn.execute('DELETE FROM assignments WHERE id=?',(id,))
    conn.commit()
    conn.close()
    return redirect('/')
if __name__ == '__main__':
    app.run(debug=True)