# B1 Design System Implementation Guide for Story of Dubai

**Target**: Apply B1 Properties premium design (gold, luxury fonts, minimal borders) to storyofdubai.com  
**Duration**: ~4 hours  
**Difficulty**: Medium (CSS-only, no logic changes)

---

## 📋 STEP-BY-STEP IMPLEMENTATION

### PHASE 1: Setup & Configuration (30 mins)

#### 1.1 Update Tailwind Configuration

**File**: `frontend/tailwind.config.ts`

```typescript
import type { Config } from 'tailwindcss'

export default {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // B1 Properties brand colors
        'b1-gold': '#96651E',           // Primary action color
        'b1-gold-hover': '#7a5318',     // Gold hover state
        'b1-dark': '#444444',           // Secondary text
        'b1-darker': '#404040',         // Headings/strong text
        'b1-light': '#D9D9D9',          // Borders/dividers
        'b1-white': '#FFFFFF',          // Backgrounds
        
        // Accent grays (for compatibility)
        'gray-50': '#f9fafb',
        'gray-100': '#f3f4f6',
        'gray-300': '#d1d5db',
        'gray-500': '#6b7280',
        'gray-600': '#4b5563',
        'gray-700': '#374151',
        'gray-900': '#111827',
      },
      fontFamily: {
        'dm-sans': 'var(--font-dm-sans, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif)',
        'luxury': 'var(--font-luxury, serif)',
      },
      borderRadius: {
        'xs': '2px',
        'sm': '4px',
        'md': '6px',
        'lg': '8px',
        'xl': '12px',
      },
      spacing: {
        // Responsive spacing helpers
        'safe-4': '1rem',
        'safe-6': '1.5rem',
        'safe-8': '2rem',
      },
    },
  },
  plugins: [],
} satisfies Config
```

#### 1.2 Update Global Styles

**File**: `frontend/app/globals.css`

```css
@import "tailwindcss";

:root {
  /* B1 Properties Brand Colors */
  --color-primary: #96651E;        /* Gold */
  --color-primary-hover: #7a5318;  /* Gold Hover */
  --color-dark: #444444;           /* Text */
  --color-darker: #404040;         /* Headings */
  --color-light: #D9D9D9;          /* Borders */
  --color-white: #FFFFFF;          /* Background */
  
  /* Backgrounds */
  --background: #ffffff;
  --foreground: #171717;
  
  /* Fonts */
  --font-dm-sans: 'DM Sans', system-ui, sans-serif;
  --font-luxury: 'Luxury Font', serif;
}

@theme inline {
  --color-background: var(--background);
  --color-foreground: var(--foreground);
  --color-primary: var(--color-primary);
  --font-sans: var(--font-dm-sans);
  --font-luxury: var(--font-luxury);
}

@media (prefers-color-scheme: dark) {
  :root {
    --background: #0a0a0a;
    --foreground: #ededed;
  }
}

/* Body & Typography */
body {
  background: var(--background);
  color: var(--color-dark);
  font-family: var(--font-dm-sans), system-ui, sans-serif;
  font-weight: 400;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* Headings: Use Luxury Font */
h1, h2, h3, h4, h5, h6 {
  font-family: var(--font-luxury), serif;
  font-weight: 400;
  color: var(--color-darker);
}

h1 { font-size: 2.5rem; line-height: 2.75rem; }
h2 { font-size: 2rem; line-height: 2.25rem; }
h3 { font-size: 1.5rem; line-height: 1.75rem; }

/* Text Elements: Use DM Sans */
p, span, a, button, input, textarea, select, label, li {
  font-family: var(--font-dm-sans), sans-serif;
}

/* Form Elements */
input, textarea, select {
  border: 1px solid var(--color-light);
  border-radius: 2px;
  padding: 0.75rem 1rem;
  font-family: var(--font-dm-sans);
  font-size: 1rem;
  color: var(--color-darker);
  background-color: white;
  transition: all 200ms ease;
}

input:focus, textarea:focus, select:focus {
  border-color: var(--color-darker);
  outline: none;
  box-shadow: 0 0 0 1px var(--color-darker);
}

input::placeholder {
  color: var(--color-dark);
  opacity: 0.6;
}

/* Links */
a {
  color: var(--color-primary);
  text-decoration: none;
  transition: color 200ms ease;
}

a:hover {
  color: var(--color-primary-hover);
}

/* Scrollbar Hiding */
.scrollbar-hide::-webkit-scrollbar {
  display: none;
}

.scrollbar-hide {
  -ms-overflow-style: none;
  scrollbar-width: none;
}

/* Utility Classes */
.text-primary { color: var(--color-primary); }
.text-dark { color: var(--color-dark); }
.bg-primary { background-color: var(--color-primary); }
.border-light { border-color: var(--color-light); }
```

