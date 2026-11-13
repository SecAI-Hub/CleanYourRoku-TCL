"""Read-only, on-LAN Roku metadata/icon connection; no credentials or server."""
import ipaddress
import re
import urllib.request
import xml.etree.ElementTree as ET

NETWORKS = tuple(ipaddress.ip_network(n) for n in ("10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"))


def validate_host(value):
    address = ipaddress.ip_address(value)
    if address.version != 4 or not any(address in network for network in NETWORKS):
        raise ValueError("select the TV using its private IPv4 address")
    return str(address)


def validate_path(path):
    if path not in ("/query/device-info", "/query/apps") and not re.fullmatch(r"/query/icon/[0-9]{1,12}", path):
        raise ValueError("only device/app metadata and numeric app icons can be requested")
    return path


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


class Connection:
    def __init__(self, host):
        self.base = "http://" + validate_host(host) + ":8060"
        self.opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())

    def read(self, path):
        path = validate_path(path)
        with self.opener.open(self.base + path, timeout=5) as response:
            data = response.read(1048577)
        if len(data) > 1048576:
            raise ValueError("TV response exceeds 1 MiB")
        return data

    def verify_model(self):
        root = ET.fromstring(self.read("/query/device-info"))
        values = {node.tag: node.text for node in root}
        if values.get("vendor-name") != "TCL" or values.get("model-name") != "65R635":
            raise ValueError("endpoint did not identify as the intended TCL 65R635")
        return {key: values.get(key) for key in ("vendor-name", "model-name", "software-version", "software-build", "ecp-setting-mode")}

    def installed(self):
        return {node.get("id"): node.text for node in ET.fromstring(self.read("/query/apps")).findall("app")}
