/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Orbitron', 'sans-serif'],
      },
      colors: {
        'cyan-glow': '#00ffff',
        'magenta-glow': '#ff00ff',
        'blue-glow': '#0077ff',
      },
      boxShadow: {
        'neon-cyan': '0 0 5px #00ffff, 0 0 10px #00ffff, 0 0 20px #00ffff, 0 0 40px #00ffff',
        'neon-magenta': '0 0 5px #ff00ff, 0 0 10px #ff00ff, 0 0 20px #ff00ff, 0 0 40px #ff00ff',
        'neon-blue': '0 0 5px #0077ff, 0 0 10px #0077ff, 0 0 20px #0077ff, 0 0 40px #0077ff',
      }
    },
  },
  plugins: [],
}
