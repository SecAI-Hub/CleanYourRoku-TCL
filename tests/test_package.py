import copy
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import build
from tv_connection import validate_host, validate_path, NoRedirect


class PackageSecurityTests(unittest.TestCase):
    def setUp(self):
        self.settings = json.loads((ROOT / "launcher.json").read_text())

    def test_current_configuration_is_valid(self):
        result = build.validate_settings(self.settings)
        self.assertEqual([app["id"] for app in result["apps"]], ["12", "2285"])

    def test_external_resource_or_unexpected_config_fields_are_rejected(self):
        for key, value in (("background_url", "https://example.com/image.png"), ("api_key", "example")):
            settings = copy.deepcopy(self.settings)
            settings[key] = value
            with self.assertRaises(ValueError):
                build.validate_settings(settings)
        self.settings["apps"][0]["icon"] = "https://example.com/icon.png"
        with self.assertRaises(ValueError):
            build.validate_settings(self.settings)

    def test_non_app_targets_duplicates_and_control_characters_are_rejected(self):
        for identifier in ("../plugin_install", "dev", "tvinput.hdmi1", "12?x=1", "", "1" * 13):
            settings = copy.deepcopy(self.settings)
            settings["apps"][0]["id"] = identifier
            with self.assertRaises(ValueError):
                build.validate_settings(settings)
        self.settings["apps"][1]["id"] = "12"
        with self.assertRaises(ValueError):
            build.validate_settings(self.settings)
        self.settings["apps"][1]["id"] = "2285"
        self.settings["apps"][0]["name"] = "Netflix\nextra"
        with self.assertRaises(ValueError):
            build.validate_settings(self.settings)

    def test_packaging_excludes_unlisted_secrets_and_legacy_content(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            names = list(build.APP_SOURCES) + ["LICENSE", "launcher.json"] + ["images/" + n for n in build.ARTWORK]
            for name in names:
                (root / name).parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / name, root / name)
            for name in (".env", "developer-password.txt", "mychannel.json", "scripts/rokuremote.py", "images/private-photo.png"):
                (root / name).parent.mkdir(parents=True, exist_ok=True)
                (root / name).write_text("must never ship")
            record = build.build(root)
            with zipfile.ZipFile(root / "out" / record["file"]) as archive:
                self.assertIsNone(archive.testzip())
                self.assertFalse(any("private" in n or "password" in n or n.startswith("scripts/") for n in archive.namelist()))
                self.assertNotIn("mychannel.json", archive.namelist())
                self.assertNotIn(".env", archive.namelist())
                settings = json.loads(archive.read("appsettings.json"))
                self.assertTrue(all(a["icon"].startswith("pkg:/images/") for a in settings["apps"]))
            second = build.build(root)
            self.assertEqual(record["sha256"], second["sha256"])

    def test_new_network_component_or_remote_uri_fails_build_guard(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for name in build.APP_SOURCES:
                (root / name).parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / name, root / name)
            target = root / "components/Launcher.brs"
            original = target.read_text()
            for addition in ('\nnetwork = CreateObject("roUrlTransfer")\n', '\nnetwork = createobject ( "roUrlTransfer" )\n', '\nnetwork = CreateObject(componentName)\n', '\nurl = "https://example.com"\n'):
                target.write_text(original + addition)
                with self.assertRaises(ValueError):
                    build.validate_application_sources(root)

    def test_symlinked_application_source_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for name in build.APP_SOURCES:
                (root / name).parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / name, root / name)
            target = root / "source/main.brs"
            target.unlink()
            target.symlink_to(ROOT / "source/main.brs")
            with self.assertRaises(ValueError):
                build.validate_application_sources(root)

    def test_local_connector_rejects_external_hosts_and_write_endpoints(self):
        for address in ("127.0.0.1", "0.0.0.0", "8.8.8.8", "169.254.0.1", "::1", "example.com"):
            with self.assertRaises(ValueError):
                validate_host(address)
        self.assertEqual(validate_host("192.168.1.50"), "192.168.1.50")
        for path in ("/keypress/Power", "/launch/dev", "/query/icon/../x", "http://example.com"):
            with self.assertRaises(ValueError):
                validate_path(path)
        self.assertEqual(validate_path("/query/icon/12"), "/query/icon/12")
        self.assertIsNone(NoRedirect().redirect_request(None, None, 302, "", {}, "http://example.com"))


if __name__ == "__main__":
    unittest.main()
