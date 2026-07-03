/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        canvas: "#0A1128",
        "canvas-raised": "#0E1836",
        surface: "#131F42",
        "surface-hi": "#1A2955",
        border: {
          DEFAULT: "rgba(139, 158, 219, 0.14)",
          strong: "rgba(139, 158, 219, 0.28)",
        },
        ink: {
          DEFAULT: "#EDF1FA",
          muted: "#9FAAC9",
          faint: "#6B7699",
        },
        brand: {
          DEFAULT: "#5B7FDE",
          strong: "#4C6FE0",
          soft: "rgba(91, 127, 222, 0.14)",
        },
        risk: {
          low: "#3FC7B0",
          moderate: "#E8C547",
          high: "#E8934A",
          severe: "#E0602F",
          extreme: "#C81E3A",
        },
        green: {
          DEFAULT: "#4FAE7C",
          strong: "#2F9165",
          soft: "rgba(79, 174, 124, 0.14)",
        },
      },
      fontFamily: {
        display: ["'Space Grotesk'", "system-ui", "sans-serif"],
        body: ["'IBM Plex Sans'", "system-ui", "sans-serif"],
        mono: ["'IBM Plex Mono'", "ui-monospace", "monospace"],
      },
      boxShadow: {
        glass: "0 1px 0 0 rgba(255,255,255,0.04) inset, 0 20px 60px -20px rgba(0,0,0,0.55)",
        "glow-brand": "0 0 0 1px rgba(91,127,222,0.3), 0 0 24px rgba(91,127,222,0.18)",
      },
      backgroundImage: {
        "thermal-gradient": "linear-gradient(90deg, #3FC7B0 0%, #E8C547 35%, #E8934A 60%, #E0602F 80%, #C81E3A 100%)",
        "grid-lines":
          "linear-gradient(rgba(139,158,219,0.06) 1px, transparent 1px), linear-gradient(90deg, rgba(139,158,219,0.06) 1px, transparent 1px)",
      },
      backgroundSize: {
        grid: "28px 28px",
      },
      borderRadius: {
        xl2: "1.25rem",
      },
      keyframes: {
        "scan-sweep": {
          "0%": { transform: "translateY(-100%)" },
          "100%": { transform: "translateY(100%)" },
        },
        "fade-up": {
          "0%": { opacity: "0", transform: "translateY(8px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        "pulse-dot": {
          "0%, 100%": { opacity: "1" },
          "50%": { opacity: "0.35" },
        },
      },
      animation: {
        "fade-up": "fade-up 0.5s ease-out both",
        "pulse-dot": "pulse-dot 2s ease-in-out infinite",
      },
    },
  },
  plugins: [],
};
