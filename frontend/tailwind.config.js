/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        marble: "#F5F0E8",
        sand: "#E8DCC8",
        stone: "#8B7D6B",
        bronze: "#CD7F32",
        gold: "#D4AF37",
        olive: "#556B2F",
        terracotta: "#CC5533",
        ocean: "#2E5A88",
        night: "#1A1A2E",
        ink: "#2D2D2D",
        // Provider colors
        provider: {
          anthropic: "#D97706",
          openai: "#10B981",
          google: "#3B82F6",
          xai: "#8B5CF6",
          deepseek: "#06B6D4",
          kimi: "#EC4899",
          qwen: "#F97316",
          glm: "#EF4444",
        },
      },
      fontFamily: {
        display: ["Cinzel", "serif"],
        body: ["Inter", "sans-serif"],
      },
    },
  },
  plugins: [],
};
