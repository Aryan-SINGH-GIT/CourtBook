/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    darkMode: 'class',
    theme: {
        extend: {
            fontFamily: {
                sans: ['Inter', 'sans-serif'],
                display: ['Outfit', 'sans-serif'],
            },
            colors: {
                // Custom Minimalist Palette
                brand: {
                    black: '#09090b', // Deepest black-grey for main dark bg
                    dark: '#18181b',  // Dark grey for cards/surfaces
                    grey: '#27272a',  // Lighter grey for borders/secondary
                    light: '#f4f4f5', // Very light grey for light mode backgrounds
                    white: '#ffffff',
                    blue: '#1e40af',  // Navy Blue Accent
                }
            },
            animation: {
                'fade-in': 'fadeIn 0.5s ease-out',
            },
            keyframes: {
                fadeIn: {
                    '0%': { opacity: '0', transform: 'translateY(10px)' },
                    '100%': { opacity: '1', transform: 'translateY(0)' },
                }
            }
        },
    },
    plugins: [],
}
