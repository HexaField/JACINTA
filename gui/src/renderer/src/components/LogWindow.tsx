// src/components/LogWindow.tsx
import React from 'react';

interface LogWindowProps {
  logs: string[];
}

const LogWindow: React.FC<LogWindowProps> = ({ logs }) => {
  return (
    <div className="log-window" style={{ border: '1px solid #ccc', padding: '0.5rem', borderRadius: '4px', height: '100%', overflowY: 'auto' }}>
      <h2>Agent Logs</h2>
      <div className="logs">
        {logs.map((log, index) => (
          <div key={index} className="log-entry" style={{ padding: '0.25rem 0', borderBottom: '1px solid #eee' }}>
            {log}
          </div>
        ))}
      </div>
    </div>
  );
};

export default LogWindow;