---

### PHASE 2: Component Updates (2 hours)

#### 2.1 Update ScoreBadge Component

**File**: `frontend/components/ScoreBadge.tsx`

```typescript
interface ScoreBadgeProps {
  score: number
  size?: 'sm' | 'md' | 'lg'
}

export default function ScoreBadge({ score, size = 'md' }: ScoreBadgeProps) {
  const getColor = (score: number) => {
    if (score >= 80) return { bg: '#96651E', label: 'Exceptional' }     // Gold
    if (score >= 70) return { bg: '#96651E', label: 'Very Good' }       // Gold
    if (score >= 60) return { bg: '#96651E', label: 'Good' }            // Gold
    if (score >= 40) return { bg: '#D9D9D9', label: 'Fair' }            // Light gray
    return { bg: '#D9D9D9', label: 'Listed' }                            // Light gray
  }

  const color = getColor(score)
  const sizeClasses = {
    sm: 'w-12 h-12 text-xs',
    md: 'w-16 h-16 text-sm',
    lg: 'w-20 h-20 text-lg',
  }

  return (
    <div
      className={`${sizeClasses[size]} rounded-xs flex flex-col items-center justify-center`}
      style={{ backgroundColor: color.bg }}
    >
      <div className={`font-luxury font-bold text-white`}>
        {score.toFixed(0)}
      </div>
      <div className="text-white text-xs mt-1 font-dm-sans">
        {color.label}
      </div>
    </div>
  )
}
```

#### 2.2 Update Button Styling (All Button Components)

**Pattern to use everywhere**:

```typescript
// Primary Button (Gold)
<button
  className="bg-b1-gold hover:bg-b1-gold-hover text-white font-dm-sans font-medium py-3 sm:py-4 px-6 rounded-xs transition-all duration-200"
>
  {children}
</button>

// Secondary Button (Outlined)
<button
  className="border-2 border-b1-gold text-b1-gold hover:bg-gray-50 font-dm-sans font-medium py-3 sm:py-4 px-6 rounded-xs transition-all duration-200"
>
  {children}
</button>

// Ghost Button
<button
  className="text-b1-gold hover:text-b1-gold-hover font-dm-sans underline transition-colors duration-200"
>
  {children}
</button>
```

**Files to update**:
- `components/Layout.tsx` - Header buttons
- `components/VenueCard.tsx` - CTA button
- `components/EmailCapture.tsx` - Subscribe button
- `pages/*/[venue].tsx` - View details buttons
- All modal buttons

#### 2.3 Update Form Components

**Input Style Pattern**:

```typescript
const inputClasses = `
  w-full
  border border-b1-light
  rounded-xs
  px-4 py-3 sm:py-4
  text-sm sm:text-base
  font-dm-sans
  text-b1-darker
  placeholder:text-b1-dark placeholder:opacity-60
  focus:border-b1-darker
  focus:ring-1 focus:ring-b1-darker
  focus:outline-none
  transition-all duration-200
  bg-white
`
```

**Update files**:
- `components/EmailCapture.tsx`
- `components/AppointmentModal.tsx` (if you create one)
- Any form pages

#### 2.4 Update Card Components

**Card Style Pattern**:

```typescript
<div
  className="
    bg-white
    border border-b1-light
    rounded-xs
    p-4 sm:p-6
    shadow-sm
    hover:shadow-md
    transition-shadow duration-200
  "
>
  {children}
</div>
```

