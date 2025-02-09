// src/components/TaskList.tsx
import React from 'react';
import { Task } from '../../../types';

interface TaskListProps {
  tasks: Task[];
}

const TaskList: React.FC<TaskListProps> = ({ tasks }) => {
  const completedTasks = tasks.filter(task => task.status === 'completed');
  const inProgressTasks = tasks.filter(task => task.status === 'in-progress');
  const notStartedTasks = tasks.filter(task => task.status === 'not-started');

  return (
    <div className="task-list" style={{ padding: '0 1rem' }}>
      <h2>Not Yet Started</h2>
      <ul>
        {notStartedTasks.map(task => (
          <li key={task.id}>{task.title}</li>
        ))}
      </ul>

      <h2>In Progress</h2>
      <ul>
        {inProgressTasks.map(task => (
          <li key={task.id}>{task.title}</li>
        ))}
      </ul>

      <h2>Completed</h2>
      <ul>
        {completedTasks.map(task => (
          <li key={task.id}>{task.title}</li>
        ))}
      </ul>
    </div>
  );
};

export default TaskList;
