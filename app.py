from flask import Flask, render_template, request, redirect
from datetime import datetime
import sqlite3

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('assignments.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    try:
        conn.execute('''CREATE TABLE IF NOT EXISTS assignments 
                       (id INTEGER PRIMARY KEY, student_name TEXT, name TEXT, due_date TEXT, subject TEXT, completed INTEGER DEFAULT 0)''')
        conn.commit()
    except Exception as e:
        print(f"DB Error: {e}")
    finally:
        conn.close()

init_db()

@app.route('/', methods=['GET', 'POST'])
def landing():
    if request.method == 'POST':
        student_name = request.form['student_name']
        return redirect(f'/tracker?student={student_name}')
    return render_template('landing.html')

@app.route('/tracker', methods=['GET', 'POST'])
def tracker():
    student_name = request.args.get('student', '')
    if not student_name:
        return redirect('/')
    
    if request.method == 'POST':
        name = request.form['assignment_name']
        due_date = request.form['due_date']
        subject = request.form['subject']
        
        conn = get_db_connection()
        conn.execute('INSERT INTO assignments (student_name, name, due_date, subject, completed) VALUES (?, ?, ?, ?, 0)', 
                     (student_name, name, due_date, subject))
        conn.commit()
        conn.close()
        return redirect(f'/tracker?student={student_name}')
    
    conn = get_db_connection()
    assignments = conn.execute('SELECT * FROM assignments WHERE student_name = ? ORDER BY due_date', 
                               (student_name,)).fetchall()
    conn.close()
    
    return render_template('index.html', assignments=assignments, now=datetime.now(), student_name=student_name)

@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    student_name = request.args.get('student', '')
    conn = get_db_connection()
    conn.execute('DELETE FROM assignments WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(f'/tracker?student={student_name}')

@app.route('/toggle/<int:id>', methods=['POST'])
def toggle(id):
    student_name = request.args.get('student', '')
    conn = get_db_connection()
    assignment = conn.execute('SELECT completed FROM assignments WHERE id = ?', (id,)).fetchone()
    new_status = 1 - assignment['completed']
    conn.execute('UPDATE assignments SET completed = ? WHERE id = ?', (new_status, id))
    conn.commit()
    conn.close()
    return redirect(f'/tracker?student={student_name}')

if __name__ == '__main__':
    app.run(debug=True)