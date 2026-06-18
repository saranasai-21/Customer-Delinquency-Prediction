// frontend/app/page.tsx
'use client';

import React from 'react';

export default function DashboardPage() {
  // Mock data representing database states for high-fidelity presentation
  const stats = [
    { name: "Portfolio Exposure", value: "$4.8M", change: "+12.4%", trend: "up" },
    { name: "Average Credit Score", value: "712", change: "+4", trend: "up" },
    { name: "Flagged High Risk", value: "8.4%", change: "-0.5%", trend: "down" },
    { name: "Inference Latency", value: "1.25 ms", change: "Optimal", trend: "neutral" },
  ];

  const recentAudits = [
    { id: 105, score: 580, utilization: "84%", missed: 3, risk: "HIGH", probability: "0.89" },
    { id: 109, score: 640, utilization: "62%", missed: 1, risk: "MEDIUM", probability: "0.48" },
    { id: 112, score: 780, utilization: "12%", missed: 0, risk: "LOW", probability: "0.08" },
    { id: 115, score: 710, utilization: "38%", missed: 0, risk: "LOW", probability: "0.12" },
  ];

  return (
    <div className="space-y-8">
      {/* Overview Cards */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat, idx) => (
          <div key={idx} className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
            <p className="text-sm font-medium text-slate-500 dark:text-slate-400">{stat.name}</p>
            <div className="mt-2 flex items-baseline justify-between">
              <span className="text-3xl font-semibold tracking-tight text-slate-800 dark:text-white">{stat.value}</span>
              <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${
                stat.trend === "up" ? "bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-200" :
                stat.trend === "down" ? "bg-rose-100 text-rose-800 dark:bg-rose-950 dark:text-rose-200" :
                "bg-slate-100 text-slate-800 dark:bg-slate-950 dark:text-slate-200"
              }`}>
                {stat.change}
              </span>
            </div>
          </div>
        ))}
      </div>

      {/* Visual Analytics Grid */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="col-span-2 rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <h2 className="text-base font-semibold text-slate-800 dark:text-white mb-4">Delinquency Risk Breakdown</h2>
          
          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className="font-medium dark:text-slate-300">Healthy (Low Risk)</span>
                <span className="text-slate-500">76.4%</span>
              </div>
              <div className="h-3 w-full bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                <div className="h-full bg-emerald-500 rounded-full" style={{ width: '76.4%' }}></div>
              </div>
            </div>

            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className="font-medium dark:text-slate-300">Attention (Medium Risk)</span>
                <span className="text-slate-500">15.2%</span>
              </div>
              <div className="h-3 w-full bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                <div className="h-full bg-amber-500 rounded-full" style={{ width: '15.2%' }}></div>
              </div>
            </div>

            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className="font-medium dark:text-slate-300">Critical (High Risk)</span>
                <span className="text-slate-500">8.4%</span>
              </div>
              <div className="h-3 w-full bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                <div className="h-full bg-rose-500 rounded-full" style={{ width: '8.4%' }}></div>
              </div>
            </div>
          </div>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <h2 className="text-base font-semibold text-slate-800 dark:text-white mb-4">Feature Store Ingestion</h2>
          <ul className="space-y-3">
            <li className="flex items-center justify-between text-sm">
              <span className="text-slate-600 dark:text-slate-400">Repayment_Score</span>
              <span className="font-semibold text-emerald-600 dark:text-emerald-400">Online</span>
            </li>
            <li className="flex items-center justify-between text-sm">
              <span className="text-slate-600 dark:text-slate-400">Payment_Stress</span>
              <span className="font-semibold text-emerald-600 dark:text-emerald-400">Online</span>
            </li>
            <li className="flex items-center justify-between text-sm">
              <span className="text-slate-600 dark:text-slate-400">Utilization_DTI</span>
              <span className="font-semibold text-emerald-600 dark:text-emerald-400">Online</span>
            </li>
            <li className="flex items-center justify-between text-sm">
              <span className="text-slate-600 dark:text-slate-400">Repayment_Trend</span>
              <span className="font-semibold text-amber-500">Recalculating...</span>
            </li>
          </ul>
        </div>
      </div>

      {/* Auditing Panel */}
      <div className="rounded-xl border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900 overflow-hidden">
        <div className="p-6 border-b border-slate-200 dark:border-slate-800">
          <h2 className="text-base font-semibold text-slate-800 dark:text-white">Recent Decisions & Inference Auditing</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-sm">
            <thead>
              <tr className="bg-slate-50 dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700 text-slate-500 font-medium">
                <th className="p-4">Customer ID</th>
                <th className="p-4">Credit Score</th>
                <th className="p-4">Utilization</th>
                <th className="p-4">Missed Payments</th>
                <th className="p-4">Risk Class</th>
                <th className="p-4">Score Probability</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200 dark:divide-slate-800 text-slate-700 dark:text-slate-300">
              {recentAudits.map((audit) => (
                <tr key={audit.id} className="hover:bg-slate-50 dark:hover:bg-slate-800">
                  <td className="p-4 font-semibold text-indigo-600 dark:text-indigo-400">#{audit.id}</td>
                  <td className="p-4">{audit.score}</td>
                  <td className="p-4">{audit.utilization}</td>
                  <td className="p-4">{audit.missed}</td>
                  <td className="p-4">
                    <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold ${
                      audit.risk === "HIGH" ? "bg-rose-100 text-rose-800 dark:bg-rose-950 dark:text-rose-200" :
                      audit.risk === "MEDIUM" ? "bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-200" :
                      "bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-200"
                    }`}>
                      {audit.risk}
                    </span>
                  </td>
                  <td className="p-4 font-mono">{audit.probability}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
