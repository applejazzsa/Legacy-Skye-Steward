import type { Config } from "tailwindcss";

export default {
  darkMode: "class",
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
    "./components/**/*.{js,ts,jsx,tsx}",
    "./layouts/**/*.{js,ts,jsx,tsx}",
    "./pages/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        steward: {
          600: "#2563eb", // primary accent (Steward blue)
          700: "#1e40af",
        },
        legacy: {
          400: "#f0d48a", // champagne gold accent
          700: "#0f172a", // charcoal
        },
      },
      borderRadius: {
        xl: "0.9rem",
        "2xl": "1.25rem",
      },
      boxShadow: {
        card: "0 6px 24px -8px rgba(15,23,42,0.12)",
      },
    },
  },
  plugins: [],
} satisfies Config;
