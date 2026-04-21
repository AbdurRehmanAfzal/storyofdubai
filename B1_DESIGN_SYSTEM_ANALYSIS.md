# B1 Properties Design System Analysis & Application to Story of Dubai

**Scan Date**: 2026-04-21  
**Source**: https://b1properties.ae (Local: ~/Documents/B1 Website/b1properties-frontend)  
**Application**: Story of Dubai (storyofdubai.com)

---

## 📊 DESIGN SYSTEM OVERVIEW

### Color Scheme

| Color | Hex | Usage | Component |
|-------|-----|-------|-----------|
| **Primary Gold** | `#96651E` | Primary actions, key elements | Buttons, accents, highlights |
| **Primary Gold Hover** | `#7a5318` | Hover states | Button hover, interactive focus |
| **Dark Gray** | `#444444` | Text, secondary elements | Paragraph text, secondary labels |
| **Darker Gray** | `#404040` | Headers, primary text | Headings, strong text |
| **Light Gray** | `#D9D9D9` | Borders, dividers | Form inputs, lines, separators |
| **White** | `#FFFFFF` | Background, contrast | Cards, modals, clean spaces |
| **Black** | `#000000` / `#1a1a1a` | Borders, focus states | Borders, focus rings |

### Typography

```css
/* Primary Font: DM Sans */
- Body: DM Sans (Weight 400, Regular)
- Smooth rendering: -webkit-font-smoothing: antialiased
- Platform smoothing: -moz-osx-font-smoothing: grayscale

/* Display Font: Luxury Font (Top Luxury) */
- Headings: h1-h6 use Luxury Font (Weight 400, serif style)
- File location: /DM_Sans folder in project
- Purpose: Premium, elegant appearance for headlines
```

### Spacing & Sizing

```javascript
// Responsive spacing patterns
py-16 sm:py-20 lg:py-24  // Vertical sections: 64px → 80px → 96px
px-4 sm:px-6 lg:px-8     // Horizontal padding: 16px → 24px → 32px
gap-4 sm:gap-6           // Component gaps: 16px → 24px
p-6 sm:p-8               // Internal padding: 24px → 32px
```

### Border Styles

- **Border Radius**: Minimal, `2px` (squarish, not rounded)
- **Border Width**: 1-2px for inputs and cards
- **Border Color**: `#d1d5db` (light gray) → `#111827` (black on focus)
- **Focus State**: `1px solid border` + `1px ring` for inputs

---

## 🎨 COMPONENT STYLES

### Buttons

```css
/* Primary Button (Gold) */
backgroundColor: #96651E
color: white
padding: py-3 sm:py-4, px-3 sm:px-6
fontSize: sm:text-base
fontFamily: var(--font-dm-sans)
borderRadius: 2px
transition: all 200ms

/* Hover State */
backgroundColor: #7D5520 (darker gold)

/* Secondary Button (Outlined) */
borderColor: #966627
color: #966627
backgroundColor: transparent
hover: backgroundColor: #f5f5f5

/* Disabled State */
opacity: 0.5
cursor: not-allowed
```

### Form Inputs

```css
/* Input Fields */
border: 1px solid #d1d5db
padding: py-3 sm:py-4, px-3 sm:px-4
fontSize: sm:text-base
fontFamily: var(--font-dm-sans)
borderRadius: 2px
backgroundColor: white
color: #1a1a1a

/* Focus State */
borderColor: #111827 (gray-900)
ring: 1px solid #111827
outline: none

/* Placeholder */
color: #6b7280 (gray-500)
opacity: 1

/* Disabled State */
backgroundColor: #f3f4f6
cursor: not-allowed
color: #9ca3af
```

### Appointment Modal (Complex Component)

```css
/* Modal Container */
position: fixed inset-0 z-50
display: flex items-center justify-center
padding: p-4

/* Modal Content */
backgroundColor: white
borderRadius: 0px (no rounding)
boxShadow: shadow-xl
maxWidth: max-w-2xl
maxHeight: max-h-[90vh]
overflow: overflow-y-auto

/* Close Button */
position: absolute top-4 right-4
color: #9ca3af
hover:color: #4b5563
transition: transition-colors

/* Form Spacing */
space-y-4 (16px between form items)

/* Toggle Buttons (In-person vs Video) */
grid grid-cols-2
gap-3 sm:gap-4
border: 1px solid #d1d5db
py-3 sm:py-4
padding-x: px-3 sm:px-6
transition: all
active: border-gray-900, bg-white, font-medium
inactive: border-gray-300, text-gray-600, hover:border-gray-400
```

### Country Selector Dropdown