**Files to update**:
- `components/VenueCard.tsx`
- Create `PropertyCard.tsx`
- Create `VisaCard.tsx`

#### 2.5 Update Layout Component

**File**: `frontend/components/Layout.tsx`

```typescript
<header className="border-b border-b1-light bg-white sticky top-0 z-40">
  <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between">
    {/* Logo */}
    <h1 className="text-2xl font-luxury text-b1-darker">Story of Dubai</h1>
    
    {/* Navigation Links */}
    <ul className="flex gap-6 font-dm-sans">
      <li><a href="/restaurants" className="text-b1-dark hover:text-b1-gold transition-colors">Restaurants</a></li>
      <li><a href="/apartments" className="text-b1-dark hover:text-b1-gold transition-colors">Apartments</a></li>
      <li><a href="/visa-guide" className="text-b1-dark hover:text-b1-gold transition-colors">Visa Guides</a></li>
    </ul>
  </nav>
</header>

<footer className="bg-b1-darker text-white py-12 px-4 sm:px-6 lg:px-8">
  <div className="max-w-7xl mx-auto font-dm-sans text-sm">
    <p>&copy; 2026 Story of Dubai. All rights reserved.</p>
  </div>
</footer>
```

---

### PHASE 3: Page Updates (1 hour)

#### 3.1 Update Detail Pages

**Pattern for `/[category]/[area]/[venue].tsx`**:

```typescript
<div className="bg-gradient-to-r from-gray-50 to-gray-100 rounded-xs p-6 mb-6 border border-b1-light">
  <p className="text-sm text-b1-gold font-medium mb-1">Asking Price</p>
  <p className="text-3xl font-luxury font-bold text-b1-darker">
    AED {property.price_aed.toLocaleString()}
  </p>
</div>

<a
  href={property.affiliate_url}
  className="inline-block w-full text-center bg-b1-gold hover:bg-b1-gold-hover text-white font-medium font-dm-sans py-3 rounded-xs transition-colors mb-6"
>
  View on PropertyFinder →
</a>
```

#### 3.2 Update Hero Sections

**Pattern for hero backgrounds**:

```typescript
<section className="relative bg-white border-b border-b1-light py-16 sm:py-20 lg:py-24">
  <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <h1 className="text-4xl md:text-5xl font-luxury text-b1-darker mb-4">
      {title}
    </h1>
    <p className="text-lg text-b1-dark max-w-2xl mb-8">
      {description}
    </p>
    <button className="bg-b1-gold hover:bg-b1-gold-hover text-white py-3 px-6 rounded-xs font-dm-sans font-medium transition-colors">
      Get Started
    </button>
  </div>
</section>
```

---

### PHASE 4: Testing & Refinement (30 mins)

#### 4.1 Browser Testing Checklist

```
Desktop (1920px):
- [ ] All buttons show gold color
- [ ] Hover states work (darker gold)
- [ ] Borders appear light gray (2px radius)
- [ ] Typography is clean and readable
- [ ] Spacing is consistent

Tablet (768px):
- [ ] Responsive padding works
- [ ] Form inputs resize properly
- [ ] Buttons remain clickable
- [ ] Modal works on smaller screen

Mobile (375px):
- [ ] Text is readable (no overflow)
- [ ] Buttons stack vertically if needed
- [ ] Form inputs are touch-friendly
- [ ] No horizontal scroll
```

#### 4.2 Color Verification

```
Use browser DevTools to check:
- Primary buttons: #96651E (gold)
- Button hover: #7a5318 (darker gold)
- Text: #444444 (dark gray)
- Borders: #D9D9D9 (light gray)
- Focus rings: #404040 (darker gray)
- Links: #96651E (gold)
```

#### 4.3 Typography Check

```
- Headings: Luxury font, weight 400
- Body text: DM Sans, weight 400
- Button text: DM Sans, weight 500 (medium)
- All text antialiased: ✓
```

---

## 🔧 CONFIGURATION FILES

### Required: Import DM Sans Font

