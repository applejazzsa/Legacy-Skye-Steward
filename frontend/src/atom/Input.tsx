// feat(ui): standard Input atom
import React from "react";

type InputProps = React.InputHTMLAttributes<HTMLInputElement> & {
  label?: string;
  hint?: string;
  id?: string;
};

export default function Input({ label, hint, id, ...rest }: InputProps) {
  const input = <input id={id} {...rest} />;
  if (!label) return input;
  return (
    <div className="field">
      <label htmlFor={id}>{label}</label>
      {input}
      {hint && <div className="help">{hint}</div>}
    </div>
  );
}

