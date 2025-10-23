// frontend/src/util/currency.ts

/**
 * Format a number in South African Rand (ZAR).
 * Examples:
 *  formatZAR(1234.5) => "R 1,234.50"
 */
export function formatZAR(value: number | null | undefined): string {
  const n = typeof value === "number" && isFinite(value) ? value : 0;
  return new Intl.NumberFormat("en-ZA", {
    style: "currency",
    currency: "ZAR",
    maximumFractionDigits: 2,
    minimumFractionDigits: 0,
  }).format(n);
}

/**
 * Compact ZAR (for small chips etc.)
 *  formatZARCompact(123400) => "R 123K"
 */
export function formatZARCompact(value: number | null | undefined): string {
  const n = typeof value === "number" && isFinite(value) ? value : 0;
  const parts = new Intl.NumberFormat("en-ZA", {
    notation: "compact",
    maximumFractionDigits: 1,
  }).format(n);
  // Prepend currency symbol manually for compact notation
  return `R ${parts}`;
}
