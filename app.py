from flask import Flask, render_template, request, redirect
from datetime import datetime
import sqlite3
import os

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('assignments.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    try:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS assignments (
                id INTEGER PRIMARY KEY,
                student_name TEXT,
                name TEXT,
                due_date TEXT,
                subject TEXT
            )
        ''')
        conn.commit()
    except Exception as e:
        print(f"DB Error: {e}")
    finally:
        conn.close()

init_db()

@app.route('/', methods=['GET', 'POST'])
def home():
    student_name = request.args.get('student', 'Student')

    if request.method == 'POST':
        name = request.form['assignment_name']
        due_date = request.form['due_date']
        subject = request.form['subject']
        student = request.form.get('student_name', student_name)

        conn = get_db_connection()
        conn.execute(
            'INSERT INTO assignments(student_name, name, due_date, subject) VALUES (?, ?, ?, ?)',
            (student, name, due_date, subject)
        )
        conn.commit()
        conn.close()

        return redirect(f'/?student={student}')

    conn = get_db_connection()
    assignments = conn.execute(
        'SELECT * FROM assignments WHERE student_name=? ORDER BY due_date',
        (student_name,)
    ).fetchall()
    conn.close()

    return render_template(
        'index.html',
        assignments=assignments,
        now=datetime.now(),
        student_name=student_name
    )

@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    student_name = request.args.get('student', 'Student')

    conn = get_db_connection()
    conn.execute('DELETE FROM assignments WHERE id=?', (id,))
    conn.commit()
    conn.close()

    return redirect(f'/?student={student_name}')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
