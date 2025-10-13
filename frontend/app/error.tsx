"use client";

import { useEffect } from "react";

export default function Error({ error, reset }: { error: Error; reset: () => void }) {
  useEffect(() => {
    console.error("Dashboard error:", error);
  }, [error]);

  return (
    <main className="flex min-h-screen items-center justify-center">
      <div className="max-w-md rounded-lg bg-white p-6 text-center shadow">
        <h1 className="text-lg font-semibold text-red-600">Something went wrong</h1>
        <p className="mt-2 text-sm text-slate-600">
          We couldn&apos;t load the latest analytics. Please try again.
        </p>
        <button
          className="mt-4 rounded-md bg-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow hover:bg-indigo-500"
          onClick={() => reset()}
        >
          Retry
        </button>
      </div>
    </main>
  );
}
