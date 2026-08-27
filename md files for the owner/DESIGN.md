---
name: "{{PROJECT_NAME}}"
version: "1.0"
status: "draft"
interface_type: "{{web-app | dashboard | marketing-site | mobile-app | desktop-app}}"
visual_direction:
  mood: []
  density: "moderate"
  theme: "{{light | dark | adaptive}}"
colors:
  primary: "{{PRIMARY_COLOR}}"
  secondary: "{{SECONDARY_COLOR}}"
  background: "{{BACKGROUND_COLOR}}"
  surface: "{{SURFACE_COLOR}}"
  surface_elevated: "{{SURFACE_ELEVATED_COLOR}}"
  border: "{{BORDER_COLOR}}"
  text_primary: "{{TEXT_PRIMARY_COLOR}}"
  text_secondary: "{{TEXT_SECONDARY_COLOR}}"
  success: "{{SUCCESS_COLOR}}"
  warning: "{{WARNING_COLOR}}"
  danger: "{{DANGER_COLOR}}"
typography:
  display: "{{DISPLAY_FONT}}"
  body: "{{BODY_FONT}}"
  mono: "{{MONOSPACE_FONT_OR_NONE}}"
spacing:
  unit: "{{BASE_SPACING_UNIT}}"
rounded:
  sm: "{{SMALL_RADIUS}}"
  md: "{{MEDIUM_RADIUS}}"
  lg: "{{LARGE_RADIUS}}"
---

# Design Specification

## Purpose

This file is the project's **source of truth for visual and interaction design**.

It should be self-contained enough that an agent can implement or modify the UI without repeatedly consulting the reusable design-library files.

This file is generated and refined after the project type and visual direction have been agreed with the user.

---

## 1. Product and Design Intent

**Project:** {{PROJECT_NAME}}

**Primary interface type:** {{TYPE}}

**Target users:** {{TARGET_USERS}}

**Desired visual character:**

- {{MOOD_1}}
- {{MOOD_2}}
- {{MOOD_3}}

### Design goal

{{DESCRIBE_THE_EXPERIENCE_THE_INTERFACE_SHOULD_CREATE}}

### Design priorities

1. {{PRIORITY_1}}
2. {{PRIORITY_2}}
3. {{PRIORITY_3}}

---

## 2. Visual Language

The product follows a restrained, structured interface style inspired by modern high-quality product software.

Use:

- clear hierarchy
- deliberate alignment
- consistent spacing
- restrained surfaces
- limited accent usage
- meaningful visual differentiation
- strong readability

Avoid visual noise that does not improve comprehension or interaction.

Project-specific departures from these defaults must be documented here.

---

## 3. Information Hierarchy

Define the visual priority of:

- primary actions: {{RULE}}
- primary content: {{RULE}}
- secondary content: {{RULE}}
- metadata: {{RULE}}
- status information: {{RULE}}
- destructive actions: {{RULE}}

Important information should be visually stronger because of hierarchy, not because every important element uses a bright color.

---

## 4. Layout

### Global structure

{{DESCRIBE_THE_MAIN_PAGE_OR_SCREEN_STRUCTURE}}

### Grid and alignment

{{DESCRIBE_GRID_COLUMNS_MAX_WIDTHS_ALIGNMENT_RULES}}

### Information density

{{SPARSE_MODERATE_OR_DENSE_AND_WHERE}}

### Spacing

Use the declared spacing scale consistently. Prefer a small set of repeatable spacing values rather than arbitrary one-off values.

---

## 5. Color System

### Color roles

- `primary`: {{USAGE}}
- `secondary`: {{USAGE}}
- `background`: {{USAGE}}
- `surface`: {{USAGE}}
- `surface_elevated`: {{USAGE}}
- `border`: {{USAGE}}
- `text_primary`: {{USAGE}}
- `text_secondary`: {{USAGE}}
- `success`: {{USAGE}}
- `warning`: {{USAGE}}
- `danger`: {{USAGE}}

### Rules

- Use color semantically rather than decoratively.
- Reserve strong semantic colors for meaningful states.
- Do not introduce additional accent colors without a clear reason.
- Maintain readable contrast.

---

## 6. Typography

### Font roles

- display: `{{DISPLAY_FONT}}`
- body: `{{BODY_FONT}}`
- monospace: `{{MONOSPACE_FONT_OR_NONE}}`

### Hierarchy

{{DESCRIBE_HEADING_BODY_LABEL_AND_METADATA_SCALE}}

### Technical content

{{DEFINE_WHEN_MONOSPACE_OR_TECHNICAL_STYLING_IS_USED}}

