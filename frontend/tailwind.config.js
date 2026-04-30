export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        canvas: "#f5f3ee",
        ink: "#161616",
        brand: {
          50: "#eef6f3",
          100: "#d7ebe4",
          500: "#1f7662",
          600: "#195f4f",
          700: "#11453a"
        },
        accent: {
          100: "#f7e4b6",
          500: "#c68d1f",
          700: "#8c5f06"
        }
      },
      fontFamily: {
        display: ["ui-serif", "Georgia", "serif"],
        body: ["ui-sans-serif", "system-ui", "sans-serif"]
      },
      boxShadow: {
        soft: "0 16px 40px rgba(20, 24, 28, 0.08)"
      }
    },
  },
  plugins: [],
};