```css
/* Trigger Button */
position: absolute left-3 top-1/2 -translate-y-1/2
display: flex items-center gap-1 sm:gap-2
padding: px-1.5 sm:px-2 py-1
hover: bg-gray-100
borderRadius: 2px
z-index: 10

/* Dropdown Menu */
position: absolute left-0 top-full
margin-top: mt-2
width: w-full
backgroundColor: white
border: 1px solid #d1d5db
boxShadow: shadow-lg
maxHeight: max-h-60
overflow-y: overflow-y-auto
z-index: 20
borderRadius: 2px

/* Dropdown Item */
width: w-full
display: flex items-center gap-2 sm:gap-3
padding: px-3 sm:px-4 py-2.5 sm:py-3
hover: bg-gray-50
transition: transition-colors
text-align: text-left
```

### Date & Time Picker

```css
/* Date Input Wrapper */
position: relative
border: 1px solid #d1d5db
display: flex items-center justify-between
padding: px-3 sm:px-4 py-3 sm:py-4
backgroundColor: white
borderRadius: 2px
pointer-events: none (for the wrapper)

/* Actual Date Input */
position: absolute inset-0
z-index: 10
width: w-full height: h-full
cursor: cursor-pointer
opacity: opacity-0
appearance: appearance-none

/* Time Select */
width: w-full
border: 1px solid #d1d5db
padding: px-3 sm:px-4 py-3 sm:py-4
backgroundColor: white
appearance: appearance-none (removes default styling)
cursor: cursor-pointer
borderRadius: 2px

/* Dropdown Arrow */
position: absolute right-3 sm:right-4 top-1/2 -translate-y-1/2
pointer-events: pointer-events-none
```

---

## 🏗️ LAYOUT PATTERNS

### Section Container
```javascript
<section className="relative py-16 sm:py-20 lg:py-24 overflow-hidden bg-white">
  <div className="relative z-10 max-w-7xl mx-auto px-2 sm:px-4 lg:px-6">
    {/* Content */}
  </div>
</section>
```

### Responsive Grid
```javascript
// 2-column on mobile, 1 on desktop
grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4

// Heading sizes
text-2xl sm:text-3xl md:text-4xl

// Padding responsive
px-4 sm:px-6 lg:px-8
py-3 sm:py-4
```

### Modal Structure
```javascript
// Backdrop
<div className="absolute inset-0 bg-black bg-opacity-50" onClick={onClose} />

// Content
<div className="relative bg-white rounded-sm shadow-xl max-w-2xl w-full">
  <button className="absolute top-4 right-4">{/* close icon */}</button>
  <div className="p-6 sm:p-8">
    {/* content */}
  </div>
</div>
```

---

## 🎯 VISUAL HIERARCHY

### Text Sizes
- **Headings (h1-h3)**: 40px-64px (luxury font)
- **Subheadings (h4-h5)**: 20px-28px
- **Body Text**: 14px-16px (DM Sans)
- **Small Text**: 12px-14px
- **Captions**: 11px-12px

### Font Weights
- **Luxury Font**: 400 (regular)
- **DM Sans Regular**: 400
- **DM Sans Medium**: 500 (buttons, labels)
- **DM Sans Bold**: 700 (rare, strong emphasis)