Typography should establish hierarchy before relying on color, borders, or decorative elements.

---

## 7. Shape, Borders, and Elevation

### Radius

- small: `{{SMALL_RADIUS}}`
- medium: `{{MEDIUM_RADIUS}}`
- large: `{{LARGE_RADIUS}}`

Use rounded shapes deliberately. Do not turn every control into a pill.

### Borders

{{DESCRIBE_BORDER_STRENGTH_AND_USAGE}}

### Elevation

{{DESCRIBE_WHEN_SHADOWS_OR_SURFACE_LAYERS_ARE_ALLOWED}}

Prefer subtle depth cues over heavy shadows unless the project explicitly calls for stronger elevation.

---

## 8. Navigation

{{DESCRIBE_PRIMARY_NAVIGATION_SECONDARY_NAVIGATION_BREADCRUMBS_TABS_OR_OTHER_NAVIGATION}}

Navigation should make the user's current location and available next actions clear without competing with the main content.

---

## 9. Components

Document the project's established component behavior here.

### Buttons

{{PRIMARY_SECONDARY_TERTIARY_DESTRUCTIVE_AND_SIZE_RULES}}

### Inputs

{{INPUT_APPEARANCE_STATES_AND_LABELING_RULES}}

### Cards / Panels

{{SURFACE_STRUCTURE_AND_USAGE_RULES}}

### Tables / Lists

{{DENSITY_ALIGNMENT_STATES_AND_RESPONSIVENESS_RULES}}

### Dialogs / Sheets

{{RULES}}

### Alerts / Status

{{SUCCESS_WARNING_ERROR_INFO_RULES}}

### Other project-specific components

{{ADD_ONLY_WHAT_THE_PROJECT_NEEDS}}

Reuse existing components before creating variants. New variants should have a clear semantic purpose.

---

## 10. Data Visualization

{{INCLUDE_IF_RELEVANT}}

Charts and graphs should prioritize accurate interpretation over decoration.

- keep scales truthful
- use semantic color consistently
- provide labels/tooltips where needed
- do not rely on color alone to communicate meaning
- maintain sufficient contrast

---

## 11. Interaction States

Every interactive component should have an intentional treatment for relevant states:

- default
- hover
- focus
- active/pressed
- disabled
- loading
- success
- error
- empty

Focus indicators must remain visible for keyboard users.

---

## 12. Motion

### General philosophy

{{SUBTLE_FUNCTIONAL_EXPRESSIVE_OR_OTHER}}

### Timing

{{DEFINE_PROJECT_RANGE_IF_NEEDED}}

### Rules

- Motion should communicate state, hierarchy, continuity, or feedback.
- Avoid animation that competes with the task.
- Respect reduced-motion preferences where applicable.

---

## 13. Responsive / Platform Behavior

{{DESCRIBE_BREAKPOINTS_OR_PLATFORM_RULES}}

Define how the interface changes when space, input method, or platform changes instead of simply shrinking the desktop layout.

---

## 14. Accessibility

- Do not communicate important information through color alone.
- Preserve visible keyboard focus.
- Use semantic structure and accessible labels.
- Maintain readable contrast.
- Provide appropriate states for loading, errors, and disabled controls.
- Support reduced motion where applicable.

Project-specific accessibility requirements:

{{RULES}}

---

## 15. Visual References

Use references to communicate direction, not to copy another product's branding or implementation.

### References

- {{REFERENCE_1}} — {{WHAT_TO_LEARN_FROM_IT}}
- {{REFERENCE_2}} — {{WHAT_TO_LEARN_FROM_IT}}

### Local reference assets

{{LIST_REPOSITORY_REFERENCE_IMAGES_OR_DESIGNS}}

---

## 16. Do

- maintain hierarchy
- reuse established components
- keep spacing consistent
- use color semantically
- preserve platform-appropriate behavior
- keep visual noise controlled
- use design decisions that support the product's actual purpose

---

## 17. Don't

- don't introduce random colors
- don't create unnecessary component variants
- don't make every section a floating card
- don't use decorative gradients without a documented reason
- don't overuse shadows or rounded pills
- don't copy another product's branding
- don't sacrifice usability for visual novelty

Project-specific prohibitions:

- {{DON_T_1}}
- {{DON_T_2}}

---

## 18. Change Rules

When a design decision changes across the application, update this file first and then update the affected implementation.

When a change is isolated to one component or page, document it here only if it represents a durable design-system rule.

Keep this file current. It should describe the intended current state of the interface, not a history of previous designs.
