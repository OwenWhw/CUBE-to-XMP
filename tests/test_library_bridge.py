import base64
from io import BytesIO
import tempfile
import unittest
from pathlib import Path
import xml.etree.ElementTree as ET

from PIL import Image
from conversion_service import ConversionService
from lut_library import LutLibrary
from web_studio import StudioBridge

ROOT = Path(__file__).resolve().parents[1]


class FakeWindow:
    def __init__(self, *choices):
        self.choices = iter(choices)

    def create_file_dialog(self, *args, **kwargs):
        return next(self.choices)


class LibraryBridgeTests(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.tmp = Path(folder.name)
        self.library = LutLibrary(ROOT, self.tmp / "library")
        self.service = ConversionService()

    def test_import_persists_after_source_deleted_and_removes_cleanly(self):
        source = self.tmp / "custom.xmp"
        cube = ROOT / "built_in_luts" / "Fuji_Astia_Soft.cube"
        self.service.export(self.service.load_lut(cube), source, 16)
        ids = self.library.import_paths([source, source])
        self.assertEqual(len(ids), 1)
        source.unlink()
        reloaded = LutLibrary(ROOT, self.tmp / "library")
        item = reloaded.get(ids[0])
        self.assertIsNotNone(item)
        self.assertEqual(reloaded.service.load_lut(item.path).source, "XMP")
        self.assertTrue(reloaded.remove(ids[0]))
        self.assertIsNone(LutLibrary(ROOT, self.tmp / "library").get(ids[0]))

    def test_bridge_import_then_xmp_to_cube(self):
        source = self.tmp / "input.xmp"
        cube = ROOT / "built_in_luts" / "Fuji_Monochrome.cube"
        self.service.export(self.service.load_lut(cube), source, 16)
        output = self.tmp / "result.cube"
        bridge = StudioBridge(ROOT, self.tmp / "library")
        bridge._window = FakeWindow((str(source),), (str(output),))
        imported = bridge.import_luts()
        self.assertTrue(imported["ok"], imported)
        self.assertEqual(imported["data"]["document"]["target"], "CUBE")
        exported = bridge.export(17)
        self.assertTrue(exported["ok"], exported)
        self.assertEqual(self.service.load_lut(output).size, 17)
        self.assertEqual(len(bridge.state()["data"]["history"]), 1)

    def test_preferences_persist_and_reject_invalid_values(self):
        bridge = StudioBridge(ROOT, self.tmp / "library")
        self.assertEqual(bridge.state()["data"]["settings"],
                         {"language": "zh", "theme": "light", "motion": True})
        saved = bridge.update_settings({"language": "en", "theme": "dark", "motion": False})
        self.assertTrue(saved["ok"], saved)
        self.assertEqual(StudioBridge(ROOT, self.tmp / "library").state()["data"]["settings"],
                         {"language": "en", "theme": "dark", "motion": False})
        self.assertFalse(bridge.update_settings({"theme": "neon"})["ok"])
        self.assertFalse(bridge.update_settings({"motion": 1})["ok"])
        self.assertEqual(bridge.state()["data"]["settings"], saved["data"])

    def test_photo_and_library_previews_keep_detail_and_refresh(self):
        bridge = StudioBridge(ROOT, self.tmp / "library")
        first = bridge.state()["data"]

        def dimensions(uri):
            with Image.open(BytesIO(base64.b64decode(uri.split(",", 1)[1]))) as image:
                return image.size

        self.assertGreaterEqual(dimensions(first["original"])[0], 1500)
        self.assertGreaterEqual(dimensions(first["items"][0]["thumbnail"])[0], 700)
        old_thumbnail = first["items"][0]["thumbnail"]
        photo_path = self.tmp / "new-photo.png"
        Image.new("RGB", (2500, 1700), "#3861a4").save(photo_path)
        bridge._window = FakeWindow((str(photo_path),))
        changed = bridge.choose_photo()
        self.assertTrue(changed["ok"], changed)
        self.assertEqual(dimensions(changed["data"]["original"]), (2500, 1700))
        self.assertNotEqual(changed["data"]["items"][0]["thumbnail"], old_thumbnail)
        self.assertEqual(bridge._thumbnail_photo.size, (735, 500))

    def test_xmp_namespace_prefix_does_not_affect_decoder(self):
        cube = ROOT / "built_in_luts" / "Fuji_Provia_Standard.cube"
        out = self.tmp / "prefix.xmp"
        self.service.export(self.service.load_lut(cube), out, 16)
        tree = ET.parse(out)
        description = tree.getroot().find('.//{http://www.w3.org/1999/02/22-rdf-syntax-ns#}Description')
        table_key = next(key for key in description.attrib if '}Table_' in key)
        encoded = description.attrib[table_key]
        description.attrib[table_key] = ' '.join(encoded[i:i+80] for i in range(0, len(encoded), 80))
        ET.register_namespace("camera", "http://ns.adobe.com/camera-raw-settings/1.0/")
        tree.write(out, encoding="utf-8", xml_declaration=True)
        self.assertEqual(self.service.load_lut(out).size, 16)


if __name__ == "__main__":
    unittest.main()
