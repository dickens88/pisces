/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        "primary": "#2563EB",
        "primary-hover": "#1d4ed8",
        "background-light": "#f3f4f6",
        "background-dark": "#0f172a",
        "surface-dark": "#1e293b",
        "surface-hover-dark": "#334155",
        "panel-dark": "#161d26",
        "panel-light": "#ffffff",
        "border-dark": "#334155",
        "border-light": "#e5e7eb",
        "text-light": "#9ca3af",
        "text-dark": "#6b7280",
        "text-primary-light": "#111827",
        "text-primary-dark": "#f9fafb",
        "text-secondary-dark": "#94a3b8",
      },
      fontFamily: {
        "display": ["Inter", "sans-serif"]
      },
      borderRadius: {
        "DEFAULT": "0.25rem",
        "lg": "0.5rem",
        "xl": "0.75rem",
        "full": "9999px"
      },
    },
  },
  plugins: [],
}

