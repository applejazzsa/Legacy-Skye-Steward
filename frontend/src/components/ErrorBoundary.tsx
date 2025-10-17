import React from "react";

type Props = { children: React.ReactNode; fallback?: React.ReactNode };
type State = { hasError: boolean; error?: any };

export default class ErrorBoundary extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }
  static getDerivedStateFromError(error: any) {
    return { hasError: true, error };
  }
  componentDidCatch(error: any, info: any) {
    // You could log to a service here
    console.error("Component error:", error, info);
  }
  render() {
    if (this.state.hasError) {
      return (
        this.props.fallback ?? (
          <div className="card">
            <h2>Something went wrong</h2>
            <div className="badge" style={{ color: "#ef4444" }}>
              {String(this.state.error ?? "Unknown error")}
            </div>
          </div>
        )
      );
    }
    return this.props.children;
  }
}
