import urllib.parse

from lxml import etree
from tg import config

BISQUE_CALLBACK_SERVICE_TYPES = (
    "data_service",
    "module_service",
    "engine_service",
    "image_service",
    "blob_service",
)


def configured_bisque_roots(extra_roots=None, app_config=None):
    app_config = app_config or config
    roots = []
    for key in ("docker.callback_url", "bisque.server"):
        value = app_config.get(key, "")
        if value and value not in roots:
            roots.append(value)
    for value in extra_roots or ():
        if value and value not in roots:
            roots.append(value)
    return roots


def url_origin(url):
    parts = urllib.parse.urlparse(url)
    if not parts.scheme or not parts.netloc:
        return None
    scheme = parts.scheme.lower()
    port = parts.port
    if port is None and scheme == "http":
        port = 80
    elif port is None and scheme == "https":
        port = 443
    return (scheme, parts.hostname.lower() if parts.hostname else "", port)


def same_origin_host(left, right):
    return left is not None and right is not None and left[:2] == right[:2]


def is_bisque_service_path(path, service_types=BISQUE_CALLBACK_SERVICE_TYPES):
    return any(
        path == "/" + service_type or path.startswith("/" + service_type + "/")
        for service_type in service_types
    )


def remap_bisque_service_url(url, roots, target_root, allow_same_host=False):
    parts = urllib.parse.urlparse(url)
    if not parts.scheme or not parts.netloc:
        return url
    if not is_bisque_service_path(parts.path):
        return url

    origin = url_origin(url)
    root_origins = {url_origin(root) for root in roots}
    root_origins.discard(None)
    if origin not in root_origins and not (
        allow_same_host and any(same_origin_host(origin, root) for root in root_origins)
    ):
        return url

    target = urllib.parse.urlparse(target_root.rstrip("/"))
    if not target.scheme or not target.netloc or origin == url_origin(target_root):
        return url

    return urllib.parse.urlunparse(
        (target.scheme, target.netloc, parts.path, "", parts.query, parts.fragment)
    )


def remap_bisque_service_tree(
    root,
    roots,
    target_root,
    allow_same_host=False,
    attributes=("uri", "value", "owner", "type"),
):
    rewritten = 0
    for node in root.iter():
        for attribute in attributes:
            value = node.get(attribute)
            if not value:
                continue
            remapped = remap_bisque_service_url(value, roots, target_root, allow_same_host)
            if remapped != value:
                node.set(attribute, remapped)
                rewritten += 1
    return rewritten


def remap_bisque_service_xml(value, roots, target_root, allow_same_host=False):
    if not value:
        return value, 0

    is_bytes = isinstance(value, bytes)
    try:
        root = etree.fromstring(value)
    except (TypeError, etree.XMLSyntaxError, ValueError):
        return value, 0

    rewritten = remap_bisque_service_tree(root, roots, target_root, allow_same_host)
    if not rewritten:
        return value, 0

    remapped = etree.tostring(root, encoding="utf-8" if is_bytes else "unicode")
    return remapped, rewritten
