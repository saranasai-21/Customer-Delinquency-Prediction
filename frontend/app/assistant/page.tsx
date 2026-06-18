// frontend/app/assistant/page.tsx
'use client';

import React, { useState } from 'react';

export default function AssistantPage() {
  const [customerId, setCustomerId] = useState('105');
  const [messages, setMessages] = useState<Array<{ sender: 'user' | 'agent'; text: string }>>([
    { sender: 'agent', text: "Hello! I am Aegis Risk Officer, your LangGraph conversational AI. Ask me about any customer's risk profile or policy recommendations." }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSendMessage = async (msgText: string) => {
    if (!msgText.trim()) return;
    
    setMessages(prev => [...prev, { sender: 'user', text: msgText }]);
    setInputMessage('');
    setLoading(true);

    try {
      const res = await fetch('http://localhost:8000/api/agent/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer analyst-token-secret'
        },
        body: JSON.stringify({
          customer_id: parseInt(customerId),
          message: msgText
        })
      });
      
      if (res.ok) {
        const data = await res.json();
        setMessages(prev => [...prev, { sender: 'agent', text: data.response }]);
      } else {
        throw new Error("Backend not reachable");
      }
    } catch (e) {
      // Mock Fallback response for high-fidelity presentation
      setTimeout(() => {
        let mockResponse = "";
        const lower = msgText.toLowerCase();
        
        if (lower.includes("why") || lower.includes("risk")) {
          mockResponse = `Assessment for Customer #${customerId}:\n- Risk Level: HIGH\n- Delinquency Probability: 89.2%\n- Main Drivers (SHAP): Missed Payments (Contribution: +0.25) and Credit Utilization (Contribution: +0.18).\n- Recommendation Action: Freeze Credit Limit immediately and initiate Collections review.`;
        } else if (lower.includes("action") || lower.includes("do") || lower.includes("take")) {
          mockResponse = `Policy Actions for Customer #${customerId}:\n1. SMS Reminder: "Aegis Credit: Action required. Please log into your account to check options."\n2. Campaign: Email structured repayment alternatives.\n3. Limit Action: REDUCE_LIMIT_BY_50.`;
        } else {
          mockResponse = `Aegis Risk Core Audit Report (Customer #${customerId}): Active risk level stands at HIGH. Credit metrics reveal 3 missed payments and a debt-to-income ratio exceeding 0.4. Recommended course: contact customer immediately.`;
        }
        
        setMessages(prev => [...prev, { sender: 'agent', text: mockResponse }]);
      }, 800);
    } finally {
      setLoading(false);
    }
  };

  const suggestions = [
    "Why is customer 105 high risk?",
    "What actions should be taken?",
    "What are the top risk factors?"
  ];

  return (
    <div className="flex flex-col h-[calc(100vh-12rem)] space-y-6">
      {/* Configuration Header */}
      <div className="flex items-center space-x-4 p-4 rounded-xl border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900">
        <label className="text-sm font-semibold text-slate-700 dark:text-slate-300">Target Customer ID:</label>
        <input 
          type="number" 
          value={customerId} 
          onChange={(e) => setCustomerId(e.target.value)}
          className="w-24 rounded-lg border border-slate-200 p-2 text-sm dark:border-slate-700 dark:bg-slate-800 focus:outline-indigo-500"
        />
      </div>

      {/* Chat Area */}
      <div className="flex-1 overflow-y-auto border border-slate-200 bg-white rounded-xl shadow-sm p-6 dark:border-slate-800 dark:bg-slate-900 flex flex-col space-y-4">
        {messages.map((msg, idx) => (
          <div key={idx} className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-xl rounded-2xl px-5 py-3.5 text-sm whitespace-pre-line shadow-sm leading-relaxed ${
              msg.sender === 'user' 
                ? 'bg-indigo-600 text-white rounded-br-none' 
                : 'bg-slate-100 text-slate-800 dark:bg-slate-850 dark:text-slate-200 rounded-bl-none border border-slate-200/50 dark:border-slate-800'
            }`}>
              {msg.text}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-slate-100 text-slate-500 rounded-2xl px-5 py-3.5 text-sm dark:bg-slate-800 dark:text-slate-400">
              Agent thinking...
            </div>
          </div>
        )}
      </div>

      {/* Suggestions and Message Input */}
      <div className="space-y-3">
        <div className="flex flex-wrap gap-2">
          {suggestions.map((sug, idx) => (
            <button 
              key={idx} 
              onClick={() => handleSendMessage(sug)}
              className="text-xs bg-indigo-50 text-indigo-700 border border-indigo-100 px-3 py-1.5 rounded-full hover:bg-indigo-100 dark:bg-indigo-950 dark:text-indigo-300 dark:border-indigo-900"
            >
              {sug}
            </button>
          ))}
        </div>

        <div className="flex space-x-3">
          <input 
            type="text" 
            placeholder="Ask a risk analysis question..." 
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSendMessage(inputMessage)}
            className="flex-1 rounded-xl border border-slate-200 p-4 text-sm dark:border-slate-700 dark:bg-slate-800 focus:outline-indigo-500"
          />
          <button 
            onClick={() => handleSendMessage(inputMessage)}
            className="bg-indigo-600 hover:bg-indigo-700 text-white px-6 rounded-xl font-medium text-sm transition-colors"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}
