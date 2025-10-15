import React from "react";

type State = { hasError: boolean; error?: any };

export default class ErrorBoundary extends React.Component<React.PropsWithChildren, State> {
  constructor(props: React.PropsWithChildren) {
    super(props);
    this.state = { hasError: false };
  }
  static getDerivedStateFromError(error: any): State {
    return { hasError: true, error };
  }
  componentDidCatch(error: any, info: any) {
    console.error("ErrorBoundary caught:", error, info);
  }
  render() {
    if (this.state.hasError) {
      return (
        <div className="container">
          <div className="card">
            <h2>Something went wrong</h2>
            <pre style={{whiteSpace:"pre-wrap"}}>{String(this.state.error)}</pre>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}
