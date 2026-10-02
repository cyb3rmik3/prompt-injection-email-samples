#!/usr/bin/env python3
"""Validate every sample in samples/ before it is merged.

Checks:
  * file name follows NN_intent_evasion.eml
  * message parses and has From, To, Subject, Date, Message-ID
  * X-Injection-Test header is present with intent, evasion and control
  * every domain in addresses and URLs is reserved (RFC 2606 / RFC 6761),
    including inside Base64 payloads, so no sample can reach a real mailbox
    or a real server

Usage: python scripts/validate_samples.py [samples_dir]
"""

import base64
import binascii
import email
import email.policy
import re
import sys
from pathlib import Path

REQUIRED_HEADERS = ("From", "To", "Subject", "Date", "Message-ID", "X-Injection-Test")
REQUIRED_KEYS = ("intent", "evasion", "control")
NAME_RE = re.compile(r"^\d{2,3}_[a-z0-9]+_[a-z0-9_]+\.eml$")
ADDR_DOMAIN_RE = re.compile(r"[A-Za-z0-9._%+-]+@([A-Za-z0-9.-]+\.[A-Za-z]{2,})")
URL_HOST_RE = re.compile(r"https?://([A-Za-z0-9.-]+)", re.I)
B64_BLOCK_RE = re.compile(r"(?:[A-Za-z0-9+/]{16,}={0,2}\s*){2,}|[A-Za-z0-9+/]{40,}={0,2}")
RESERVED_TLDS = ("example", "test", "invalid", "localhost")
RESERVED_DOMAINS = ("example.com", "example.net", "example.org")


def is_reserved(host: str) -> bool:
    host = host.lower().rstrip(".")
    if host.rsplit(".", 1)[-1] in RESERVED_TLDS:
        return True
    return any(host == d or host.endswith("." + d) for d in RESERVED_DOMAINS)


def decoded_blobs(text: str) -> list[str]:
    """Best-effort decode of Base64 blocks embedded in a body."""
    out = []
    for block in B64_BLOCK_RE.findall(text):
        # Try the block as one wrapped payload; if that fails, each line on its own.
        whole = _b64(block)
        if whole is not None:
            out.append(whole)
        else:
            out += [s for s in map(_b64, block.split()) if s is not None]
    return out


def _b64(candidate: str) -> str | None:
    compact = re.sub(r"\s+", "", candidate)
    compact += "=" * (-len(compact) % 4)
    try:
        return base64.b64decode(compact, validate=True).decode("utf-8")
    except (binascii.Error, UnicodeDecodeError):
        return None


def check(path: Path) -> list[str]:
    errors = []
    if not NAME_RE.match(path.name):
        errors.append("file name should look like NN_intent_evasion.eml")

    raw = path.read_bytes()
    msg = email.message_from_bytes(raw, policy=email.policy.default)

    for h in REQUIRED_HEADERS:
        if not msg.get(h):
            errors.append(f"missing header: {h}")

    meta = msg.get("X-Injection-Test", "")
    fields = dict(
        part.strip().split("=", 1) for part in str(meta).split(";") if "=" in part
    )
    for key in REQUIRED_KEYS:
        if not fields.get(key):
            errors.append(f"X-Injection-Test missing '{key}='")
    if fields.get("control") not in (None, "true", "false"):
        errors.append("X-Injection-Test control must be true or false")

    # Scan headers and every decoded body part, so encoded parts are checked too.
    texts = [raw.decode("utf-8", errors="replace")]
    for part in msg.walk():
        if part.get_content_maintype() == "text":
            try:
                texts.append(part.get_content())
            except Exception as exc:  # noqa: BLE001
                errors.append(f"cannot decode body part: {exc}")
    texts += [blob for text in list(texts) for blob in decoded_blobs(text)]
    hosts = set()
    for text in texts:
        hosts.update(ADDR_DOMAIN_RE.findall(text))
        hosts.update(URL_HOST_RE.findall(text))
    for host in sorted(hosts):
        if not is_reserved(host):
            errors.append(f"non-reserved domain: {host} (use .example / example.com)")

    return errors


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).parent.parent / "samples")
    files = sorted(root.glob("*.eml"))
    if not files:
        print(f"no .eml files found in {root}")
        return 1

    failed = 0
    for path in files:
        errors = check(path)
        if errors:
            failed += 1
            print(f"FAIL {path.name}")
            for e in errors:
                print(f"     - {e}")
        else:
            print(f"ok   {path.name}")

    print(f"\n{len(files) - failed}/{len(files)} samples passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
