// src/ErrorBoundary.tsx
import { Component, ReactNode } from "react";

type Props = { children: ReactNode };
type State = { error: Error | null };

export default class ErrorBoundary extends Component<Props, State> {
  state: State = { error: null };

  static getDerivedStateFromError(error: Error) {
    return { error };
  }

  componentDidCatch(error: Error, info: any) {
    // still log to console so you can inspect stack traces
    console.error("ErrorBoundary caught:", error, info);
  }

  render() {
    if (this.state.error) {
      return (
        <div
          style={{
            background: "#1f2937",
            color: "#fff",
            border: "2px solid #ef4444",
            borderRadius: 12,
            padding: 16,
            margin: 24,
            fontFamily: "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas",
          }}
        >
          <h2 style={{ marginTop: 0, color: "#fca5a5" }}>UI crashed</h2>
          <pre style={{ whiteSpace: "pre-wrap" }}>
{String(this.state.error?.message || this.state.error)}
          </pre>
          <p style={{ opacity: 0.8 }}>
            Check the browser console for a stack trace.
          </p>
        </div>
      );
    }
    return this.props.children;
  }
}
