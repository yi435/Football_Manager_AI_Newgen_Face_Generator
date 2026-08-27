"""
Design system loader and token manager for FM AI Newgen Generator.
Directly parses and binds tokens from DESIGN.md into strongly-typed objects
for Tkinter widgets, ensuring the UI strictly tracks the design specification.
"""
import os
import re
from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass(frozen=True)
class ColorTokens:
    primary: str = "#6c5ce7"
    primary_hover: str = "#5b4bc4"
    secondary: str = "#00cec9"
    background: str = "#121214"
    surface: str = "#1a1a1e"
    surface_elevated: str = "#222228"
    surface_input: str = "#26262b"
    border: str = "#2e2e38"
    border_focus: str = "#6c5ce7"
    text_primary: str = "#f1f1f5"
    text_secondary: str = "#a5a5b5"
    text_disabled: str = "#636375"
    success: str = "#00b894"
    warning: str = "#fdcb6e"
    danger: str = "#d63031"
    active: str = "#00cec9"


@dataclass(frozen=True)
class TypographyTokens:
    display_family: str = "Segoe UI"
    body_family: str = "Segoe UI"
    mono_family: str = "Consolas"

    @property
    def title(self):
        return (self.display_family, 13, "bold")

    @property
    def subtitle(self):
        return (self.body_family, 8, "normal")

    @property
    def header(self):
        return (self.body_family, 10, "bold")

    @property
    def body(self):
        return (self.body_family, 9, "normal")

    @property
    def body_bold(self):
        return (self.body_family, 9, "bold")

    @property
    def small(self):
        return (self.body_family, 8, "normal")

    @property
    def small_bold(self):
        return (self.body_family, 8, "bold")

    @property
    def mono(self):
        return (self.mono_family, 8, "normal")

    @property
    def stat(self):
        return (self.body_family, 15, "bold")


@dataclass(frozen=True)
class SpacingTokens:
    unit: int = 4
    xs: int = 4
    sm: int = 8
    md: int = 12
    lg: int = 16
    xl: int = 20
    xxl: int = 24


@dataclass
class DesignTokens:
    name: str = "FM AI Newgen Generator"
    interface_type: str = "desktop-app"
    theme: str = "dark"
    colors: ColorTokens = field(default_factory=ColorTokens)
    fonts: TypographyTokens = field(default_factory=TypographyTokens)
    spacing: SpacingTokens = field(default_factory=SpacingTokens)

    @classmethod
    def load(cls, search_paths=None):
        """
        Loads design tokens by scanning for DESIGN.md and parsing its YAML frontmatter.
        Falls back cleanly to built-in DESIGN.md defaults if file is missing.
        """
        if search_paths is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            search_paths = [
                os.path.join(base_dir, "DESIGN.md"),
                os.path.join(base_dir, "md files for the owner", "DESIGN.md"),
            ]

        raw_content = ""
        for path in search_paths:
            if os.path.isfile(path):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        raw_content = f.read()
                    break
                except Exception:
                    continue

        if not raw_content:
            return cls()

        # Parse YAML frontmatter between --- markers
        fm_match = re.search(r"^---\s*\n(.*?)\n---", raw_content, re.DOTALL)
        if not fm_match:
            return cls()

        fm_text = fm_match.group(1)
        colors_dict = {}
        typography_dict = {}
        spacing_dict = {}
        current_section = None

        for line in fm_text.splitlines():
            line_str = line.strip()
            if not line_str or line_str.startswith("#"):
                continue

            # Check section header
            if line_str.endswith(":") and not line_str.startswith("-"):
                current_section = line_str[:-1].strip()
                continue

            if ":" in line_str:
                k, v = line_str.split(":", 1)
                k = k.strip()
                v = v.strip().strip('"').strip("'")
                
                # Convert numbers
                if v.isdigit():
                    v_val = int(v)
                else:
                    v_val = v

                if current_section == "colors":
                    colors_dict[k] = v_val
                elif current_section == "typography":
                    typography_dict[k] = v_val
                elif current_section == "spacing":
                    spacing_dict[k] = v_val

        # Construct token objects
        colors = ColorTokens(
            primary=colors_dict.get("primary", "#6c5ce7"),
            primary_hover=colors_dict.get("primary_hover", "#5b4bc4"),
            secondary=colors_dict.get("secondary", "#00cec9"),
            background=colors_dict.get("background", "#121214"),
            surface=colors_dict.get("surface", "#1a1a1e"),
            surface_elevated=colors_dict.get("surface_elevated", "#222228"),
            surface_input=colors_dict.get("surface_input", "#26262b"),
            border=colors_dict.get("border", "#2e2e38"),
            border_focus=colors_dict.get("border_focus", "#6c5ce7"),
            text_primary=colors_dict.get("text_primary", "#f1f1f5"),
            text_secondary=colors_dict.get("text_secondary", "#a5a5b5"),
            text_disabled=colors_dict.get("text_disabled", "#636375"),
            success=colors_dict.get("success", "#00b894"),
            warning=colors_dict.get("warning", "#fdcb6e"),
            danger=colors_dict.get("danger", "#d63031"),
            active=colors_dict.get("active", "#00cec9"),
        )

        display_font = typography_dict.get("display", "Segoe UI").split(",")[0].strip()
        body_font = typography_dict.get("body", "Segoe UI").split(",")[0].strip()
        mono_font = typography_dict.get("mono", "Consolas").split(",")[0].strip()
        fonts = TypographyTokens(
            display_family=display_font or "Segoe UI",
            body_family=body_font or "Segoe UI",
            mono_family=mono_font or "Consolas",
        )

        spacing = SpacingTokens(
            unit=spacing_dict.get("unit", 4),
            xs=spacing_dict.get("xs", 4),
            sm=spacing_dict.get("sm", 8),
            md=spacing_dict.get("md", 12),
            lg=spacing_dict.get("lg", 16),
            xl=spacing_dict.get("xl", 20),
            xxl=spacing_dict.get("xxl", 24),
        )

        return cls(colors=colors, fonts=fonts, spacing=spacing)
