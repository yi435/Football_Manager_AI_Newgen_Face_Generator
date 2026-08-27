import os
import re

class XMLManager:
    def __init__(self, graphics_dir):
        self.graphics_dir = graphics_dir
        self.config_path = os.path.join(graphics_dir, "config.xml")

    def load_mappings(self):
        """
        Reads the config.xml file and returns a dictionary of mappings: {player_uid: image_filename}
        Uses robust regex parsing matching both attribute orderings (from...to and to...from)
        and normalizing path separators.
        """
        mappings = {}
        if not os.path.exists(self.config_path):
            return mappings

        try:
            with open(self.config_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # Find all <record from="..." to="..."/> or <record to="..." from="..."/> entries.
            pattern = re.compile(
                r'<record\s+(?:from=["\'](?P<from1>[^"\']+)["\']\s+to=["\'](?P<to1>[^"\']+)["\']|'
                r'to=["\'](?P<to2>[^"\']+)["\']\s+from=["\'](?P<from2>[^"\']+)["\'])\s*/?>',
                re.IGNORECASE
            )
            for match in pattern.finditer(content):
                from_val = match.group("from1") or match.group("from2")
                to_val = match.group("to1") or match.group("to2")

                if not from_val or not to_val:
                    continue

                # Normalize target path: "graphics/pictures/person/r-{UID}/portrait"
                norm_to = to_val.replace("\\", "/").strip("/")
                parts = norm_to.split("/")
                if len(parts) >= 4:
                    raw_uid = parts[3]
                    if raw_uid.startswith("r-"):
                        raw_uid = raw_uid[2:]
                    if raw_uid:
                        mappings[raw_uid] = from_val
        except Exception as e:
            print(f"Error reading config.xml: {e}. Starting with empty mappings.")
        
        return mappings

    def save_mappings(self, mappings):
        """
        Writes the mappings dictionary back to config.xml using atomic replacement
        and the community standard format (NewGAN/fmXML).
        """
        # Ensure target graphics directories exist
        os.makedirs(self.graphics_dir, exist_ok=True)

        lines = []
        lines.append("<record>")
        lines.append("\t<!-- resource info -->")
        lines.append('\t<boolean id="preload" value="false"/>')
        lines.append('\t<boolean id="amap" value="false"/>')
        lines.append("")
        lines.append("\t<!-- picture mappings -->")
        lines.append("\t<!-- maps link user to game -->")
        lines.append('\t<list id="maps">')

        # Populate records sorted by UID numerically/alphabetically
        for uid in sorted(mappings.keys(), key=lambda x: int(x) if x.isdigit() else x):
            from_filename = mappings[uid]
            # Maps the image filename directly to the person UID with the required 'r-' prefix for FM24
            lines.append(f'\t\t<record from="{from_filename}" to="graphics/pictures/person/r-{uid}/portrait"/>')

        lines.append("\t</list>")
        lines.append("</record>")

        clean_xml = "\n".join(lines)
        tmp_path = f"{self.config_path}.tmp.{os.getpid()}"
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                f.write(clean_xml)
            os.replace(tmp_path, self.config_path)
        except Exception:
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except OSError:
                    pass
            raise

    def add_mapping(self, uid, filename):
        """
        Loads mappings, adds/updates a mapping for a player UID, and saves it.
        """
        mappings = self.load_mappings()
        mappings[uid] = filename
        self.save_mappings(mappings)
