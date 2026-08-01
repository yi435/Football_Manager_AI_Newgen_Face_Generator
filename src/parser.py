import os
import re
import random
from html.parser import HTMLParser
from striprtf.striprtf import rtf_to_text

# FIFA/FM 3-Letter Country Code to Nationality Details
COUNTRY_MAP = {
    "ENG": {"name": "England", "adjective": "English", "region": "WEST_EUROPE"},
    "FRA": {"name": "France", "adjective": "French", "region": "WEST_EUROPE"},
    "GER": {"name": "Germany", "adjective": "German", "region": "WEST_EUROPE"},
    "ITA": {"name": "Italy", "adjective": "Italian", "region": "SOUTH_EUROPE"},
    "ESP": {"name": "Spain", "adjective": "Spanish", "region": "SOUTH_EUROPE"},
    "BRA": {"name": "Brazil", "adjective": "Brazilian", "region": "SOUTH_AMERICA"},
    "ARG": {"name": "Argentina", "adjective": "Argentinian", "region": "SOUTH_AMERICA"},
    "NED": {"name": "Netherlands", "adjective": "Dutch", "region": "WEST_EUROPE"},
    "POR": {"name": "Portugal", "adjective": "Portuguese", "region": "SOUTH_EUROPE"},
    "BEL": {"name": "Belgium", "adjective": "Belgian", "region": "WEST_EUROPE"},
    "SWE": {"name": "Sweden", "adjective": "Swedish", "region": "NORDIC"},
    "NOR": {"name": "Norway", "adjective": "Norwegian", "region": "NORDIC"},
    "DEN": {"name": "Denmark", "adjective": "Danish", "region": "NORDIC"},
    "FIN": {"name": "Finland", "adjective": "Finnish", "region": "NORDIC"},
    "ISL": {"name": "Iceland", "adjective": "Icelandic", "region": "NORDIC"},
    "JPN": {"name": "Japan", "adjective": "Japanese", "region": "EAST_ASIA"},
    "KOR": {"name": "South Korea", "adjective": "Korean", "region": "EAST_ASIA"},
    "CHN": {"name": "China", "adjective": "Chinese", "region": "EAST_ASIA"},
    "USA": {"name": "United States", "adjective": "American", "region": "NORTH_AMERICA"},
    "NGA": {"name": "Nigeria", "adjective": "Nigerian", "region": "AFRICA"},
    "SEN": {"name": "Senegal", "adjective": "Senegalese", "region": "AFRICA"},
    "GHA": {"name": "Ghana", "adjective": "Ghanaian", "region": "AFRICA"},
    "CIV": {"name": "Ivory Coast", "adjective": "Ivorian", "region": "AFRICA"},
    "EGY": {"name": "Egypt", "adjective": "Egyptian", "region": "MIDDLE_EAST"},
    "MAR": {"name": "Morocco", "adjective": "Moroccan", "region": "MIDDLE_EAST"},
    "ALG": {"name": "Algeria", "adjective": "Algerian", "region": "MIDDLE_EAST"},
    "TUN": {"name": "Tunisia", "adjective": "Tunisian", "region": "MIDDLE_EAST"},
    "KSA": {"name": "Saudi Arabia", "adjective": "Saudi", "region": "MIDDLE_EAST"},
    "MEX": {"name": "Mexico", "adjective": "Mexican", "region": "SOUTH_AMERICA"},
    "COL": {"name": "Colombia", "adjective": "Colombian", "region": "SOUTH_AMERICA"},
    "URU": {"name": "Uruguay", "adjective": "Uruguayan", "region": "SOUTH_AMERICA"},
    "CHL": {"name": "Chile", "adjective": "Chilean", "region": "SOUTH_AMERICA"},
    "POL": {"name": "Poland", "adjective": "Polish", "region": "EAST_EUROPE"},
    "UKR": {"name": "Ukraine", "adjective": "Ukrainian", "region": "EAST_EUROPE"},
    "RUS": {"name": "Russia", "adjective": "Russian", "region": "EAST_EUROPE"},
    "CRO": {"name": "Croatia", "adjective": "Croatian", "region": "EAST_EUROPE"},
    "SRB": {"name": "Serbia", "adjective": "Serbian", "region": "EAST_EUROPE"},
    "TUR": {"name": "Turkey", "adjective": "Turkish", "region": "MIDDLE_EAST"},
    "GRE": {"name": "Greece", "adjective": "Greek", "region": "SOUTH_EUROPE"},
    "SUI": {"name": "Switzerland", "adjective": "Swiss", "region": "WEST_EUROPE"},
    "AUT": {"name": "Austria", "adjective": "Austrian", "region": "WEST_EUROPE"},
    "SCO": {"name": "Scotland", "adjective": "Scottish", "region": "WEST_EUROPE"},
    "WAL": {"name": "Wales", "adjective": "Welsh", "region": "WEST_EUROPE"},
    "NIR": {"name": "Northern Ireland", "adjective": "Northern Irish", "region": "WEST_EUROPE"},
    "IRL": {"name": "Ireland", "adjective": "Irish", "region": "WEST_EUROPE"},
    "AUS": {"name": "Australia", "adjective": "Australian", "region": "WEST_EUROPE"},
    "RSA": {"name": "South Africa", "adjective": "South African", "region": "AFRICA"},
    "CMR": {"name": "Cameroon", "adjective": "Cameroonian", "region": "AFRICA"},
}

