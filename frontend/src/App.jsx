import { useState, useEffect } from 'react'

function App() {
  const [tasks, setTasks] = useState([])
  const [newTaskTitle, setNewTaskTitle] = useState("")

  // READ
  useEffect(() => {
    fetch('https://my-task-backend-ytwd.onrender.com/tasks')
      .then(response => response.json())
      .then(data => setTasks(data))
  }, [])

  // CREATE
  const addTask = (e) => {
    e.preventDefault()
    if (!newTaskTitle) return;

    fetch('https://my-task-backend-ytwd.onrender.com/tasks', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title: newTaskTitle })
    })
    .then(response => response.json())
    .then(newTask => {
      setTasks([...tasks, newTask])
      setNewTaskTitle("")
    })
  }

  // DELETE
  const deleteTask = (id) => {
    fetch(`https://my-task-backend-ytwd.onrender.com/tasks/${id}`, { method: 'DELETE' })
    .then(() => setTasks(tasks.filter(task => task.id !== id)))
  }

  // UPDATE: The new toggle function
  const toggleComplete = (task) => {
    // 1. Figure out what the opposite of the current status is
    const updatedStatus = !task.completed

    // 2. Send the PUT request with the new status
    fetch(`https://my-task-backend-ytwd.onrender.com/tasks/${task.id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ completed: updatedStatus })
    })
    .then(() => {
      // 3. Update the storefront clipboard
      // This tells React: "Find the task with this ID, and flip its status. Leave the rest alone."
      setTasks(tasks.map(t => 
        t.id === task.id ? { ...t, completed: updatedStatus } : t
      ))
    })
  }

  return (
    <div style={{ padding: '20px', fontFamily: 'sans-serif' }}>
      <h1>My Task Tracker</h1>
      
      <form onSubmit={addTask} style={{ marginBottom: '20px' }}>
        <input 
          type="text" 
          value={newTaskTitle}
          onChange={(e) => setNewTaskTitle(e.target.value)}
          placeholder="What needs to be done?" 
          style={{ padding: '5px', marginRight: '5px' }}
        />
        <button type="submit" style={{ padding: '5px 10px' }}>Add Task</button>
      </form>

      <ul>
        {tasks.map(task => (
          <li key={task.id} style={{ 
            marginBottom: '10px', 
            // Optional: Put a line through the text if it is completed
            textDecoration: task.completed ? 'line-through' : 'none' 
          }}>
            {task.title} - {task.completed ? "✅ Done" : "⏳ Pending"}
            
            {/* The new Complete/Undo Button */}
            <button 
              onClick={() => toggleComplete(task)} 
              style={{ marginLeft: '15px', cursor: 'pointer' }}
            >
              {task.completed ? "Undo" : "Complete"}
            </button>

            {/* The Delete Button */}
            <button 
              onClick={() => deleteTask(task.id)} 
              style={{ marginLeft: '5px', color: 'red', cursor: 'pointer' }}
            >
              Delete
            </button>
          </li>
        ))}
      </ul>
    </div>
  )
}

export default App