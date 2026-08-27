---
name: "Web Application Design Archetype"
version: "1.0"
---

# Web Application Archetype

Use this file for interactive web products such as SaaS applications, developer tools, admin systems, productivity applications, and authenticated product interfaces.

Combine with `BASE.md` when generating the project's root `DESIGN.md`.

---

## 1. Application Shell

Treat the application shell as a persistent hierarchy rather than a decorative frame.

Typical structure:

- workspace/navigation context
- primary navigation
- page or view header
- main content area
- contextual actions or secondary panels

Keep the primary content visually stronger than global navigation.

---

## 2. Navigation

Navigation should make three questions easy to answer:

- Where am I?
- What can I do next?
- Where can I go from here?

Use clear active states.

Keep navigation compact and consistent across views.

Use breadcrumbs, tabs, secondary navigation, or contextual navigation only when they improve orientation.

---

## 3. Page Headers

A page header should establish:

- current location/title
- short contextual description when needed
- primary action(s)
- relevant filters or view controls

Avoid oversized hero-style headers inside product applications unless the product genuinely benefits from them.

---

## 4. CRUD and Forms

Forms should prioritize clarity and task completion.

- group related fields
- use explicit labels
- keep destructive actions visually distinct
- preserve input state on recoverable errors
- provide clear validation feedback
- avoid unnecessary wizard steps

For dense admin interfaces, use predictable alignment and compact but readable spacing.

---

## 5. Tables and Lists

When displaying collections:

- prioritize the fields users actually need
- keep columns aligned
- distinguish primary information from metadata
- provide useful empty/loading/error states
- support responsive alternatives when appropriate

Do not squeeze a desktop table into unreadable mobile widths.

---

## 6. Detail Views

Detail screens should establish a clear primary object and then group secondary information around it.

Prefer:

- clear title/identity
- primary actions near identity
- related metadata grouped predictably
- sections that can be scanned quickly

---

## 7. Search, Filter, and Command Patterns

Search and filtering should be easy to discover and quick to use.

For products where frequent navigation or action execution matters, command-palette patterns may be useful.

Keyboard interaction should complement, not replace, visible controls.

---

## 8. Responsive Behavior

On smaller screens:

- reduce secondary chrome
- collapse global navigation appropriately
- prioritize primary actions
- reorganize dense controls instead of simply shrinking them
- stack or transform multi-column layouts when necessary

Do not assume every desktop interaction pattern maps directly to touch.

---

## 9. Product Feel

The default web-app feel should be:

- efficient
- structured
- responsive
- low-noise
- trustworthy

Polish should come from interaction quality, not decorative effects.