# Regional Fallback Presets for Hair, Eyes, and Skin Tone
REGIONAL_PRESETS = {
    "NORDIC": [
        {"ethnicity": "nordic/scandinavian heritage", "skin": "fair skin", "hair": ["blonde hair", "light brown hair"], "eyes": ["blue eyes", "green eyes"]}
    ],
    "WEST_EUROPE": [
        {"ethnicity": "western european heritage", "skin": "fair skin", "hair": ["brown hair", "dark brown hair", "blonde hair"], "eyes": ["brown eyes", "blue eyes", "hazel eyes"]}
    ],
    "SOUTH_EUROPE": [
        {"ethnicity": "southern european heritage", "skin": "light olive skin", "hair": ["dark brown hair", "black wavy hair"], "eyes": ["brown eyes", "hazel eyes"]}
    ],
    "EAST_EUROPE": [
        {"ethnicity": "eastern european heritage", "skin": "pale skin", "hair": ["brown hair", "light brown hair", "dark hair"], "eyes": ["blue eyes", "grey eyes", "brown eyes"]}
    ],
    "EAST_ASIA": [
        {"ethnicity": "east asian heritage", "skin": "fair skin", "hair": ["straight black hair", "neat black hair"], "eyes": ["dark brown eyes", "black eyes"]}
    ],
    "MIDDLE_EAST": [
        {"ethnicity": "middle eastern heritage", "skin": "olive skin", "hair": ["thick dark hair", "curly black hair"], "eyes": ["dark brown eyes"]}
    ],
    "AFRICA": [
        {"ethnicity": "sub-saharan african heritage", "skin": "dark skin", "hair": ["black curly hair", "short black buzzcut hair", "short afro hair"], "eyes": ["dark brown eyes"]}
    ],
    "SOUTH_AMERICA": [
        {"ethnicity": "latino heritage", "skin": "tan skin", "hair": ["wavy black hair", "dark brown hair"], "eyes": ["brown eyes"]}
    ],
    "NORTH_AMERICA": [
        {"ethnicity": "north american heritage", "skin": "fair skin", "hair": ["brown hair", "blonde hair"], "eyes": ["blue eyes", "brown eyes"]}
    ]
}

