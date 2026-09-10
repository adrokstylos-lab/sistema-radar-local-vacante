/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        void: "#05070A",
        ink: "#0A0E14",
        carbon: "#12161D",
        graphite: "#1B2129",
        steel: "#2A3340",
        haze: "#8FA0B4",
        ghost: "#A7B0BE",
        bright: "#F5F8FF",
        ice: "#7DE3FF",
        vac: "#35E0A1",
        unver: "#F5C36B",
        closed: "#E5556E",
      },
      fontFamily: {
        hud: ['Oxanium', 'system-ui', 'sans-serif'],
        body: ['Inter', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        glass: "0 8px 40px rgba(0,0,0,0.55), inset 0 1px 0 rgba(255,255,255,0.06)",
        glow: "0 0 0 1px rgba(125,227,255,0.25), 0 0 24px rgba(125,227,255,0.15)",
        panel: "0 20px 60px rgba(0,0,0,0.65)",
      },
      backdropBlur: {
        xs: "2px",
      },
      keyframes: {
        pulse2: {
          "0%, 100%": { transform: "scale(1)", opacity: "0.9" },
          "50%": { transform: "scale(1.15)", opacity: "0.5" },
        },
      },
      animation: {
        pulse2: "pulse2 2.2s ease-in-out infinite",
      },
    },
  },
  plugins: [],
};
