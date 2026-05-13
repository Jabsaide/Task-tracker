from flask import Flask, jsonify, request, g
from flask_cors import CORS
import sqlite3 # <-- 1. Import the database engine

app = Flask(__name__)
CORS(app)

DATABASE = 'tasks.db' # This is the file that will be created on your hard drive

# --- DATABASE PROTOCOLS ---

# Protocol 1: Open the connection to the file
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row # This makes the data behave like a dictionary
    return db

# Protocol 2: The Blueprint (Create the table if it doesn't exist)
def init_db():
    with app.app_context():
        db = get_db()
        # Create a table with 3 columns: id, title, and completed status
        db.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                completed BOOLEAN NOT NULL CHECK (completed IN (0, 1))
            )
        ''')
        db.commit()

# --- API ROUTES ---

@app.route('/tasks', methods=['GET', 'POST'])
def handle_tasks():
    db = get_db()
    
    if request.method == 'POST':
        # WRITE PROTOCOL: Insert a new row into the database
        new_task_data = request.get_json()
        cursor = db.execute(
            'INSERT INTO tasks (title, completed) VALUES (?, ?)',
            (new_task_data['title'], False)
        )
        db.commit()
        
        # Send the newly created task back to the storefront
        return jsonify({
            "id": cursor.lastrowid,
            "title": new_task_data['title'],
            "completed": False
        }), 201
    
    # READ PROTOCOL (GET Request): Fetch all rows from the database
    cursor = db.execute('SELECT * FROM tasks')
    tasks = cursor.fetchall()
    
    # Convert the database rows into a clean JSON list
    task_list = [{"id": row["id"], "title": row["title"], "completed": bool(row["completed"])} for row in tasks]
    
    return jsonify(task_list)

# Safely close the database connection when the request is done
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# --- NEW ROUTE: DELETE A SPECIFIC TASK ---
# Notice how we add <int:task_id> to the route. This catches the number at the end of the URL.
@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    db = get_db()
    
    # Execute the SQL command to delete the row where the ID matches
    db.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    db.commit()
    
    # Send a quick message back saying it was successful
    return jsonify({"message": "Task deleted successfully"}), 200

# --- NEW ROUTE: UPDATE A TASK ---
@app.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    db = get_db()
    
    # 1. Read the package sent by the storefront
    data = request.get_json()
    
    # 2. SQLite stores True/False as 1 or 0. We convert it here.
    new_status = 1 if data['completed'] else 0
    
    # 3. Update that specific row in the database spreadsheet
    db.execute('UPDATE tasks SET completed = ? WHERE id = ?', (new_status, task_id))
    db.commit()
    
    return jsonify({"message": "Task updated successfully"}), 200

# Protocol 2: The Blueprint (Create the table if it doesn't exist)
def init_db():
    with app.app_context():
        db = get_db()
        db.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                completed BOOLEAN NOT NULL CHECK (completed IN (0, 1))
            )
        ''')
        db.commit()

init_db() # <--- ADD THIS LINE HERE! Now Gunicorn will trigger it.

# --- API ROUTES ---
# (Keep all your routes the same down here)

if __name__ == '__main__':
    # Remove init_db() from down here, leave only app.run
    app.run(debug=True)