# Weighted Demographic Distributions for Multi-Ethnic Countries
DEMOGRAPHIC_WEIGHTS = {
    "ENG": [
        {"weight": 75, "preset": "WEST_EUROPE"},
        {"weight": 18, "preset": "AFRICA"},
        {"weight": 7, "preset": "MIDDLE_EAST"}  # Proxy for South Asian / Middle Eastern heritage
    ],
    "FRA": [
        {"weight": 70, "preset": "WEST_EUROPE"},
        {"weight": 20, "preset": "AFRICA"},
        {"weight": 10, "preset": "MIDDLE_EAST"}  # North African heritage
    ],
    "GER": [
        {"weight": 78, "preset": "WEST_EUROPE"},
        {"weight": 14, "preset": "MIDDLE_EAST"}, # Turkish heritage
        {"weight": 8, "preset": "AFRICA"}
    ],
    "BEL": [
        {"weight": 75, "preset": "WEST_EUROPE"},
        {"weight": 17, "preset": "AFRICA"},
        {"weight": 8, "preset": "MIDDLE_EAST"}
    ],
    "NED": [
        {"weight": 78, "preset": "WEST_EUROPE"},
        {"weight": 15, "preset": "AFRICA"},
        {"weight": 7, "preset": "MIDDLE_EAST"}
    ],
    "BRA": [
        {"weight": 48, "preset": "SOUTH_AMERICA"}, # Pardo/Latino
        {"weight": 40, "preset": "SOUTH_EUROPE"},  # European descent
        {"weight": 12, "preset": "AFRICA"}         # Afro-Brazilian
    ],
    "USA": [
        {"weight": 60, "preset": "NORTH_AMERICA"},
        {"weight": 18, "preset": "AFRICA"},
        {"weight": 18, "preset": "SOUTH_AMERICA"},
        {"weight": 4, "preset": "EAST_ASIA"}
    ],
}

# Simple HTML parser to parse Football Manager exported Web Pages (.html)
class FMHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_table = False
        self.in_row = False
        self.in_cell = False
        self.headers = []
        self.rows = []
        self.current_row = []
        self.current_cell_data = ""

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            self.in_table = True
        elif tag == "tr" and self.in_table:
            self.in_row = True
            self.current_row = []
        elif tag in ["td", "th"] and self.in_row:
            self.in_cell = True
            self.current_cell_data = ""

    def handle_data(self, data):
        if self.in_cell:
            self.current_cell_data += data

    def handle_endtag(self, tag):
        if tag == "table":
            self.in_table = False
        elif tag == "tr" and self.in_row:
            self.in_row = False
            clean_row = [c.strip() for c in self.current_row]
            if not self.headers:
                self.headers = clean_row
            else:
                self.rows.append(clean_row)
        elif tag in ["td", "th"] and self.in_cell:
            self.in_cell = False
            self.current_row.append(self.current_cell_data)

