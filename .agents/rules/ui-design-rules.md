# NAVIS — UI Color Theme & Design Rules

All UI work across NAVIS (dashboard, web pages, visualizations) **must** follow this design system. No exceptions.

---

## Color Palette — NAVIS Dark Theme

### Primary Colors

| Token | Hex | Usage |
|-------|-----|-------|
| `--navis-bg-primary` | `#0a0e17` | Main background (deepest layer) |
| `--navis-bg-secondary` | `#111827` | Cards, panels, sidebars |
| `--navis-bg-tertiary` | `#1e293b` | Elevated surfaces, modals |
| `--navis-bg-hover` | `#263245` | Hover states on surfaces |

### Accent Colors

| Token | Hex | Usage |
|-------|-----|-------|
| `--navis-accent-primary` | `#3b82f6` | Primary buttons, active states, links |
| `--navis-accent-secondary` | `#8b5cf6` | Secondary highlights, AI/perception elements |
| `--navis-accent-success` | `#22c55e` | Success states, goal reached, healthy status |
| `--navis-accent-warning` | `#f59e0b` | Warnings, caution zones, medium confidence |
| `--navis-accent-danger` | `#ef4444` | Errors, collisions, critical alerts |
| `--navis-accent-cyan` | `#06b6d4` | LiDAR visualization, sensor data |

### Text Colors

| Token | Hex | Usage |
|-------|-----|-------|
| `--navis-text-primary` | `#f1f5f9` | Primary text, headings |
| `--navis-text-secondary` | `#94a3b8` | Secondary text, labels, descriptions |
| `--navis-text-muted` | `#64748b` | Disabled text, timestamps, hints |

### Gradients

| Token | Value | Usage |
|-------|-------|-------|
| `--navis-gradient-primary` | `linear-gradient(135deg, #3b82f6, #8b5cf6)` | Primary action buttons, hero elements |
| `--navis-gradient-dark` | `linear-gradient(180deg, #0a0e17, #111827)` | Page backgrounds |
| `--navis-gradient-card` | `linear-gradient(135deg, #111827, #1e293b)` | Card backgrounds |

### Borders & Shadows

| Token | Value | Usage |
|-------|-------|-------|
| `--navis-border` | `1px solid rgba(255, 255, 255, 0.08)` | Card borders, dividers |
| `--navis-border-active` | `1px solid #3b82f6` | Active/focused elements |
| `--navis-shadow-sm` | `0 2px 8px rgba(0, 0, 0, 0.3)` | Subtle elevation |
| `--navis-shadow-lg` | `0 8px 32px rgba(0, 0, 0, 0.5)` | Modals, dropdowns |
| `--navis-glow-blue` | `0 0 20px rgba(59, 130, 246, 0.3)` | Active panel glow |
| `--navis-glow-purple` | `0 0 20px rgba(139, 92, 246, 0.3)` | AI-related element glow |

---

## Typography

| Element | Font | Size | Weight |
|---------|------|------|--------|
| Headings (h1–h3) | `'Inter', sans-serif` | 24–32px | 700 |
| Subheadings (h4–h6) | `'Inter', sans-serif` | 16–20px | 600 |
| Body text | `'Inter', sans-serif` | 14px | 400 |
| Labels / captions | `'Inter', sans-serif` | 12px | 500 |
| Monospace / data | `'JetBrains Mono', monospace` | 13px | 400 |
| Dashboard numbers | `'JetBrains Mono', monospace` | 18–24px | 600 |

**Import in CSS:**
```css
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');
```

---

## Strict Design Rules

1. **Always use dark theme.** No light mode unless explicitly requested by the human.
2. **Use only the colors defined above.** Do not introduce new colors without human approval.
3. **Use CSS custom properties** (`var(--navis-bg-primary)`) — never hardcode hex values in component styles.
4. **Cards must have:** `border-radius: 12px`, the `--navis-border` border, and `--navis-bg-secondary` background.
5. **Buttons must have:** `border-radius: 8px`, smooth hover transitions (`transition: all 0.2s ease`).
6. **Status indicators:** Green = success/healthy, Amber = warning, Red = error/collision, Cyan = sensor data, Purple = AI/perception.
7. **Animations:** Use subtle micro-animations only. Max `300ms` duration. Use `ease` or `ease-out` timing. No bouncy or attention-grabbing animations.
8. **Glassmorphism** is allowed on overlays/modals: `backdrop-filter: blur(12px); background: rgba(17, 24, 39, 0.8);`
9. **Charts and data visualizations** must use the accent color palette — never default chart library colors.
10. **Loading states** must use a skeleton shimmer effect with `--navis-bg-tertiary` → `--navis-bg-hover` gradient animation.

---

## Component Semantic Colors

| Context | Background | Border Accent | Text |
|---------|-----------|---------------|------|
| Robot position | `--navis-accent-primary` | — | white |
| YOLO detection boxes | `--navis-accent-secondary` | — | white |
| Navigation path | `--navis-accent-success` | — | — |
| Obstacle zones | `--navis-accent-danger` | — | — |
| LiDAR points | `--navis-accent-cyan` | — | — |
| Sensor data cards | `--navis-bg-secondary` | `--navis-accent-cyan` | `--navis-text-primary` |
| AI metrics cards | `--navis-bg-secondary` | `--navis-accent-secondary` | `--navis-text-primary` |
| Mission status (active) | `--navis-bg-secondary` | `--navis-accent-success` | `--navis-text-primary` |
| Mission status (failed) | `--navis-bg-secondary` | `--navis-accent-danger` | `--navis-text-primary` |
