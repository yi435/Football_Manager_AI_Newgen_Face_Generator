"""
Parser tests. Run with:  python -m unittest discover -s tests -v

Covers the FM26 Player Export plugin CSV output (semicolon-delimited), the
legacy FM24 formats (tab/text, HTML, RTF), the configurable uid_prefix, and
the "missing ID column" guidance error.
"""

import io
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.parser import PlayerParser, PromptBuilder
from src.xml_manager import XMLManager


class ParserTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = self._tmp.name

    def tearDown(self):
        self._tmp.cleanup()

    def _write(self, name, content, binary=False):
        path = os.path.join(self.dir, name)
        if binary:
            with open(path, "wb") as f:
                f.write(content)
        else:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
        return path

    def _ids(self, players):
        return [p["uid"] for p in players]

    def test_csv_semicolon_default_prefix(self):
        # Mirrors the FM26 Player Export CSV layout (with a UTF-8 BOM).
        csv_text = (
            "\ufeffID;Player;Nation;Age;Personality\n"
            "2000000001;Ruben Silva;FRA;17;Professional\n"
            "2000000002;Kai Tanaka;JPN;19;Balanced\n"
            "7100000001;Old Regen;BRA;24;Model Citizen\n"
            "abc123;Not Numeric;GER;20;Balanced\n"
        )
        path = self._write("player_export_20260310.csv", csv_text, binary=False)
        players = PlayerParser.parse_file(path)
        # Only numeric IDs starting with "2" are kept.
        self.assertEqual(self._ids(players), ["2000000001", "2000000002"])
        self.assertEqual(players[0]["name"], "Ruben Silva")
        self.assertEqual(players[0]["nat"], "FRA")
        self.assertEqual(players[0]["personality"], "Professional")

    def test_2nd_nat_column_precedence(self):
        # When 2nd Nat appears before Nat, primary Nat must NOT be overwritten by 2nd Nat!
        csv_text = (
            "ID;Player;2nd Nat;Nat;Age;Personality\n"
            "2000000010;Alexandre Diallo;SEN;FRA;18;Model Citizen\n"
        )
        path = self._write("second_nat_first.csv", csv_text)
        players = PlayerParser.parse_file(path)
        self.assertEqual(len(players), 1)
        self.assertEqual(players[0]["nat"], "FRA")
        self.assertEqual(players[0]["sec_nat"], "SEN")

    def test_word_boundary_id_matching(self):
        # Ensure column named 'Paid' or 'Valid' or 'Hidden' is not misidentified as ID column
        csv_text = (
            "Player;Paid;Valid;Age;Personality;ID\n"
            "Marcus;Yes;True;19;Jovial;2000000020\n"
        )
        path = self._write("word_boundary.csv", csv_text)
        players = PlayerParser.parse_file(path)
        self.assertEqual(len(players), 1)
        self.assertEqual(players[0]["uid"], "2000000020")
        self.assertEqual(players[0]["name"], "Marcus")

    def test_csv_with_bom_bytes(self):
        data = ("\ufeffID;Player;Nation;Age;Personality\n"
                "2000000001;A;BAN;18;Balanced\n").encode("utf-8-sig")
        path = self._write("bom.csv", data, binary=True)
        players = PlayerParser.parse_file(path)
        self.assertEqual(self._ids(players), ["2000000001"])

    def test_csv_latin1_fallback(self):
        # Plugin is known to garble accents; latin-1 fallback must not crash and
        # must still parse the ID column.
        raw = "ID;Player;Nation;Age;Personality\n2000000001;Jo\u00e3o Cruz;BRA;19;Balanced\n"
        path = self._write("latin1.csv", raw.encode("latin-1"), binary=True)
        players = PlayerParser.parse_file(path)
        self.assertEqual(self._ids(players), ["2000000001"])

    def test_csv_uid_prefix_empty(self):
        csv_text = (
            "ID;Player;Nation;Age;Personality\n"
            "2000000001;A;FRA;17;Balanced\n"
            "7100000005;B;GER;21;Balanced\n"
        )
        path = self._write("all.csv", csv_text)
        players = PlayerParser.parse_file(path, uid_prefix="")
        self.assertEqual(self._ids(players), ["2000000001", "7100000005"])

    def test_csv_missing_id_column_raises(self):
        csv_text = "Player;Nation;Age\nRuben;FRA;17\n"
        path = self._write("noid.csv", csv_text)
        with self.assertRaises(ValueError):
            PlayerParser.parse_file(path)

    def test_html_plugin_style(self):
        html = """<html><body><table>
        <tr><th>ID</th><th>Player</th><th>Nation</th><th>Age</th><th>Personality</th></tr>
        <tr><td>2000000042</td><td>Emil Johansson</td><td>SWE</td><td>16</td><td>Jovial</td></tr>
        <tr><td>2000000043</td><td>Leo Dubois</td><td>FRA</td><td>18</td><td>Perfectionist</td></tr>
        </table></body></html>"""
        path = self._write("export.html", html)
        players = PlayerParser.parse_file(path)
        self.assertEqual(self._ids(players), ["2000000042", "2000000043"])

    def test_tab_text_legacy(self):
        text = "Unique Id\tName\tNat\tAge\tPersonality\n" \
               "2000000099\tZak Mensah\tGHA\t17\tResolute\n"
        path = self._write("export.txt", text)
        players = PlayerParser.parse_file(path)
        self.assertEqual(self._ids(players), ["2000000099"])

    def test_r_prefix_stripped(self):
        csv_text = "ID;Player;Nation;Age;Personality\nr-2000000007;X;NED;20;Balanced\n"
        path = self._write("rpref.csv", csv_text)
        players = PlayerParser.parse_file(path)
        self.assertEqual(self._ids(players), ["2000000007"])

    def test_empty_export(self):
        path = self._write("empty.csv", "ID;Player\n")
        players = PlayerParser.parse_file(path)
        self.assertEqual(players, [])

    def test_input_sanitization(self):
        csv_text = "ID;Player;Nation;Age;Personality\n2000000099;Bad\tName\r\nWith\x00Controls;FRA;17;Model\nCitizen\n"
        path = self._write("sanitize.csv", csv_text)
        players = PlayerParser.parse_file(path)
        self.assertEqual(len(players), 1)
        self.assertNotIn("\x00", players[0]["name"])
        self.assertNotIn("\r", players[0]["name"])
        self.assertNotIn("\n", players[0]["name"])