**File**: `frontend/components/Layout.tsx` (or `app/_app.tsx`)

```typescript
import { DM_Sans } from 'next/font/google'

const dmSans = DM_Sans({
  subsets: ['latin'],
  variable: '--font-dm-sans',
  display: 'swap',
})

export default function RootLayout({ children }) {
  return (
    <html lang="en" className={dmSans.variable}>
      <body>{children}</body>
    </html>
  )
}
```

### Optional: Luxury Font Setup

If using a custom luxury font, add to `next.config.js`:

```javascript
const nextConfig = {
  webpack: (config) => {
    config.module.rules.push({
      test: /\.(woff|woff2|eot|ttf|otf)$/i,
      type: 'asset/resource',
      generator: {
        filename: 'static/fonts/[name].[hash][ext]',
      },
    })
    return config
  },
}
```

---

## 📊 COLOR REPLACEMENT GUIDE

### Search & Replace in Code

```
# In your IDE, use Find & Replace:

Find: rounded-lg
Replace: rounded-xs

Find: rounded-xl
Replace: rounded-xs

Find: from-blue-50
Replace: from-gray-50

Find: to-blue-100
Replace: to-gray-100

Find: hover:text-blue-600
Replace: hover:text-b1-gold

Find: bg-blue-600
Replace: bg-b1-gold

Find: hover:bg-blue-700
Replace: hover:bg-b1-gold-hover

Find: border-gray-200
Replace: border-b1-light

Find: text-gray-600
Replace: text-b1-dark

Find: text-gray-900
Replace: text-b1-darker

Find: focus:border-gray-900
Replace: focus:border-b1-darker

Find: focus:ring-gray-900
Replace: focus:ring-b1-darker
```

---

## ✅ VALIDATION CHECKLIST

Before committing, verify:

- [ ] All buttons use gold color (#96651E)
- [ ] Button hover states use darker gold (#7a5318)
- [ ] All inputs have 2px border radius
- [ ] Form focus states show dark border + ring
- [ ] Headings use Luxury font
- [ ] Body text uses DM Sans
- [ ] No blue colors remain (replaced with gold)
- [ ] Border colors updated to light gray (#D9D9D9)
- [ ] Spacing is responsive (sm: / md: / lg:)
- [ ] Modal styling matches B1 pattern
- [ ] All transitions are 200ms
- [ ] No rounded corners > 8px
- [ ] TypeScript compiles: `npm run build`
- [ ] No lint errors: `npm run lint`

---

## 🚀 DEPLOYMENT STEPS

```bash
# 1. Create feature branch
git checkout -b design/b1-style-system

# 2. Make all CSS changes
# ... run through all phases above ...

# 3. Build and test
npm run build
npm run lint

# 4. Test locally
npm run dev
# Visit http://localhost:3000 and verify all pages

# 5. Commit changes
git add .
git commit -m "design: apply B1 Properties design system

- Update color scheme: gold (#96651E) primary
- Change border radius to 2px (minimal style)
- Import DM Sans font for body text
- Apply Luxury font to headings
- Update all button and form styles
- Update modal and card styling
- Responsive breakpoint updates
- All transitions 200ms ease

Testing:
- Verified on desktop (1920px)
- Verified on tablet (768px)
- Verified on mobile (375px)
- All buttons, forms, and interactions tested
"

# 6. Push and create PR
git push origin design/b1-style-system
```

---

## ⏱️ TIME ESTIMATE

| Phase | Task | Duration |
|-------|------|----------|
| 1 | Setup & Config | 30 min |
| 2 | Component Updates | 2 hr |
| 3 | Page Updates | 1 hr |
| 4 | Testing & QA | 30 min |
| **Total** | | **~4 hours** |

---

## 📝 NOTES

- Keep all logic unchanged (CSS-only modifications)
- Ensure all components remain accessible
- Test all interactive elements
- Verify responsive behavior on all breakpoints
- Keep animations smooth (200ms transitions)
- No breaking changes to API or data structures

**Status**: Ready for implementation  
**Next Step**: Follow PHASE 1 above to start setup

