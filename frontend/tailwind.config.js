/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        cream: {
          DEFAULT: "#DDD0C8",
          light: "#F5EDE5",
          sidebar: "#E8DDD3",
        },
        sand: {
          border: "#C9BDB3",
        },
        charcoal: {
          DEFAULT: "#323232",
          muted: "#5A5A5A",
        },
        accent: {
          DEFAULT: "#8B7355",
        },
        weakness: {
          severe: "#7C2D12",
        },
      },
    },
  },
  plugins: [],
};
