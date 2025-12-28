import React, { useState } from 'react';

interface Message { id: string; role: 'user' | 'assistant' | 'error'; content: string; }

export const ChatPanel: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  function addMessage(role: Message['role'], content: string) {
    setMessages(m => [...m, { id: crypto.randomUUID(), role, content }]);
  }

  async function send() {
    const text = input.trim();
    if (!text) return;
    setInput('');
    addMessage('user', text);
    setIsLoading(true);
    // Placeholder fetch to backend (later replaced with Tauri invoke)
    try {
      // Fake small delay
      await new Promise(r => setTimeout(r, 200));
      addMessage('assistant', 'Echo: ' + text);
    } catch (e: any) {
      addMessage('error', e?.message || 'Error');
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="flex flex-col flex-1 bg-surface border-l border-border">
      <div className="flex-1 overflow-auto p-3 space-y-3 text-sm">
        {messages.map(msg => (
          <div key={msg.id} className={`rounded px-3 py-2 whitespace-pre-wrap border border-border text-[13px] ${msg.role==='user' ? 'bg-surfaceAlt' : msg.role==='assistant' ? 'bg-surface' : 'bg-red-900/40 border-red-500'}`}>{msg.role}: {msg.content}</div>
        ))}
        {isLoading && <div className="text-xs text-slate-400 animate-pulse">Thinking...</div>}
      </div>
      <form onSubmit={e => { e.preventDefault(); send(); }} className="flex gap-2 p-2 border-t border-border">
        <input value={input} onChange={e => setInput(e.target.value)} placeholder="Ask or chat..." className="flex-1 px-2 py-1 rounded bg-surfaceAlt border border-border text-sm" />
        <button type="submit" className="px-3 py-1 bg-blue-600 hover:bg-blue-500 rounded text-sm">Send</button>
      </form>
    </div>
  );
};
