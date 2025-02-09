// src/components/ChatWindow.tsx
import React, { useState } from 'react';

interface Message {
  sender: 'user' | 'agent';
  content: string;
}

const ChatWindow: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');

  const handleSend = async () => {
    if (!input.trim()) return;
    
    // Add the user message
    const userMessage: Message = { sender: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);

    window.electron.ipcRenderer.send('new-chat-message', input);

    // Clear the input field
    setInput('');
  };

  return (
    <div className="chat-window" style={{ border: '1px solid #ccc', padding: '0.5rem', borderRadius: '4px', marginBottom: '1rem' }}>
      <div className="messages" style={{ height: '200px', overflowY: 'auto', marginBottom: '0.5rem' }}>
        {messages.map((msg, index) => (
          <div key={index} className={`message ${msg.sender}`} style={{ margin: '0.25rem 0' }}>
            <strong>{msg.sender === 'user' ? 'You' : 'Agent'}:</strong> {msg.content}
          </div>
        ))}
      </div>
      <div className="input" style={{ display: 'flex' }}>
        <input
          type="text"
          value={input}
          onChange={e => setInput(e.target.value)}
          placeholder="Ask a question or create a task..."
          style={{ flex: 1, padding: '0.5rem' }}
        />
        <button onClick={handleSend} style={{ padding: '0.5rem 1rem' }}>Send</button>
      </div>
    </div>
  );
};

export default ChatWindow;
