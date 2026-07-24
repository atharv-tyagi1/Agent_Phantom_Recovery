---
name: Phantom Protocol
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
  on-surface-variant: '#d7c4ac'
  inverse-surface: '#e5e2e1'
  inverse-on-surface: '#313030'
  outline: '#9f8e78'
  outline-variant: '#524533'
  surface-tint: '#ffba43'
  primary: '#ffd597'
  on-primary: '#432c00'
  primary-container: '#ffb000'
  on-primary-container: '#6a4700'
  inverse-primary: '#805600'
  secondary: '#adc6ff'
  on-secondary: '#002e69'
  secondary-container: '#4b8eff'
  on-secondary-container: '#00285c'
  tertiary: '#67f4b7'
  on-tertiary: '#003824'
  tertiary-container: '#45d79c'
  on-tertiary-container: '#00593c'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#ffddaf'
  primary-fixed-dim: '#ffba43'
  on-primary-fixed: '#281800'
  on-primary-fixed-variant: '#614000'
  secondary-fixed: '#d8e2ff'
  secondary-fixed-dim: '#adc6ff'
  on-secondary-fixed: '#001a41'
  on-secondary-fixed-variant: '#004493'
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
    fontWeight: '600'
    lineHeight: '1.1'
    letterSpacing: -0.04em
  headline-lg:
    fontFamily: Geist
    fontSize: 32px
    fontWeight: '600'
    lineHeight: '1.2'
    letterSpacing: -0.02em
  headline-lg-mobile:
    fontFamily: Geist
    fontSize: 24px
    fontWeight: '600'
    lineHeight: '1.2'
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Geist
    fontSize: 20px
    fontWeight: '500'
    lineHeight: '1.4'
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.6'
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: '1.5'
  mono-label:
    fontFamily: JetBrains Mono
    fontSize: 12px
    fontWeight: '500'
    lineHeight: '1.2'
    letterSpacing: 0.05em
  mono-data:
    fontFamily: JetBrains Mono
    fontSize: 13px
    fontWeight: '400'
    lineHeight: '1.4'
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  unit: 4px
  container-max: 1440px
  gutter: 24px
  margin-desktop: 40px
  margin-mobile: 16px
  stack-xs: 4px
  stack-sm: 8px
  stack-md: 16px
  stack-lg: 32px
---

## Brand & Style
The design system is engineered for high-stakes autonomous security and engineering environments. It evokes the feeling of a "Mission Control" interface—quiet, powerful, and hyper-precise. The brand personality is authoritative and technical, prioritizing data density without sacrificing aesthetic clarity.

The visual style merges **Minimalism** with **Glassmorphism**. It utilizes a "Dark Mode First" philosophy, leaning on obsidian surfaces and high-frequency telemetry accents. The interface should feel like a sophisticated physical console translated into a digital space, employing subtle glowing states and sharp architectural lines to guide the eye through complex security workflows.

## Colors
The palette is dominated by **Obsidian (#0A0A0A)** and **Deep Slate**, providing a low-fatigue backdrop for prolonged technical monitoring. 

- **Neon Amber (#FFB000)**: Used exclusively for primary actions, critical alerts, and active "Phantom" agent states. It represents the "energy" of the system.
- **Electric Blue (#007AFF)**: Applied to secondary telemetry, data visualizations, and non-critical system updates.
- **Emerald (#10B981)**: Dedicated to success states, secure protocols, and healthy system pulses.
- **Surface & Borders**: Backgrounds use a tiered dark hierarchy. Borders are kept thin and low-contrast (#262626) to maintain a seamless, "infinite" feel.

## Typography
The typography strategy differentiates between "Narrative" and "Technical" content. 

- **Headlines (Geist)**: Use a sharp, tight-kerning sans-serif for headers to create a modern, architectural feel.
- **Body (Inter)**: Maintains high readability for long-form security logs and documentation.
- **Technical/Labels (JetBrains Mono)**: All system-generated data, IDs, timestamps, and status labels must use the monospaced font. This reinforces the "engineering-first" nature of the platform. Labels should frequently use `uppercase` with increased letter-spacing to denote secondary system information.

## Layout & Spacing
This design system utilizes a **Fixed Grid** for main content areas to maintain precision, while sidebars and telemetry panels follow a fluid model. 

- **Grid**: A 12-column grid system is used for the main dashboard. 
- **Density**: The layout is high-density. Information is packed tightly using a 4px base unit, but "breathing room" is created via generous outer margins (40px) to prevent the UI from feeling claustrophobic.
- **Mobile**: On mobile devices, the 12-column grid collapses into a single-column stack. Sidebar elements move into a bottom-sheet or a full-screen "Command Center" overlay.

## Elevation & Depth
Depth is created through **Glassmorphism** and **Tonal Layering** rather than traditional drop shadows.

- **Panels**: Use a semi-transparent background (`rgba(22, 22, 22, 0.7)`) with a `20px` backdrop-blur.
- **Borders**: Elements are defined by 1px solid borders. For elevated components (like modals), use a dual border: a dark outer border and a faint 1px inner highlight on the top edge to simulate light hitting a physical edge.
- **Glows**: High-priority elements (Active Agents, Critical Alerts) use an ambient glow—a soft, low-opacity shadow tinted with the component's accent color (e.g., a `0 0 15px rgba(255, 176, 0, 0.2)` glow for Amber buttons).

## Shapes
The shape language is **Soft (0.25rem)**. While the system is "sharp" and technical, slight rounding on corners prevents the UI from feeling "primitive" or "brutalist." 

- Small components (Buttons, Inputs, Chips) use a **4px (0.25rem)** radius.
- Larger containers (Cards, Glass Panels) use **8px (0.5rem)**.
- Specialized telemetry dots or status indicators remain perfectly square or circular to denote mathematical precision.

## Components
- **Buttons**: Primary buttons are solid Neon Amber with black text. Secondary buttons use a ghost style: a 1px border with Electric Blue text that gains a subtle glow on hover.
- **Inputs**: Field backgrounds are deeper than the page background (#050505). Focus states trigger a 1px Neon Amber border and a faint outer glow.
- **Glass Panels**: Used for sidebars and floating menus. Always include a 1px semi-transparent border to ensure separation from the background.
- **Telemetry Chips**: Small, monospaced labels with a background tint corresponding to the status (e.g., Emerald tint for "System Nominal").
- **Activity Feed**: A vertical list of monospaced logs. Highlighting an entry should use a subtle Electric Blue left-border accent.
- **Command Palette**: A central, high-elevation modal with high backdrop-blur, used for quick-searching agents or security protocols.