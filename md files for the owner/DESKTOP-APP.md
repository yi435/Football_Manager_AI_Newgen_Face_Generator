---
name: "Desktop Application Design Archetype"
version: "1.0"
---

# Desktop Application Archetype

Use this file for desktop software such as developer tools, editors, administration tools, productivity applications, creative tools, monitoring clients, and other applications designed primarily for resizable desktop windows.

Combine with `BASE.md` when generating the project's root `DESIGN.md`.

---

## 1. Desktop as a Workspace

Treat the application as a persistent workspace rather than a sequence of isolated pages.

The interface should support:

- sustained use
- multitasking within the application
- dense information when appropriate
- keyboard and pointer interaction
- resizable layouts
- persistent context

---

## 2. Window and Shell Structure

The shell may include:

- window/menu area where appropriate
- primary navigation
- secondary navigation or tool panels
- main workspace
- inspectors or contextual side panels
- status area

Do not add faux window chrome if the platform already provides native window controls unless the project's product design deliberately requires custom chrome.

---

## 3. Resizable Layouts

Important panels should respond deliberately to resizing.

Define:

- minimum useful widths
- collapsible panels
- split views
- overflow behavior
- what disappears or becomes secondary at smaller window sizes

Do not let important content become unreadable simply because the window is narrower.

---

## 4. Keyboard and Pointer

Desktop products should take advantage of both keyboard and pointer input where useful.

Consider:

- keyboard shortcuts for frequent actions
- command palettes for dense products
- visible menus and controls for discoverability
- focus management
- predictable tab order

Do not hide essential functionality behind shortcuts alone.

---

## 5. Dense Workspaces

For tools used for extended sessions, prefer stable visual locations for frequently used controls.

Panels should remain visually quiet so the workspace can hold significant information without becoming tiring.

---

## 6. Toolbars and Contextual Controls

Toolbars should contain related actions and maintain predictable ordering.

Separate primary actions from destructive or infrequent actions.

Avoid turning every toolbar into a row of equally prominent buttons.

---

## 7. Tabs and Multiple Contexts

When the product supports multiple open contexts, use tabs, documents, workspaces, or panes consistently.

The active context should be obvious without relying on color alone.

---

## 8. Context Panels and Inspectors

Side inspectors can provide detail without replacing the primary workspace.

Use them for:

- properties
- settings
- object details
- secondary actions

Avoid forcing the user to leave the main workspace for information that can be shown contextually.

---

## 9. Native vs Cross-Platform Behavior

Follow the project's actual platform strategy.

Do not imitate platform-specific controls merely for appearance.

When platform-specific behavior improves usability or accessibility, document the difference in the project's root `DESIGN.md`.

---

## 10. Motion and Feedback

Desktop motion should usually be subtle and quick.

Use clear hover, focus, selection, and active states.

For long-running operations, communicate progress without blocking the entire workspace unnecessarily.
