import type { Config } from "tailwindcss";

export default {
  darkMode: ["class"],
  content: [
    "./pages/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./app/**/*.{ts,tsx}",
    "./src/**/*.{ts,tsx}",
  ],
  prefix: "",
  theme: {
    extend: {
      colors: {
        'cyber-primary': '#1a237e',
        'cyber-secondary': '#00ff00',
        'cyber-accent': '#0288d1',
        'cyber-dark': '#121212',
        'cyber-light': '#2d2d2d',
        border: "hsl(var(--border))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
      },
      backgroundImage: {
        'cyber-gradient': 'linear-gradient(to right, #121212, #1a237e)',
      },
      fontFamily: {
        'cyber': ['Inter', 'sans-serif'],
      },
      borderColor: {
        DEFAULT: "hsl(var(--border))",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
} satisfies Config;