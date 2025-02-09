// src/App.tsx
import React, { useState, useEffect } from 'react';
import TaskList from './components/TaskList';
import ChatWindow from './components/ChatWindow';
import LogWindow from './components/LogWindow';
import { Task } from '../../types';

const App: React.FC = () => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [logs, setLogs] = useState<string[]>([]);

  useEffect(() => {
    // For demonstration, we initialize with some dummy data.
    setTasks([
      { id: '1', title: 'Initial Setup', status: 'completed' },
      { id: '2', title: 'Develop Feature X', status: 'in-progress' },
      { id: '3', title: 'Test Module Y', status: 'not-started' }
    ]);

    setLogs([
      'Agent started.',
      'Completed task "Initial Setup".',
      'Task "Develop Feature X" is now in progress.'
    ]);

    // Later, you can listen for updates from your backend agent.
    // For example, using Electron’s IPC:
    // window.electron.ipcRenderer.on('task-updated', (event, updatedTasks) => setTasks(updatedTasks));
    // window.electron.ipcRenderer.on('new-log', (event, newLog) => setLogs(prev => [...prev, newLog]));
  }, []);

  return (
    <div className="app-container" style={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
      <header style={{ padding: '1rem', borderBottom: '1px solid #ccc' }}>
        <h1>AI Task Agent Dashboard</h1>
      </header>
      <div className="content" style={{ display: 'flex', flex: 1 }}>
        {/* Sidebar for task list */}
        <aside style={{ flex: 1, borderRight: '1px solid #ccc', padding: '1rem', overflowY: 'auto' }}>
          <TaskList tasks={tasks} />
        </aside>

        {/* Main area for chat and logs */}
        <main style={{ flex: 2, padding: '1rem', display: 'flex', flexDirection: 'column' }}>
          <ChatWindow />
          <div style={{ flex: 1, marginTop: '1rem' }}>
            <LogWindow logs={logs} />
          </div>
        </main>
      </div>
    </div>
  );
};

export default App;
