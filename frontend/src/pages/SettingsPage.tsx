import React from "react";

export default function SettingsPage() {
  return (
    <section>
      <h2 className="text-xl font-semibold mb-2">Settings</h2>
      <div className="grid gap-3 max-w-xl">
        <div className="rounded-xl border border-slate-200 p-3 dark:border-slate-800">
          <div className="text-sm font-medium">Theme</div>
          <div className="text-sm text-slate-500">Use the toggle in the header to switch Light/Dark.</div>
        </div>
        <div className="rounded-xl border border-slate-200 p-3 dark:border-slate-800">
          <div className="text-sm font-medium">Backend URL</div>
          <div className="text-sm text-slate-500">Configure with <code>VITE_API_URL</code> in <code>frontend/.env</code>.</div>
        </div>
      </div>
    </section>
  );
}
