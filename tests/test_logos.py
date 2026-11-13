import importlib.util
import io
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from pull_logos import png_logo


@unittest.skipUnless(importlib.util.find_spec("PIL"), "optional artwork tools are not installed")
class LogoBoundaryTests(unittest.TestCase):
    def test_webp_logo_is_converted_to_local_png(self):
        from PIL import Image
        source = io.BytesIO()
        Image.new("RGB", (48, 32), "blue").save(source, "WEBP")
        result = png_logo(source.getvalue())
        self.assertTrue(result.startswith(b"\x89PNG\r\n\x1a\n"))
        with Image.open(io.BytesIO(result)) as image:
            self.assertEqual(image.size, (48, 32))

    def test_input_text_metadata_is_not_carried_into_output(self):
        from PIL import Image, PngImagePlugin
        metadata = PngImagePlugin.PngInfo()
        metadata.add_text("private-note", "must not be copied")
        source = io.BytesIO()
        Image.new("RGB", (16, 16), "red").save(source, "PNG", pnginfo=metadata)
        with Image.open(io.BytesIO(png_logo(source.getvalue()))) as image:
            self.assertNotIn("private-note", image.info)

    def test_oversized_or_invalid_logo_is_rejected(self):
        from PIL import Image
        source = io.BytesIO()
        Image.new("RGB", (2049, 1), "red").save(source, "PNG")
        with self.assertRaises(ValueError):
            png_logo(source.getvalue())
        with self.assertRaises((ValueError, OSError)):
            png_logo(b"not an image")


if __name__ == "__main__":
    unittest.main()
