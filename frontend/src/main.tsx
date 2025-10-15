import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import "./index.css";

function Root() {
  return <App />;
}

const rootEl = document.getElementById("root");
if (!rootEl) {
  // Hard fail early so it's obvious if the root div is missing
  throw new Error("Root element #root not found in index.html");
}

ReactDOM.createRoot(rootEl).render(
  <React.StrictMode>
    <Root />
  </React.StrictMode>
);
