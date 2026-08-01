import os
import xml.etree.ElementTree as ET
from xml.dom import minidom

class XMLManager:
    def __init__(self, graphics_dir):
        self.graphics_dir = graphics_dir
        self.config_path = os.path.join(graphics_dir, "config.xml")

    def load_mappings(self):
        """
        Reads the config.xml file and returns a dictionary of mappings: {player_uid: image_filename}
        """
        mappings = {}
        if not os.path.exists(self.config_path):
            return mappings

        try:
            tree = ET.parse(self.config_path)
            root = tree.getroot()
            
            # Find the <list id="maps"> tag
            maps_list = root.find(".//list[@id='maps']")
            if maps_list is not None:
                for record in maps_list.findall("record"):
                    from_val = record.get("from")
                    to_val = record.get("to")
                    if from_val and to_val:
                        # Extract the UID from the target path: "graphics/pictures/person/{UID}/portrait"
                        parts = to_val.split("/")
                        if len(parts) >= 4:
                            uid = parts[3].replace("r-", "")
                            mappings[uid] = from_val
        except Exception as e:
            print(f"Error reading config.xml: {e}. Starting with empty mappings.")
        
        return mappings

    def save_mappings(self, mappings):
        """
        Writes the mappings dictionary back to config.xml with clean indentation.
        """
        # Ensure directories exist
        os.makedirs(self.graphics_dir, exist_ok=True)

        root = ET.Element("record")
        
        # Add the standard FM headers
        preload = ET.SubElement(root, "boolean", {"id": "preload", "value": "false"})
        amap = ET.SubElement(root, "boolean", {"id": "amap", "value": "false"})
        
        # Add the list container
        maps_list = ET.SubElement(root, "list", {"id": "maps"})
        
        # Populate records sorted by UID
        for uid in sorted(mappings.keys(), key=lambda x: int(x) if x.isdigit() else x):
            from_filename = mappings[uid]
            target_path = f"graphics/pictures/person/r-{uid}/portrait"
            ET.SubElement(maps_list, "record", {"from": from_filename, "to": target_path})

        # Convert to string and prettify
        raw_xml = ET.tostring(root, encoding="utf-8")
        parsed = minidom.parseString(raw_xml)
        pretty_xml = parsed.toprettyxml(indent="    ", encoding="utf-8").decode("utf-8")
        
        # minidom's toprettyxml adds a declaration line "<?xml version="1.0" ?>" which FM doesn't require,
        # but it is harmless. If we want it identical to FM standard, we can strip the first line.
        lines = pretty_xml.splitlines()
        if lines and lines[0].startswith("<?xml"):
            lines = lines[1:]
        clean_xml = "\n".join(lines).strip()

        with open(self.config_path, "w", encoding="utf-8") as f:
            f.write(clean_xml)

    def add_mapping(self, uid, filename):
        """
        Loads mappings, adds or updates a mapping for a player UID, and saves it.
        """
        mappings = self.load_mappings()
        mappings[uid] = filename
        self.save_mappings(mappings)
