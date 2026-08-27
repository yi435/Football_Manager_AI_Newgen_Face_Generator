---
name: "Mobile Application Design Archetype"
version: "1.0"
---

# Mobile Application Archetype

Use this file for native or cross-platform mobile applications designed primarily for touch devices.

Combine with `BASE.md` when generating the project's root `DESIGN.md`.

---

## 1. Touch-First Thinking

Design for touch as a primary input method.

Controls should have comfortable touch targets and sufficient spacing to reduce accidental activation.

Do not shrink desktop controls simply to make them fit a mobile screen.

---

## 2. Navigation

Use mobile-appropriate navigation patterns such as:

- bottom navigation
- navigation stacks
- drawers where justified
- tabs for closely related peer views

Do not copy a desktop sidebar into a phone interface unless it genuinely improves the product.

---

## 3. Screen Hierarchy

Each screen should have one dominant purpose.

Prioritize:

1. current context
2. primary content
3. primary action
4. supporting information
5. secondary actions

---

## 4. Forms and Input

Minimize unnecessary typing.

Use appropriate input types, pickers, selectors, autofill-friendly patterns, and clear validation.

Keep error messages near the relevant control.

---

## 5. Sheets, Dialogs, and Overlays

Use bottom sheets, dialogs, and menus according to platform conventions and task importance.

Avoid stacking multiple overlays unless the interaction genuinely requires it.

---

## 6. Gestures

Gestures may complement visible controls, but essential actions should not depend solely on hidden gestures.

Where gesture behavior exists, make its result predictable and recoverable.

---

## 7. Platform Behavior

Respect platform conventions for navigation, keyboard/input behavior, system prompts, permissions, and accessibility where appropriate.

If the application targets both iOS and Android, document intentional differences rather than pretending the platforms behave identically.

---

## 8. Responsive and Orientation Behavior

Define behavior for:

- compact phones
- large phones
- portrait
- landscape when supported
- keyboards or system overlays where relevant

Do not assume one fixed viewport size.

---

## 9. Motion and Feedback

Use fast, clear feedback for touch interactions.

Motion should communicate state changes and spatial relationships without delaying the user's task.

Respect platform reduced-motion settings.
