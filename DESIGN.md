---
name: API Key Management Platform
colors:
  surface: '#131313'
  surface-dim: '#131313'
  surface-bright: '#3a3939'
  surface-container-lowest: '#0e0e0e'
  surface-container-low: '#1c1b1b'
  surface-container: '#201f1f'
  surface-container-high: '#2a2a2a'
  surface-container-highest: '#353534'
  on-surface: '#e5e2e1'
  on-surface-variant: '#c4c7c8'
  inverse-surface: '#e5e2e1'
  inverse-on-surface: '#313030'
  outline: '#8e9192'
  outline-variant: '#444748'
  surface-tint: '#c6c6c7'
  primary: '#ffffff'
  on-primary: '#2f3131'
  primary-container: '#e2e2e2'
  on-primary-container: '#636565'
  inverse-primary: '#5d5f5f'
  secondary: '#adc6ff'
  on-secondary: '#002e6a'
  secondary-container: '#0566d9'
  on-secondary-container: '#e6ecff'
  tertiary: '#ffffff'
  on-tertiary: '#003824'
  tertiary-container: '#6ffbbe'
  on-tertiary-container: '#00734e'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#e2e2e2'
  primary-fixed-dim: '#c6c6c7'
  on-primary-fixed: '#1a1c1c'
  on-primary-fixed-variant: '#454747'
  secondary-fixed: '#d8e2ff'
  secondary-fixed-dim: '#adc6ff'
  on-secondary-fixed: '#001a42'
  on-secondary-fixed-variant: '#004395'
  tertiary-fixed: '#6ffbbe'
  tertiary-fixed-dim: '#4edea3'
  on-tertiary-fixed: '#002113'
  on-tertiary-fixed-variant: '#005236'
  background: '#131313'
  on-background: '#e5e2e1'
  surface-variant: '#353534'
typography:
  display-lg:
    fontFamily: Geist
    fontSize: 48px
    fontWeight: '700'
    lineHeight: '1.1'
    letterSpacing: -0.04em
  headline-md:
    fontFamily: Geist
    fontSize: 32px
    fontWeight: '600'
    lineHeight: '1.2'
    letterSpacing: -0.02em
  headline-sm:
    fontFamily: Geist
    fontSize: 24px
    fontWeight: '600'
    lineHeight: '1.3'
  body-lg:
    fontFamily: Geist
    fontSize: 18px
    fontWeight: '400'
    lineHeight: '1.6'
  body-md:
    fontFamily: Geist
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.6'
  code-md:
    fontFamily: JetBrains Mono
    fontSize: 14px
    fontWeight: '400'
    lineHeight: '1.5'
  label-sm:
    fontFamily: JetBrains Mono
    fontSize: 12px
    fontWeight: '500'
    lineHeight: '1'
    letterSpacing: 0.05em
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  unit: 4px
  container-padding: 24px
  gutter: 16px
  stack-gap-sm: 8px
  stack-gap-md: 16px
  stack-gap-lg: 32px
---

## Brand & Style
The design system is engineered for a high-end developer tool aesthetic, prioritizing speed, security, and clarity. The personality is **minimalist and robust**, stripping away unnecessary decorative elements to focus on technical utility.

The visual style is a fusion of **Modern Minimalism** and **Glassmorphism**, specifically tailored for a deep dark mode environment. It utilizes high-contrast typography against a rich black canvas to evoke a premium, "pro-tier" feel. Surface depth is achieved through subtle translucent layers and hairline borders rather than heavy shadows, creating a UI that feels lightweight yet structurally sound. The emotional response should be one of absolute reliability and "invisible" efficiency.

## Colors
The palette is built on a "Deep Dark" foundation to reduce eye strain during long coding sessions.

*   **Primary (#FFFFFF):** Reserved for high-priority text, icons, and primary action states.
*   **Secondary (#3B82F6):** "Electric Blue" used for interactive focus states, primary buttons, and branding accents to signify trust and connectivity.
*   **Tertiary (#10B981):** "Emerald" strictly for success states, active API keys, and healthy system status.
*   **Base (#0A0A0A):** The background layer for the entire application.
*   **Surface (#141414):** Elevated containers and cards.
*   **Border (#1F1F1F):** Hairline strokes used to define structure without adding visual noise.

## Typography
The typography strategy distinguishes between "UI Navigation" and "Data/Technical Content." 

**Geist** is used for all interface elements, headings, and body copy to provide a clean, neo-grotesque feel that scales perfectly. **JetBrains Mono** is utilized for API keys, code snippets, logs, and technical labels to ensure character distinguishability (e.g., 0 vs O) and to reinforce the developer-first nature of this design system. Use `tight` letter-spacing on larger headings to maintain a premium, editorial look.

## Layout & Spacing
This design system employs a **fixed-fluid hybrid grid**. Main dashboard content is contained within a 1280px max-width container, while internal sidebars and code-panels use fluid widths to maximize horizontal space for long strings of code.

Spacing follows a strict 4px base unit. Component grouping should be tight (8px-12px) to signify relationship, while section-level margins should be generous (48px-64px) to create an airy, high-end feel. For the "3 lines of code" value proposition, use a centered, focused layout to minimize distraction and emphasize the ease of integration.

## Elevation & Depth
Elevation is expressed through **Tonal Layering** and **Glassmorphism** rather than traditional shadows.

1.  **Level 0 (Base):** #0A0A0A (Pure background).
2.  **Level 1 (Cards/Panels):** #141414 with a 1px solid border of #1F1F1F.
3.  **Level 2 (Modals/Popovers):** #1A1A1A with a subtle backdrop-blur (12px) and a light-tinted top border (0.5px white at 10% opacity) to simulate a light source from above.

Shadows, when used (e.g., on primary buttons), should be high-blur and low-opacity, using the button's accent color (blue or green) to create a soft "glow" effect rather than a physical shadow.

## Shapes
The shape language is **Soft yet Precise**. 

Small components like buttons and input fields use a `0.25rem` (4px) radius. Larger containers like code blocks and dashboard cards use a `0.5rem` (8px) radius. This conservative rounding maintains the "professional tool" aesthetic, avoiding the overly-playful look of highly rounded "consumer" apps while feeling more modern than sharp-edged legacy software.

## Components
*   **Buttons:** Primary buttons use a solid White background with Black text for maximum impact. Secondary buttons are Ghost-style with #1F1F1F borders and subtle hover states (#2A2A2A).
*   **Code Blocks:** Use #000000 (Pure Black) background with a #1F1F1F border. Add a "Copy" button in the top right that appears on hover.
*   **API Key Display:** Rendered in `code-md` (JetBrains Mono). Use a "masked" state by default, revealing the key only on explicit user click.
*   **Status Badges:** Small, pill-shaped chips. "Active" uses a 10% opacity Emerald background with a solid Emerald dot and text.
*   **Input Fields:** Minimalist design with only a bottom border or a subtle 1px frame. Focus state shifts the border color to Electric Blue with a 1px outer glow.
*   **One-Time Payment Card:** A featured card with a slightly thicker border (2px) using a gradient from #3B82F6 to #10B981 to draw the eye to the primary value prop.