### Color Hierarchy
1. **Primary Actions**: Gold (#96651E)
2. **Text**: Dark gray (#444444) or Darker gray (#404040)
3. **Secondary Elements**: Light gray (#D9D9D9)
4. **Accents**: Black (#1a1a1a) for focus/borders

---

## 🔄 INTERACTION PATTERNS

### Hover States
- Buttons: `transition-colors 200ms`
- Gold button: #96651E → #7D5520
- Text links: color change with `hover:text-blue-600`
- Inputs: Border color change #d1d5db → #111827

### Focus States
- Border: Solid 1px black (#111827)
- Ring: 1px solid black
- Outline: Removed (outline-none)
- No color change for background

### Disabled States
- Opacity: 0.5
- Cursor: not-allowed
- Background: Lightened (#f3f4f6)

### Active/Selected States
- Buttons: `border-gray-900 font-medium`
- Form inputs: Focused styling applied
- Dropdowns: Option highlighted on hover

---

## ✨ SPECIAL EFFECTS & POLISH

### Animations
```css
transition: all 200ms
transition: transition-colors
transition: transition-transform
```

### Shadows
- Cards: `shadow-xl`
- Dropdowns: `shadow-lg`
- No shadows on flat elements

### Scrollbar Hiding
```css
.scrollbar-hide::-webkit-scrollbar {
  display: none;
}
.scrollbar-hide {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
```

### Scrolling & Overflow
```css
max-h-[90vh] overflow-y-auto  /* Modals */
max-h-60 overflow-y-auto      /* Dropdowns */
```

---

## 📱 RESPONSIVE BREAKPOINTS

```javascript
// Tailwind breakpoints used
sm: 640px   (tablet portrait)
md: 768px   (tablet landscape)
lg: 1024px  (desktop)
xl: 1280px  (large desktop)
2xl: 1536px (extra large)

// Pattern examples
hidden lg:block              /* Show on desktop only */
py-16 sm:py-20 lg:py-24     /* Progressive spacing */
text-sm sm:text-base        /* Progressive text size */
px-4 sm:px-6 lg:px-8        /* Progressive padding */
grid-cols-1 sm:grid-cols-2  /* Progressive layout */
```

---

## 🎨 APPLYING TO STORY OF DUBAI

### 1. **Update Tailwind Config**

```javascript
// tailwind.config.ts
export default {
  theme: {
    extend: {
      colors: {
        'b1-gold': '#96651E',
        'b1-gold-hover': '#7a5318',
        'b1-dark': '#444444',
        'b1-darker': '#404040',
        'b1-light': '#D9D9D9',
      },
      fontFamily: {
        'dm-sans': 'var(--font-dm-sans)',
        'luxury': 'var(--font-luxury)',
      },
      borderRadius: {
        'xs': '2px',
      },
    },
  },
};
```

### 2. **Update Global CSS**

```css
/* Apply B1 color scheme */
:root {
  --color-primary: #96651E;      /* B1 Gold */
  --color-primary-hover: #7a5318; /* B1 Gold Hover */
  --color-dark: #444444;          /* B1 Dark Gray */
  --color-darker: #404040;        /* B1 Darker Gray */
  --color-light: #D9D9D9;         /* B1 Light Gray */
  --color-white: #FFFFFF;         /* B1 White */
}

/* Typography */
h1, h2, h3, h4, h5, h6 {
  font-family: var(--font-luxury), serif;
  font-weight: 400;
}

body {
  font-family: var(--font-dm-sans), sans-serif;
  color: #444444;
}
```

### 3. **Update Components**

```typescript
// Button Component
const buttonClasses = {
  primary: 'bg-b1-gold hover:bg-b1-gold-hover text-white',
  secondary: 'border-b1-gold text-b1-gold hover:bg-gray-50',
  ghost: 'text-b1-gold hover:text-b1-gold-hover',
};

// Input Component
const inputClasses = 'border border-b1-light focus:border-b1-darker focus:ring-1 focus:ring-b1-darker rounded-xs';

// Modal Component
const modalClasses = 'bg-white rounded-xs shadow-xl max-w-2xl';
```

### 4. **Update Colors in Pages**

Replace TailwindCSS colors with B1 palette:
- `from-blue-50` → `from-gray-50`
- `hover:shadow-sm` → Remove (B1 uses minimal shadows)
- `rounded-xl` → `rounded-xs` (2px border radius)
- Primary color accents: Blue → Gold (#96651E)

### 5. **Key Files to Update**

```
frontend/
├── app/globals.css                          # Update CSS variables
├── components/ScoreBadge.tsx                # Update color logic
├── components/VenueCard.tsx                 # Button styles
├── components/Layout.tsx                    # Header/footer styling
├── components/BreadcrumbNav.tsx             # Separator colors
├── components/EmailCapture.tsx              # Form input styles
├── pages/[category]/[area]/[venue].tsx     # Button styling
├── pages/apartments/.../*.tsx               # Form styling
└── tailwind.config.ts                       # Theme extension
```

---

## 🎯 QUICK IMPLEMENTATION CHECKLIST

- [ ] Update `tailwind.config.ts` with B1 colors
- [ ] Update `app/globals.css` with B1 CSS variables
- [ ] Replace all `rounded-lg` with `rounded-xs`
- [ ] Replace all blue colors with gold (#96651E)
- [ ] Update button hover states to #7a5320
- [ ] Update input focus states (border-gray-900, ring-gray-900)
- [ ] Import DM Sans font in Layout
- [ ] Update button styling in all forms
- [ ] Update card borders to light gray (#D9D9D9)
- [ ] Test responsive behavior on sm/md/lg breakpoints
- [ ] Update modal styling in AppointmentModal-like components
- [ ] Remove unnecessary shadows (use shadow-xl only on modals)
- [ ] Update heading fonts to luxury font where available
- [ ] Test all form inputs and focus states

---

## 🖼️ VISUAL REFERENCE ASSETS

From B1 Properties:
- **Logo**: Luxury serif style
- **Colors**: Gold (#96651E) on white
- **Typography**: DM Sans (body) + Luxury font (headings)
- **Spacing**: Conservative, 16px-96px sections
- **Borders**: Minimal, 2px radius, light gray (#D9D9D9)
- **Buttons**: Gold background, square borders, 200ms transitions
- **Forms**: Minimal styling, focus on inputs with rings
- **Modals**: White background, shadow, max-width 2xl
- **Images**: High-quality, aspect-ratio preserved

---

**Status**: Ready for implementation  
**Estimated Implementation Time**: 3-4 hours  
**Risk Level**: Low (CSS changes only, no logic changes)  
**Testing Required**: Visual regression testing on all breakpoints

