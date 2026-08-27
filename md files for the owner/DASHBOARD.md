---
name: "Dashboard Design Archetype"
version: "1.0"
---

# Dashboard Archetype

Use this file for data-heavy monitoring, analytics, operations, cybersecurity, finance, observability, and management interfaces.

Combine with `BASE.md` when generating the project's root `DESIGN.md`.

---

## 1. Dashboard Goal

A dashboard is a decision interface, not a collage of charts.

The first viewport should make the most important state, trends, warnings, or actions easy to understand.

Every panel should answer a useful question or support a decision.

---

## 2. Hierarchy

Establish a clear hierarchy such as:

1. global context
2. critical state / key metrics
3. major trends
4. detailed breakdowns
5. secondary or historical information

Do not make every metric equally visually prominent.

---

## 3. Density

Default toward high useful density while maintaining scanability.

Use:

- compact headers
- aligned metric groups
- consistent panel padding
- restrained whitespace
- predictable grouping

Avoid large decorative hero blocks that consume valuable dashboard space.

---

## 4. Panels and Cards

Panels should organize information rather than merely decorate it.

Use consistent:

- title placement
- padding
- border treatment
- action placement
- loading/empty/error states

Avoid deeply nesting cards inside cards without a clear hierarchy.

---

## 5. Metrics

A metric should communicate:

- what it measures
- the current value
- the relevant time/context
- change or trend when useful

Use secondary information carefully; the primary value should remain immediately scannable.

---

## 6. Charts

Choose charts based on the question being answered.

Prefer straightforward visualizations over ornamental ones.

Common patterns:

- line/area → trends over time
- bar → comparison
- stacked bar → composition
- table → precise values
- heatmap → distribution across two dimensions

Do not use a chart merely because data exists.

---

## 7. Status and Alerts

Status colors should have stable meanings across the entire application.

Typical semantics:

- green → healthy / successful
- amber → warning / attention
- red → critical / error / destructive
- neutral → informational / inactive

Do not overload the dashboard with alert colors.

Critical states should be visually noticeable without making the entire interface visually aggressive.

---

## 8. Filters and Controls

Keep the filtering model close to the content it controls.

Prefer:

- concise filter groups
- predictable date/time controls
- saved views when justified
- clearly visible active filters
- easy reset behavior

Do not bury primary filtering behind unnecessary layers of interaction.

---

## 9. Navigation and Views

When multiple views exist, maintain consistent hierarchy across:

- overview
- list/table
- board
- timeline
- detail
- split view

Changing representation should not feel like entering a completely different product.

---

## 10. Responsive Behavior

On small screens:

- prioritize the most important metrics
- reorder panels by importance
- collapse secondary controls
- allow tables to scroll or transform when needed
- preserve the meaning of charts rather than shrinking them until unreadable

A mobile dashboard is a different information-prioritization problem, not simply a smaller desktop dashboard.
