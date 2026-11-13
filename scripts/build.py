"""Validate configuration and build an allowlisted, deterministic Roku package."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import re
import struct
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parent.parent
APP_SOURCES = ("manifest", "source/main.brs", "components/HomeScene.xml", "components/HomeScene.brs",
               "components/Launcher.xml", "components/Launcher.brs", "components/AppTile.xml", "components/AppTile.brs")
ARTWORK = ("clean_icon_fhd.png", "clean_icon_hd.png", "clean_splash_fhd.png", "clean_splash_hd.png",
           "clean_splash_sd.png", "clean_background.png", "clean_surface.png", "clean_focus.png", "clean_placeholder.png")
ALLOWED_COMPONENTS = {"roSGScreen", "roMessagePort", "roSGNode", "roDateTime", "roAppManager"}
SETTINGS_KEYS = {"title", "show_clock", "show_date", "clock_format", "accent_color", "apps"}


def text(value, label, limit=40):
    if not isinstance(value, str) or not value.strip() or len(value) > limit or any(ord(c) < 32 for c in value):
        raise ValueError(label + " must be nonempty plain text of at most " + str(limit) + " characters")
    return value


def validate_settings(data):
    if not isinstance(data, dict) or set(data) != SETTINGS_KEYS:
        raise ValueError("launcher.json must contain exactly the documented settings")
    result = copy.deepcopy(data)
    text(result["title"], "title")
    if type(result["show_clock"]) is not bool or type(result["show_date"]) is not bool:
        raise ValueError("clock/date switches must be booleans")
    if result["clock_format"] not in ("12h", "24h"):
        raise ValueError("clock_format must be 12h or 24h")
    if not isinstance(result["accent_color"], str) or not re.fullmatch(r"0x[0-9A-Fa-f]{8}", result["accent_color"]):
        raise ValueError("accent_color must be a Roku RGBA color such as 0xA9C7FFFF")
    apps = result["apps"]
    if not isinstance(apps, list) or not 1 <= len(apps) <= 12:
        raise ValueError("configure between 1 and 12 apps")
    seen = set()
    for app in apps:
        if not isinstance(app, dict) or set(app) != {"name", "id"}:
            raise ValueError("each app must contain only name and id; resource URLs are not configurable")
        text(app["name"], "app name")
        if not isinstance(app["id"], str) or not re.fullmatch(r"[0-9]{1,12}", app["id"]):
            raise ValueError("app id must be 1-12 digits")
        if app["id"] in seen:
            raise ValueError("duplicate app id")
        seen.add(app["id"])
    return result


def validate_application_sources(root):
    for name in APP_SOURCES:
        path = root / name
        if path.is_symlink() or not path.resolve().is_relative_to(root.resolve()):
            raise ValueError("linked or out-of-root application source " + name)
        content = path.read_text()
        if re.search(r"(?:https?|wss?|ftp)://", content, re.I):
            raise ValueError("external resource URI in " + name)
        for creation in re.finditer(r'\bCreateObject\s*\(\s*', content, re.I):
            literal = re.match(r'"([^\"]+)"', content[creation.end():])
            if literal is None:
                raise ValueError("dynamic component creation in " + name)
            component = literal.group(1)
            if component not in ALLOWED_COMPONENTS:
                raise ValueError("unreviewed BrightScript component " + component + " in " + name)
        if re.search(r"\b(?:Eval|Run)\s*\(", content, re.I):
            raise ValueError("dynamic code execution in " + name)
        if name.endswith(".xml"):
            document = ET.fromstring(content)
            for node in document.iter():
                for key, value in node.attrib.items():
                    if key.lower().endswith("uri") and (not value.startswith("pkg:/") or ".." in value):
                        raise ValueError("non-local resource attribute in " + name)


def generated_settings(root):
    config_path = root / "launcher.json"
    if config_path.is_symlink() or not config_path.resolve().is_relative_to(root.resolve()):
        raise ValueError("linked or out-of-root configuration")
    settings = validate_settings(json.loads(config_path.read_text()))
    for app in settings["apps"]:
        icon = "images/clean_placeholder.png"
        candidate = root / "images" / ("app_" + app["id"] + ".png")
        if candidate.exists():
            if candidate.is_symlink() or not candidate.resolve().is_relative_to(root.resolve()):
                raise ValueError("linked or out-of-root local logo")
            data = candidate.read_bytes()
            if len(data) < 24 or not data.startswith(b"\x89PNG\r\n\x1a\n"):
                raise ValueError("invalid local PNG logo")
            if len(data) > 1048576 or not all(1 <= side <= 2048 for side in struct.unpack(">II", data[16:24])):
                raise ValueError("oversized local logo")
            icon = candidate.relative_to(root).as_posix()
        app["icon"] = "pkg:/" + icon
    return settings


def package_files(root, settings):
    names = set(APP_SOURCES) | {"LICENSE", "appsettings.json"}
    names.update("images/" + name for name in ARTWORK)
    names.update(app["icon"][5:] for app in settings["apps"])
    for name in names:
        path = root / name
        if path.is_symlink() or not path.is_file() or not path.resolve().is_relative_to(root.resolve()):
            raise ValueError("missing, linked, or out-of-root package asset " + name)
    return sorted(names)


def build(root=ROOT, out=None):
    root = Path(root)
    out = Path(out) if out else root / "out"
    validate_application_sources(root)
    settings = generated_settings(root)
    (root / "appsettings.json").write_text(json.dumps(settings, ensure_ascii=False, indent=2) + "\n")
    names = package_files(root, settings)
    manifest = (root / "manifest").read_text()
    if not manifest.endswith("\n"):
        raise ValueError("manifest needs a final newline")
    for uri in re.findall(r"=pkg:/([^\n]+)", manifest):
        if uri not in names:
            raise ValueError("manifest asset is outside package allowlist: " + uri)
    for name, size in (("clean_icon_fhd.png", (540, 405)), ("clean_icon_hd.png", (290, 218))):
        data = (root / "images" / name).read_bytes()
        if data[:8] != b"\x89PNG\r\n\x1a\n" or struct.unpack(">II", data[16:24]) != size:
            raise ValueError("invalid channel icon " + name)
    out.mkdir(parents=True, exist_ok=True)
    destination = out / "cleanyourroku-tcl.zip"
    with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name in names:
            info = zipfile.ZipInfo(name, (2026, 11, 13, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, (root / name).read_bytes())
    record = {"file": destination.name, "bytes": destination.stat().st_size,
              "sha256": hashlib.sha256(destination.read_bytes()).hexdigest(),
              "files": {name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in names}}
    (out / "package-manifest.json").write_text(json.dumps(record, indent=2) + "\n")
    return record


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    print(json.dumps({k: v for k, v in build(out=args.out).items() if k != "files"}))
