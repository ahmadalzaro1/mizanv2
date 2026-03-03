/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        tajawal: ['Tajawal', 'sans-serif'],
      },
      colors: {
        mizan: {
          navy: '#1a1a2e',
          surface: '#f9f9f9',
        },
      },
    },
  },
  plugins: [],
}
