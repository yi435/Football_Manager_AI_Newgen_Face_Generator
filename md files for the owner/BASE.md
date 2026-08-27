---
name: "Base Product Interface Design"
version: "1.0"
source: "Personal reusable design foundation"
---

# Base Design Foundation

This file is the reusable visual philosophy for the user's projects. It should be combined with exactly the relevant project-type archetype when creating a project's root `DESIGN.md`.

It is intentionally broad enough to work across applications, dashboards, websites, and native/desktop interfaces.

---

## 1. Core Philosophy

Prefer interfaces that feel:

- precise
- intentional
- calm
- structured
- modern
- visually restrained
- information-efficient

The design should feel polished because of hierarchy, spacing, typography, alignment, interaction quality, and consistency—not because of decorative effects.

The primary visual inspiration is the class of high-quality modern product interfaces exemplified by Linear and similar product-focused software: strong hierarchy, useful density, quiet surfaces, subtle depth, deliberate spacing, and minimal visual noise.

Do not clone another product's branding, exact visual identity, or distinctive assets.

---

## 2. Hierarchy First

Use the following order of priority when making visual decisions:

1. task clarity
2. information hierarchy
3. navigation/orientation
4. interaction clarity
5. accessibility/readability
6. visual polish
7. decoration

A visual effect that reduces clarity is not a successful design choice.

Use size, weight, spacing, alignment, grouping, and surface differentiation before relying heavily on color.

---

## 3. Information Density

Default toward **moderate-to-high useful density** for product interfaces.

Do not add large empty areas merely to make a page look spacious.

Use whitespace to separate ideas and establish hierarchy, not to inflate layouts.

The appropriate density depends on the project archetype. Marketing websites may use more breathing room; dashboards may use substantially more information per viewport.

---

## 4. Layout Principles

- Prefer strong alignment and repeatable grids.
- Keep primary content visually dominant.
- Group related controls and information.
- Avoid arbitrary offsets and one-off positioning.
- Let layout communicate hierarchy.
- Keep repeated structures visually consistent.
- Avoid nested containers when they do not communicate hierarchy.

When a layout becomes complex, simplify the hierarchy before adding decorative treatment.

---

## 5. Surfaces

Use a restrained surface system.

Typical layers are:

1. application/page background
2. primary content surface
3. elevated or selected surface
4. overlay/modal surface

Prefer subtle tonal differences and borders over dramatic shadows.

Do not make every component look like a floating card.

---

## 6. Color Philosophy

Use a neutral foundation with a small number of deliberate accents.

### Rules

- one primary interaction/brand accent by default
- semantic colors for success, warning, and danger
- strong semantic colors should communicate meaning, not decoration
- use neutral colors for most structure
- do not introduce new accents simply because a section needs visual variety

Gradients may be used only when they have a clear design purpose and are consistent with the project's established visual language. They are not a default decoration.

---

## 7. Typography

Typography should do most of the work of establishing hierarchy.

Prefer:

- a strong heading hierarchy
- highly readable body text
- clear labels and metadata
- restrained use of bold/semibold weights
- monospace only where technical or code-like content benefits from it

Avoid excessive font-size variation.

Use one coherent typographic system rather than styling every block independently.

---

## 8. Spacing

Use a compact spacing scale with a consistent rhythm.

Prefer a small reusable set such as:

- 4
- 8
- 12
- 16
- 24
- 32
- 48
- 64

The exact values may be adjusted for the project, but arbitrary values should not become the norm.

---

## 9. Shape

Use restrained rounding.

Default direction:

- controls: small-to-medium radius
- cards/panels: medium radius
- large containers: medium-to-large radius
- pills: reserved for tags, statuses, filters, or deliberate compact controls

Avoid making the interface look inflated by rounding every element heavily.

---

## 10. Borders and Depth

Prefer thin, subtle borders where structure needs clarification.

Use shadows sparingly.

Depth should communicate:

- hierarchy
- overlay state
- interaction state
- separation from the page

Do not use strong shadows as a substitute for layout hierarchy.

---

## 11. Interaction

Interactive elements should feel responsive and predictable.

Define clear states for:

- hover
- focus
- active/pressed
- selected
- disabled
- loading
- success
- error

A component should not visually jump between states unless the transition is intentional.

---

## 12. Motion

Motion should be subtle and functional by default.

Use motion to communicate:

- state change
- spatial relationship
- progress
- feedback
- opening/closing

Avoid animation that exists only to make the interface appear busy.

Respect reduced-motion preferences where supported.

---

## 13. Icons and Imagery

Icons should be visually consistent within a project.

Prefer recognizable, simple icons over decorative symbols.

Do not use emojis as primary UI icons unless the project's design explicitly calls for an expressive style.

Illustration, photography, and other imagery should support product meaning rather than fill empty space.

---

## 14. Accessibility

Accessibility is part of the design system, not a later cleanup step.

- preserve keyboard access
- maintain visible focus
- use semantic structure
- keep sufficient contrast
- do not rely on color alone
- provide meaningful labels
- ensure states are understandable without motion

---

## 15. Responsive Thinking

Do not treat responsive behavior as simply scaling the desktop layout downward.

When the available space or input method changes, reconsider:

- navigation
- control density
- information order
- table/list behavior
- modal/sheet behavior
- touch targets
- secondary content

The relevant archetype provides the more specific rules.

---

## 16. Visual Restraint

Avoid patterns that frequently create noisy or generic AI-generated interfaces:

- excessive glassmorphism
- excessive gradients
- huge decorative blobs
- unnecessary glowing effects
- excessive shadows
- excessive pill-shaped controls
- every section becoming a floating card
- random accent colors
- oversized headings that do not serve the product
- animated decoration everywhere

The interface should feel designed, not decorated.

---

## 17. Design Decision Rule

When several visual solutions are possible, prefer the one that:

1. communicates hierarchy more clearly
2. reuses existing project patterns
3. creates less visual noise
4. improves usability
5. remains consistent across the product

---

## 18. Archetype Composition

When creating a project's root `DESIGN.md`, combine this base foundation with the selected project archetype.

The final project specification should convert these general principles into concrete values, components, states, layouts, and references specific to the project.
