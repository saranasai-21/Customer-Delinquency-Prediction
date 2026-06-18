// frontend/app/layout.tsx

import React from 'react';
import './globals.css';

export const metadata = {
  title: 'Enterprise Delinquency Risk Center',
  description: 'Clean Architecture Credit Risk Platform',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="flex h-screen overflow-hidden bg-slate-50 dark:bg-slate-950">
        {/* Sidebar */}
        <aside className="w-64 border-r border-slate-200 bg-white p-6 dark:border-slate-800 dark:bg-slate-900 flex flex-col justify-between">
          <div>
            <div className="mb-8 flex items-center space-x-2">
              <span className="text-xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                Aegis Risk
              </span>
              <span className="rounded bg-indigo-100 px-2 py-0.5 text-xs font-semibold text-indigo-800 dark:bg-indigo-950 dark:text-indigo-200">
                v2.0
              </span>
            </div>
            
            <nav className="space-y-1">
              <a href="/" className="flex items-center space-x-3 rounded-lg px-4 py-2.5 text-sm font-medium text-slate-700 hover:bg-slate-100 dark:text-slate-200 dark:hover:bg-slate-800">
                <span>📊</span> <span>Risk Dashboard</span>
              </a>
              <a href="/prediction" className="flex items-center space-x-3 rounded-lg px-4 py-2.5 text-sm font-medium text-slate-700 hover:bg-slate-100 dark:text-slate-200 dark:hover:bg-slate-800">
                <span>🔮</span> <span>Run Inference</span>
              </a>
              <a href="/assistant" className="flex items-center space-x-3 rounded-lg px-4 py-2.5 text-sm font-medium text-slate-700 hover:bg-slate-100 dark:text-slate-200 dark:hover:bg-slate-800">
                <span>💬</span> <span>AI Risk Agent</span>
              </a>
              <a href="/monitoring" className="flex items-center space-x-3 rounded-lg px-4 py-2.5 text-sm font-medium text-slate-700 hover:bg-slate-100 dark:text-slate-200 dark:hover:bg-slate-800">
                <span>🛡️</span> <span>Model Drift</span>
              </a>
            </nav>
          </div>

          <div className="border-t border-slate-200 pt-4 dark:border-slate-800">
            <p className="text-xs text-slate-400 dark:text-slate-500 text-center">
              Fintech Production System
            </p>
          </div>
        </aside>

        {/* Content Frame */}
        <main className="flex-1 flex flex-col overflow-hidden">
          {/* Header */}
          <header className="h-16 border-b border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-900 flex items-center justify-between px-8">
            <h1 className="text-lg font-semibold text-slate-800 dark:text-white">Credit Risk Control Panel</h1>
            <div className="flex items-center space-x-4">
              <span className="h-2.5 w-2.5 rounded-full bg-emerald-500 animate-pulse"></span>
              <span className="text-sm font-medium text-slate-500 dark:text-slate-400">Core API Online</span>
            </div>
          </header>
          
          <div className="flex-1 overflow-y-auto p-8">
            {children}
          </div>
        </main>
      </body>
    </html>
  );
}
