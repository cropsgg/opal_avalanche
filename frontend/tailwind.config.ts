import type { Config } from 'tailwindcss';

const config: Config = {
  darkMode: ['class'],
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      translate: {
        '101': '101%',
      },

      fontFamily: {
        'display': ['var(--font-playfair)', 'serif'],
        'body': ['var(--font-merriweather)', 'serif'],
        'neu': ['neu', 'sans-serif'],
      },
      colors: {
        cream: {
          50: '#F6F0E8',
          100: '#FFF9F3'
        },
        brown: {
          900: '#3B2F2C',
          700: '#6B4226',
          500: '#8D5A45'
        },
        gold: {
          500: '#CFA96B'
        },
        olive: {
          400: '#7C7A53'
        },
        stone: {
          200: '#E8E3DE'
        },
        error: {
          500: '#A33A3A'
        },
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
        card: {
          DEFAULT: 'hsl(var(--card))',
          foreground: 'hsl(var(--card-foreground))',
        },
        popover: {
          DEFAULT: 'hsl(var(--popover))',
          foreground: 'hsl(var(--popover-foreground))',
        },
        primary: {
          DEFAULT: 'hsl(var(--primary))',
          foreground: 'hsl(var(--primary-foreground))',
        },
        secondary: {
          DEFAULT: 'hsl(var(--secondary))',
          foreground: 'hsl(var(--secondary-foreground))',
        },
        muted: {
          DEFAULT: 'hsl(var(--muted))',
          foreground: 'hsl(var(--muted-foreground))',
        },
        accent: {
          DEFAULT: 'hsl(var(--accent))',
          foreground: 'hsl(var(--accent-foreground))',
        },
        destructive: {
          DEFAULT: 'hsl(var(--destructive))',
          foreground: 'hsl(var(--destructive-foreground))',
        },
        border: 'hsl(var(--border))',
        input: 'hsl(var(--input))',
        ring: 'hsl(var(--ring))',
        chart: {
          '1': 'hsl(var(--chart-1))',
          '2': 'hsl(var(--chart-2))',
          '3': 'hsl(var(--chart-3))',
          '4': 'hsl(var(--chart-4))',
          '5': 'hsl(var(--chart-5))',
        },
      },
      backgroundColor: {
        page: '#F6F0E8'
      },
      letterSpacing: {
        'tight': '-0.02em',
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-conic':
          'conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))',
      },
      borderRadius: {
        lg: 'var(--radius)',
        md: 'calc(var(--radius) - 2px)',
        sm: 'calc(var(--radius) - 4px)',
      },
      keyframes: {
        marquee: {
          'from': { transform: 'translateX(0%)' },
          'to': { transform: 'translateX(-50%)' }
        },
        move: {
          '0%': { transform: 'translateX(0)' },
          '100%': { transform: 'translateX(-100%)' },
        },
        gooey: {
          '0%': {
            filter: 'blur(20px)',
            transform: 'translate(10%, -10%) skew(0deg)'
          },
          '100%': {
            filter: 'blur(30px)',
            transform: 'translate(-10%, 10%) skew(-12deg)'
          },
        },
        footergooey: {
          '0%': {
            filter: 'blur(50px)',
            transform: 'translate(10%, -10%) skew(0deg)'
          },
          '100%': {
            filter: 'blur(30px)',
            transform: 'translate(-10%, 10%) skew(-12deg)'
          },
        },
        'accordion-down': {
          from: {
            height: '0',
          },
          to: {
            height: 'var(--radix-accordion-content-height)',
          },
        },
        'accordion-up': {
          from: {
            height: 'var(--radix-accordion-content-height)',
          },
          to: {
            height: '0',
          },
        },
      },
      animation: {
        'move': 'move 10s linear infinite',
        'gooey': 'gooey 6s ease-in-out infinite alternate',
        'footergooey': 'footergooey 5s ease-in-out infinite alternate',
        marquee: 'marquee 15s linear infinite',
        'accordion-down': 'accordion-down 0.2s ease-out',
        'accordion-up': 'accordion-up 0.2s ease-out',
      },
    },
  },
  plugins: [require('tailwindcss-animate')],
};

export default config;
