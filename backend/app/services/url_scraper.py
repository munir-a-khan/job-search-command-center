"""Fetch and extract plain text from a job posting URL."""
import ipaddress
import re
import socket
from urllib.parse import urlparse

import httpx

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

MAX_CHARS = 14_000


class ScraperError(RuntimeError):
    pass


def _validate_url(url: str) -> None:
    """Block non-HTTP schemes and private/loopback IP ranges (SSRF prevention)."""
    try:
        parsed = urlparse(url)
    except Exception:
        raise ScraperError("Invalid URL")

    if parsed.scheme not in ("http", "https"):
        raise ScraperError("Only http/https URLs are allowed")

    hostname = parsed.hostname or ""
    if not hostname:
        raise ScraperError("URL has no hostname")

    # Block loopback / private ranges
    try:
        ip = ipaddress.ip_address(socket.gethostbyname(hostname))
        if ip.is_loopback or ip.is_private or ip.is_link_local or ip.is_reserved:
            raise ScraperError("Requests to internal addresses are not allowed")
    except ScraperError:
        raise
    except Exception:
        pass  # DNS failed or hostname is fine — let httpx handle it


def _strip_html(html: str) -> str:
    """Minimal HTML → text. Good enough for job postings."""
    # Remove style/script blocks
    html = re.sub(r"<style[^>]*>.*?</style>", " ", html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r"<script[^>]*>.*?</script>", " ", html, flags=re.DOTALL | re.IGNORECASE)
    # Replace block tags with newlines
    html = re.sub(r"<(?:br|p|div|li|tr|h[1-6])[^>]*>", "\n", html, flags=re.IGNORECASE)
    # Strip remaining tags
    html = re.sub(r"<[^>]+>", " ", html)
    # Decode common entities
    for ent, char in (("&amp;", "&"), ("&lt;", "<"), ("&gt;", ">"),
                      ("&nbsp;", " "), ("&quot;", '"'), ("&#39;", "'")):
        html = html.replace(ent, char)
    # Collapse whitespace
    html = re.sub(r"[ \t]+", " ", html)
    html = re.sub(r"\n{3,}", "\n\n", html)
    return html.strip()


def fetch_jd_text(url: str, timeout: float = 15.0) -> str:
    """Fetch a job posting URL and return cleaned plain text (max 14k chars)."""
    _validate_url(url)
    try:
        with httpx.Client(headers=_HEADERS, follow_redirects=True, timeout=timeout) as client:
            resp = client.get(url)
            resp.raise_for_status()
    except httpx.HTTPStatusError as e:
        raise ScraperError(f"HTTP {e.response.status_code} from {url}")
    except httpx.RequestError as e:
        raise ScraperError(f"Request failed: {e}")

    content_type = resp.headers.get("content-type", "")
    if "text" not in content_type and "html" not in content_type:
        raise ScraperError(f"Unexpected content type: {content_type}")

    text = _strip_html(resp.text)
    if len(text) < 100:
        raise ScraperError(
            "Could not extract meaningful text from this URL. "
            "The page may require JavaScript — try pasting the job description manually."
        )
    return text[:MAX_CHARS]