class PromptBuilderTest(unittest.TestCase):
    def test_isolated_rng_and_safe_replacement(self):
        player_under_20 = {
            "uid": "2000000001",
            "name": "Jean Dupont",
            "nat": "FRA",
            "sec_nat": "",
            "age": "17",
            "personality": "Model Citizen"
        }
        template = "photo of a [AGE]-year-old male [NATIONALITY] football player, [PERSONALITY]"
        
        prompt1 = PromptBuilder.build_prompt(player_under_20, template)
        prompt2 = PromptBuilder.build_prompt(player_under_20, template)
        
        # Must be completely deterministic for the same UID
        self.assertEqual(prompt1, prompt2)
        # Must replace 'male' with 'teenage male' safely
        self.assertIn("teenage male", prompt1)
        self.assertIn("youth academy soccer player", prompt1)
        self.assertIn("17-year-old", prompt1)
        self.assertIn("French", prompt1)

    def test_female_word_not_corrupted(self):
        player = {
            "uid": "2000000002",
            "name": "Alex Morgan",
            "nat": "USA",
            "sec_nat": "",
            "age": "18",
            "personality": "Balanced"
        }
        template = "photo of a [AGE]-year-old female [NATIONALITY] player, [PERSONALITY]"
        prompt = PromptBuilder.build_prompt(player, template)
        # 'female' must NOT become 'feteenage male'
        self.assertIn("female", prompt)
        self.assertNotIn("feteenage male", prompt)


class XMLManagerTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = self._tmp.name

    def tearDown(self):
        self._tmp.cleanup()

    def test_bidirectional_attribute_reading_and_atomic_save(self):
        xml_content = """<record>
            <boolean id="preload" value="false"/>
            <boolean id="amap" value="false"/>
            <list id="maps">
                <record from="2000000001" to="graphics/pictures/person/r-2000000001/portrait"/>
                <record to="graphics/pictures/person/r-2000000002/portrait" from="2000000002"/>
                <record to="graphics\\pictures\\person\\r-2000000003\\portrait" from="2000000003"/>
            </list>
        </record>"""
        config_path = os.path.join(self.dir, "config.xml")
        with open(config_path, "w", encoding="utf-8") as f:
            f.write(xml_content)

        mgr = XMLManager(self.dir)
        mappings = mgr.load_mappings()
        
        self.assertEqual(len(mappings), 3)
        self.assertEqual(mappings["2000000001"], "2000000001")
        self.assertEqual(mappings["2000000002"], "2000000002")
        self.assertEqual(mappings["2000000003"], "2000000003")

        # Test adding and saving
        mappings["2000000004"] = "2000000004"
        mgr.save_mappings(mappings)

        new_mappings = mgr.load_mappings()
        self.assertEqual(len(new_mappings), 4)
        self.assertEqual(new_mappings["2000000004"], "2000000004")


if __name__ == "__main__":
    unittest.main()