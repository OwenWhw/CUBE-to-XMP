import tempfile
import unittest
import re
import struct
import zlib
from pathlib import Path
import xml.etree.ElementTree as ET

from PIL import Image, ImageChops
from conversion_service import ConversionService, ConversionError
from lut_core import build_cube, encode_zlib_base85

ROOT = Path(__file__).resolve().parents[1]


class ServiceTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.tmp = Path(self.folder.name)
        self.service = ConversionService()
        self.samples = [(r/15, g/15, b/15) for b in range(16) for g in range(16) for r in range(16)]
        self.source = self.tmp / "identity.cube"
        self.source.write_text(build_cube("Identity & 光影 <test>", 16, self.samples), encoding="utf-8")

    def test_identity_photo_preview(self):
        doc = self.service.load_lut(self.source)
        photo = Image.new("RGB", (3, 1))
        photo.putdata([(15, 80, 240), (240, 17, 82), (0, 255, 160)])
        result = self.service.preview(photo, doc)
        self.assertIsNone(ImageChops.difference(photo, result).getbbox())

    def test_channel_order_is_real_lut(self):
        values = [(b/15, r/15, g/15) for b in range(16) for g in range(16) for r in range(16)]
        self.source.write_text(build_cube("Channels", 16, values), encoding="utf-8")
        doc = self.service.load_lut(self.source)
        result = self.service.preview(Image.new("RGB", (1, 1), (51, 102, 204)), doc)
        self.assertEqual(result.getpixel((0, 0)), (204, 51, 102))

    def test_all_six_presets_round_trip(self):
        paths = list((ROOT / "built_in_luts").glob("*.cube"))
        self.assertEqual(len(paths), 6)
        for path in paths:
            with self.subTest(path=path.name):
                source = self.service.load_lut(path)
                out = self.tmp / (path.stem + ".xmp")
                self.service.export(source, out, 16, "My & Profiles", "Light < warm > 色彩")
                result = self.service.load_lut(out)
                self.assertEqual(source.title, result.title)
                self.assertEqual(result.size, 16)
                error = max(abs(a-b) for left, right in zip(source.samples, result.samples) for a,b in zip(left,right))
                self.assertLessEqual(error, 1/65535)
                back = self.tmp / (path.stem + "-back.cube")
                self.service.export(result, back, 16)
                self.assertEqual(self.service.load_lut(back).size, 16)

    def test_metadata_special_characters(self):
        out = self.tmp / "escaped.xmp"
        source = self.service.load_lut(self.source)
        self.service.export(source, out, 16, "Group & 组", "Sun < clouds >")
        root = ET.parse(out)
        ns = {"crs":"http://ns.adobe.com/camera-raw-settings/1.0/", "rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#"}
        self.assertEqual(root.find(".//crs:Group/rdf:Alt/rdf:li",ns).text, "Group & 组")
        self.assertEqual(root.find(".//crs:Description/rdf:Alt/rdf:li",ns).text, "Sun < clouds >")
        self.assertEqual(self.service.load_lut(out).title, source.title)

    def test_resampling_and_xmp_cap(self):
        out = self.tmp / "capped.xmp"
        result = self.service.export(self.service.load_lut(self.source), out, 65)
        self.assertEqual(result.size, 32)
        document = self.service.load_lut(out)
        self.assertEqual(document.size, 32)
        back = self.tmp / "33.cube"
        self.service.export(document, back, 33)
        self.assertEqual(self.service.load_lut(back).size, 33)

    def test_bom_cube(self):
        self.source.write_text(build_cube("BOM", 16, self.samples), encoding="utf-8-sig")
        self.assertEqual(self.service.load_lut(self.source).title, "BOM")

    def test_invalid_grid_domain_and_values(self):
        for content in ("LUT_3D_SIZE 16\n0 0 0", "LUT_1D_SIZE 16", "DOMAIN_MIN -1 -1 -1\nLUT_3D_SIZE 16",
                        build_cube("Invalid",16,[(float('nan'),0,0)]*4096)):
            self.source.write_text(content,encoding="utf-8")
            with self.assertRaises((ValueError, ConversionError)):
                self.service.load_lut(self.source)

    def test_failure_preserves_existing_destination(self):
        out = self.tmp / "existing.xmp"
        out.write_text("original",encoding="utf-8")
        with self.assertRaises(ConversionError):
            self.service.export(self.service.load_lut(self.source), out, 10)
        self.assertEqual(out.read_text(), "original")
        self.assertFalse(list(self.tmp.glob(".lut-*.tmp")))

    def test_photo_loading_and_monochrome(self):
        photo = self.service.load_photo(ROOT / "assets" / "coastal-light.png")
        self.assertEqual(photo.mode, "RGB")
        doc = self.service.load_lut(ROOT / "built_in_luts" / "Fuji_Monochrome.cube")
        result = self.service.preview(photo, doc)
        self.assertIsNotNone(ImageChops.difference(photo,result).getbbox())
        r,g,b = result.getpixel((200,200))
        self.assertLessEqual(max(r,g,b)-min(r,g,b), 1)

    def test_xmp_rejects_oversized_decompressed_claim(self):
        out = self.tmp / "oversized.xmp"
        self.service.export(self.service.load_lut(self.source), out, 16)
        payload = encode_zlib_base85(struct.pack('<I', 100_000_000) + zlib.compress(b'x'))
        text = re.sub(r'(crs:Table_[0-9a-f]+=")[^"]+', lambda match: match.group(1) + payload,
                      out.read_text(encoding='utf-8'))
        out.write_text(text, encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'size is out of range'):
            self.service.load_lut(out)


if __name__ == "__main__":
    unittest.main()