class PlayerParser:
    @staticmethod
    def parse_file(filepath):
        """
        Parses an exported RTF or HTML file from FM and returns a list of player dicts.
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Export file not found: {filepath}")

        _, ext = os.path.splitext(filepath.lower())
        
        if ext == ".rtf":
            return PlayerParser._parse_rtf(filepath)
        elif ext in [".html", ".htm"]:
            return PlayerParser._parse_html(filepath)
        else:
            # Fallback to plain text TSV parsing
            return PlayerParser._parse_text(filepath)

    @staticmethod
    def _parse_rtf(filepath):
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        plain_text = rtf_to_text(content)
        return PlayerParser._parse_text_content(plain_text)

    @staticmethod
    def _parse_html(filepath):
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            html_content = f.read()
        
        parser = FMHTMLParser()
        parser.feed(html_content)
        
        # Standardize headers to lowercase keys
        headers = [h.lower() for h in parser.headers]
        players = []

        # Map typical FM column names to standard fields
        # UID is typically named 'id' or 'unique id'
        # Nationality is 'nat' or 'nationality' or 'nation'
        # Second Nat is 'second nationality' or '2nd nat'
        # Age is 'age'
        # Personality is 'personality'
        uid_idx = PlayerParser._find_column_index(headers, ["id", "uid", "unique id"])
        name_idx = PlayerParser._find_column_index(headers, ["name", "player name"])
        nat_idx = PlayerParser._find_column_index(headers, ["nat", "nationality", "nation"])
        sec_nat_idx = PlayerParser._find_column_index(headers, ["2nd nat", "second nationality", "second nat"])
        age_idx = PlayerParser._find_column_index(headers, ["age"])
        pers_idx = PlayerParser._find_column_index(headers, ["personality"])

        if uid_idx == -1:
            raise ValueError("Could not find ID/UID column in exported file. Ensure your FM search view contains the ID column.")

        for row in parser.rows:
            if len(row) <= uid_idx:
                continue
            
            uid = row[uid_idx].replace("r-", "").strip()
            # We filter for newgen UIDs only (which start with 200 or are 10 digits starting with 2)
            if not uid.isdigit() or not uid.startswith("2"):
                continue

            player = {
                "uid": uid,
                "name": row[name_idx] if name_idx != -1 and len(row) > name_idx else "Unknown Newgen",
                "nat": row[nat_idx] if nat_idx != -1 and len(row) > nat_idx else "",
                "sec_nat": row[sec_nat_idx] if sec_nat_idx != -1 and len(row) > sec_nat_idx else "",
                "age": row[age_idx] if age_idx != -1 and len(row) > age_idx else "16",
                "personality": row[pers_idx] if pers_idx != -1 and len(row) > pers_idx else "Balanced"
            }
            players.append(player)

        return players

    @staticmethod
    def _parse_text(filepath):
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        return PlayerParser._parse_text_content(content)

    @staticmethod
    def _parse_text_content(text):
        rows = PlayerParser._extract_table_rows(text)
        if not rows:
            return []

        headers = [h.lower() for h in rows[0]]
        
        uid_idx = PlayerParser._find_column_index(headers, ["id", "uid", "unique id"])
        name_idx = PlayerParser._find_column_index(headers, ["name", "player name"])
        nat_idx = PlayerParser._find_column_index(headers, ["nat", "nationality", "nation"])
        sec_nat_idx = PlayerParser._find_column_index(headers, ["2nd nat", "second nationality", "second nat"])
        age_idx = PlayerParser._find_column_index(headers, ["age"])
        pers_idx = PlayerParser._find_column_index(headers, ["personality"])

        if uid_idx == -1:
            raise ValueError("Could not find ID/UID column in exported file. Ensure your FM search view contains the ID column.")

        players = []
        for row in rows[1:]:
            if len(row) <= uid_idx:
                continue

            uid = row[uid_idx].replace("r-", "").strip()
            # We filter for newgen UIDs only
            if not uid.isdigit() or not uid.startswith("2"):
                continue

            player = {
                "uid": uid,
                "name": row[name_idx] if name_idx != -1 and len(row) > name_idx else "Unknown Newgen",
                "nat": row[nat_idx] if nat_idx != -1 and len(row) > nat_idx else "",
                "sec_nat": row[sec_nat_idx] if sec_nat_idx != -1 and len(row) > sec_nat_idx else "",
                "age": row[age_idx] if age_idx != -1 and len(row) > age_idx else "16",
                "personality": row[pers_idx] if pers_idx != -1 and len(row) > pers_idx else "Balanced"
            }
            players.append(player)

        return players

    @staticmethod
    def _extract_table_rows(text):
        """
        Builds table rows from FM exports. Tab/text exports use one row per line;
        RTF printouts often collapse the whole pipe table onto a single line with
        dashed separator rows between entries.
        """
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        if not lines:
            return []

        combined = "\n".join(lines)
        if "|" in combined and re.search(r"\|\s*-{5,}", combined):
            parts = re.split(r"\|\s*-{10,}[^|]*\|", combined)
            rows = []
            for part in parts:
                cells = [cell.strip() for cell in part.split("|") if cell.strip()]
                if cells:
                    rows.append(cells)
            if len(rows) > 1:
                return rows

        first_line = lines[0]
        separator = "|" if "|" in first_line else "\t"
        return [[cell.strip() for cell in line.split(separator)] for line in lines]

    @staticmethod
    def _find_column_index(headers, variants):
        for variant in variants:
            for idx, header in enumerate(headers):
                if header == variant or variant in header:
                    return idx
        return -1

class PromptBuilder:
    @staticmethod
    def build_prompt(player, prompt_template):
        """
        Creates a custom prompt based on the player details and the base template.
        Generates highly descriptive, realistic, and non-redundant sports portraits.
        """
        uid = player["uid"]
        age = player["age"]
        nat_code = player["nat"]
        sec_nat_code = player["sec_nat"]
        personality = player["personality"].lower()

        # Step 1: Resolve Nationality details
        nat_info = COUNTRY_MAP.get(nat_code, {"name": nat_code, "adjective": nat_code, "region": "WEST_EUROPE"})
        nat_name = nat_info["adjective"]
        region = nat_info["region"]

        # Step 2: Establish the base seed from UID to keep features consistent
        random.seed(int(uid))

        # Step 3: Choose demographic features based on weights
        preset_region = region
        if nat_code in DEMOGRAPHIC_WEIGHTS:
            choices = DEMOGRAPHIC_WEIGHTS[nat_code]
            weights = [c["weight"] for c in choices]
            selected = random.choices(choices, weights=weights, k=1)[0]
            preset_region = selected["preset"]

        # Select a style profile from the regional presets
        preset_list = REGIONAL_PRESETS.get(preset_region, REGIONAL_PRESETS["WEST_EUROPE"])
        profile = random.choice(preset_list)
        
        # Pick physical attributes
        skin_tone = profile["skin"]
        hair_color_raw = random.choice(profile["hair"])
        hair_color = hair_color_raw.replace(" hair", "").strip()
        eye_color_raw = random.choice(profile["eyes"])
        eye_color = eye_color_raw.replace(" eyes", "").strip()

        # Step 4: Handle Ancestry / Dual Nationality
        ancestry_desc = ""
        if sec_nat_code and sec_nat_code != nat_code:
            sec_info = COUNTRY_MAP.get(sec_nat_code)
            if sec_info:
                ancestry_desc = f", with {sec_info['adjective']} ancestral origins"

        # Step 5: Map visual attributes based on Personality
        hair_style = ""
        expression_details = "neutral focused expression"
        vibe_details = "looking determined"
        scar_desc = ""

        # Friendly/Professional personalities
        if any(p in personality for p in ["citizen", "professional", "resolute", "perfectionist", "iron"]):
            hair_style = random.choice(["neatly combed ", "well-groomed ", "neat clean-cut "])
            expression_details = random.choice(["friendly confident smile", "polite warm smile"])
            vibe_details = "looking highly professional and disciplined"
        # Aggressive/Bad personalities
        elif any(p in personality for p in ["temperamental", "confrontational", "outspoken", "unambitious", "slack"]):
            hair_style = random.choice(["slightly messy ", "textured casual ", "modern textured "])
            expression_details = random.choice(["stern intense expression", "serious focused look"])
            vibe_details = "looking fierce and determined"
            # 25% chance of a minor scar for aggressive players
            if random.random() < 0.25:
                scar_desc = ", with a small faint scar on his cheek"
        # Happy/Warm personalities
        elif any(p in personality for p in ["jovial", "spirited", "charismatic"]):
            hair_style = random.choice(["relaxed ", "casual styled "])
            expression_details = "big happy smile, cheerful laughing eyes"
            vibe_details = "looking friendly and approachable"
        # Casual/Slack personalities
        elif any(p in personality for p in ["casual", "slack", "unambitious"]):
            hair_style = "tousled casual "
            expression_details = "relaxed calm expression"
            vibe_details = "looking laid-back"
        # Default
        else:
            hair_style = "athletic short "
            expression_details = "neutral focused look"
            vibe_details = "looking determined"

        # Format clean hair and eye descriptions
        hair_desc = f"{hair_style}{hair_color} hair"
        eyes_desc = f"{eye_color} eyes"

        # Step 6: Age milestones adaptations
        age_int = int(age) if age.isdigit() else 16
        beard_style = "clean-shaven face"
        
        # Milestone updates
        if age_int >= 20:
            if preset_region in ["MIDDLE_EAST", "SOUTH_EUROPE", "SOUTH_AMERICA"]:
                beard_style = random.choice(["thick heavy stubble", "light stubble beard", "clean-shaven face"])
            else:
                beard_style = random.choice(["light stubble", "clean-shaven face"])
        if age_int >= 24:
            if preset_region in ["MIDDLE_EAST", "SOUTH_EUROPE", "SOUTH_AMERICA"]:
                beard_style = random.choice(["full well-groomed beard", "thick beard", "light stubble beard"])
            else:
                beard_style = random.choice(["short trimmed beard", "light stubble beard", "clean-shaven face"])

        # Combine all physical details into a cohesive player description
        player_desc = (
            f"with {hair_desc} and {eyes_desc}, "
            f"{profile['ethnicity']} with {skin_tone}, "
            f"{beard_style}, {expression_details}, {vibe_details}{scar_desc}{ancestry_desc}"
        )

        # Replace placeholders in template
        prompt = prompt_template
        prompt = prompt.replace("[AGE]", str(age))
        prompt = prompt.replace("[NATIONALITY]", nat_name)
        prompt = prompt.replace("[PERSONALITY]", player_desc)

        return prompt
