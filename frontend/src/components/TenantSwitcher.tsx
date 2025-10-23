// src/components/TenantSwitcher.tsx
import { useEffect, useState } from "react";

type Props = {
  value?: string;
  onChange?: (tenant: string) => void;
  tenants?: string[];
};

const DEFAULTS = ["legacy", "oceanview"];

export default function TenantSwitcher({
  value,
  onChange,
  tenants = DEFAULTS,
}: Props) {
  const [tenant, setTenant] = useState<string>(value || "legacy");

  useEffect(() => {
    const stored = localStorage.getItem("tenant");
    if (!value && stored && tenants.includes(stored)) {
      setTenant(stored);
      onChange?.(stored);
    }
  }, [value, onChange, tenants]);

  useEffect(() => {
    localStorage.setItem("tenant", tenant);
  }, [tenant]);

  return (
    <div className="inline-flex items-center gap-2">
      <label className="text-sm font-medium">Tenant</label>
      <select
        className="border rounded px-2 py-1 text-sm"
        value={tenant}
        onChange={(e) => {
          const t = e.target.value;
          setTenant(t);
          onChange?.(t);
        }}
      >
        {tenants.map((t) => (
          <option key={t} value={t}>
            {t}
          </option>
        ))}
      </select>
    </div>
  );
}
