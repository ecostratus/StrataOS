/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["\"DM Sans\"", "\"Segoe UI\"", "sans-serif"]
      }
    }
  },
  plugins: []
};
