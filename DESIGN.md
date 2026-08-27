---
name: "FM AI Newgen Generator"
version: "1.0"
status: "active"
interface_type: "desktop-app"
visual_direction:
  mood: ["technical", "clean", "calm", "premium"]
  density: "moderate-high"
  theme: "dark"
colors:
  primary: "#6c5ce7"
  primary_hover: "#5b4bc4"
  secondary: "#00cec9"
  background: "#121214"
  surface: "#1a1a1e"
  surface_elevated: "#222228"
  surface_input: "#26262b"
  border: "#2e2e38"
  border_focus: "#6c5ce7"
  text_primary: "#f1f1f5"
  text_secondary: "#a5a5b5"
  text_disabled: "#636375"
  success: "#00b894"
  warning: "#fdcb6e"
  danger: "#d63031"
  active: "#00cec9"
typography:
  display: "Segoe UI, -apple-system, BlinkMacSystemFont, Arial, sans-serif"
  body: "Segoe UI, -apple-system, BlinkMacSystemFont, Arial, sans-serif"
  mono: "Consolas, Cascadia Code, SF Mono, Menlo, monospace"
spacing:
  unit: 4
  xs: 4
  sm: 8
  md: 12
  lg: 16
  xl: 20
  xxl: 24
rounded:
  sm: 4
  md: 6
  lg: 8
---

# Design Specification: FM AI Newgen Generator

## 1. Product & Design Intent

**Project:** Football Manager AI Newgen Generator (`FMNewgenGenerator`)  
**Interface Type:** Desktop Application (`desktop-app`)  
**Target Users:** Football Manager simulation players and modders seeking fast, automated, photorealistic face generation with local ComfyUI.  
**Visual Character:** Calm, structured, technical, high-utility dark workspace.

### Design Priorities
1. **Task Clarity:** Export folder tracking, generation status, and real-time generation progress must be immediately visible.
2. **Context Persistence:** Settings (folders, model checkpoint, generation parameters, prompt styles) persist reliably and are editable in place.
3. **Responsive Visual Feedback:** Clear status indicators for AI engine connectivity (Online/Booting/Offline), live face preview thumbnail, batch ETA, and categorized logs.

---

## 2. Visual Tokens & Styling Rules

### Color Tokens
- `bg_dark` (`#121214`): Window background.
- `bg_panel` (`#1a1a1e`): Group containers, split cards, inspector drawers.
- `bg_elevated` (`#222228`): Modals, dropdown popups, active tabs.
- `bg_input` (`#26262b`): Text inputs, path entries, spinboxes.
- `border_subtle` (`#2e2e38`): 1px container boundaries.
- `border_accent` (`#6c5ce7`): Focused controls and primary buttons.
- `fg_light` (`#f1f1f5`): Primary text and titles.
- `fg_muted` (`#a5a5b5`): Labels, descriptions, secondary values.
- `fg_dim` (`#636375`): Inactive placeholders, disabled options.
- `accent_primary` (`#6c5ce7`): Primary actions ("Generate", "Save").
- `accent_success` (`#00b894`): Online status, completion markers.
- `accent_warning` (`#fdcb6e`): Startup/connecting states, non-fatal alerts.
- `accent_danger` (`#d63031`): Offline provider, errors, cancel triggers.
- `accent_active` (`#00cec9`): Watcher running indicator.

### Typography Rules
- **Display / App Title:** 16pt Bold (`fg_light`)
- **Section Headers:** 10.5pt Bold (`fg_light`)
- **Field Labels & Buttons:** 9pt Regular / Bold (`fg_light` or `fg_muted`)
- **Input Text:** 9pt Regular (`fg_light` on `bg_input`)
- **Captions & Metadata:** 8pt Regular (`fg_muted`)
- **Console Logs & Prompts:** 8.5pt Monospace (`mono`, `fg_light`)

---

## 3. Desktop Shell & Layout Structure

The interface uses a split desktop workspace:

```
+-----------------------------------------------------------------------------------+
|  [Logo] FM AI Newgen Generator                [● ComfyUI Connected]  [Maintenance] |
+-------------------------------------------------+---------------------------------+
|  LEFT PANE: WORKSPACE & BATCH CONTROLS          |  RIGHT PANE: LIVE PREVIEW & FEED|
|                                                 |                                 |
|  [📂 Watch Directory]   [Browse...]             |  +---------------------------+  |
|  [🖼️ Graphics Directory][Browse...]             |  |                           |  |
|                                                 |  |    [ Latest Generated ]   |  |
|  [⚡ Auto-Watch: ON/OFF]  [▶ Process Existing]  |  |    [    Face Card     ]   |  |
|                                                 |  |                           |  |
|  Batch Progress: [████████░░░░] 65% (ETA 45s)   |  +---------------------------+  |
|  Stats: 42 Generated | 8 Queued | 450 Total     |  Player: Ruben Silva (FRA, 18)  |
|                                                 |  [Open Folder] [Test Face]      |
|  [⚙️ Face Style & Tuning] [Cancel Batch]        |                                 |
+-------------------------------------------------+---------------------------------+
|  BOTTOM PANE: COLLAPSIBLE DIAGNOSTIC CONSOLE & STATUS LOGS                        |
|  [19:22:10] [Info] ComfyUI is ready — RealVisXL_V5.0_fp16.safetensors loaded.     |
|  [19:22:15] [Success] Generated UID 2000000001 (Ruben Silva) in 3.2s             |
+-----------------------------------------------------------------------------------+
```

### Layout Specs
- **Minimum Window Dimensions:** `880x680` (Resizable up to full desktop width/height).
- **Split Ratio:** ~60% Left Controls / ~40% Right Preview & Inspector.
- **Collapsible Drawer:** Diagnostic log console at bottom can toggle height.

---

## 4. Keyboard Shortcuts & Accessibility

- `Ctrl + G` or `F5`: Run Manual Batch on Existing Files.
- `Ctrl + W`: Toggle Auto-Watch Directory on/off.
- `Ctrl + T`: Generate Sample Test Face.
- `Ctrl + S`: Save Current Configuration.
- `Ctrl + E`: Open Face Style & Advanced Tuning Dialog.
- `Ctrl + L`: Clear Console Logs.
- `Esc`: Cancel Running Generation Batch / Close Modal.

---

## 5. Interaction States & Transitions

- **Hover:** Buttons shift background +10% brightness (`#34343d`).
- **Active / Pressed:** Buttons depress with primary border glow (`#6c5ce7`).
- **Disabled:** Dimmed to `fg_dim` (`#636375`) with no cursor change.
- **Thread Safety:** All UI updates from background threads (`watcher`, `generator`, `wizard`) must strictly dispatch via `root.after(0, ...)`.
