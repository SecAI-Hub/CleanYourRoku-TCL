"""Fetch only configured app logos directly from the selected TCL; never run a server."""
import argparse
import io
import warnings
from build import validate_settings, ROOT
import json
from tv_connection import Connection


def png_logo(data):
    try:
        from PIL import Image
    except ImportError as error:
        raise ValueError("Install the optional hash-pinned requirements-artwork.txt for local logo conversion") from error
    with warnings.catch_warnings():
        warnings.simplefilter("error", Image.DecompressionBombWarning)
        with Image.open(io.BytesIO(data), formats=["PNG", "JPEG", "WEBP"]) as image:
            if max(image.size) > 2048 or min(image.size) < 1 or getattr(image, "n_frames", 1) != 1:
                raise ValueError("logo must be a single image of at most 2048 pixels per side")
            image.load()
            clean = Image.new("RGBA", image.size)
            clean.paste(image.convert("RGBA"))
            output = io.BytesIO()
            clean.save(output, "PNG", optimize=True)
            if output.tell() > 1048576:
                raise ValueError("converted logo exceeds 1 MiB")
            return output.getvalue()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", required=True, help="private IPv4 address of the TCL 65R635")
    args = parser.parse_args()
    settings = validate_settings(json.loads((ROOT / "launcher.json").read_text()))
    connection = Connection(args.host)
    try:
        info = connection.verify_model()
        if info["ecp-setting-mode"] != "enabled":
            raise ValueError("ECP Enabled is needed for this one-time icon fetch; Permissive is unnecessary")
        installed = connection.installed()
        for app in settings["apps"]:
            if app["id"] not in installed:
                raise ValueError("configured app is not installed: " + app["name"])
            data = png_logo(connection.read("/query/icon/" + app["id"]))
            target = ROOT / "images" / ("app_" + app["id"] + ".png")
            if target.is_symlink():
                raise ValueError("logo destination is a symbolic link")
            target.write_bytes(data)
            print("Saved local logo: " + app["name"])
    except (ValueError, OSError) as error:
        parser.exit(2, str(error) + "\n")


if __name__ == "__main__":
    main()
