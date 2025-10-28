// feat(ui): standard Button atom with a11y and states
import React from "react";

type ButtonProps = React.ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "primary" | "default" | "ghost";
  busy?: boolean;
};

export default function Button({ variant = "default", busy = false, disabled, children, ...rest }: ButtonProps) {
  const cls = [
    variant === "primary" ? "primary" : "",
  ].filter(Boolean).join(" ");
  return (
    <button
      className={cls}
      aria-busy={busy || undefined}
      aria-disabled={disabled || busy || undefined}
      disabled={disabled || busy}
      {...rest}
    >
      {busy ? "Working..." : children}
    </button>
  );
}

