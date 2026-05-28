#!/usr/bin/env python3
"""Fetch and extract datasheet text for KiCAD schematic review.

This script is deliberately dependency-light. PDF text extraction works when
one of these is available:

- pypdf
- PyPDF2
- pdftotext command line tool

If none is available, the script reports a clear error so the agent can ask for
extracted text or a dependency install instead of guessing from a PDF URL.
"""

from __future__ import annotations

import argparse
import html
from html.parser import HTMLParser
import hashlib
import re
import shutil
import ssl
import subprocess
import sys
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Iterable


DEFAULT_KEYWORDS = [
    "pin",
    "pin description",
    "terminal",
    "recommended operating",
    "absolute maximum",
    "typical application",
    "application information",
    "layout",
    "decoupling",
    "bypass",
    "bulk capacitor",
    "bootstrap",
    "charge pump",
    "sense",
    "current limit",
    "vref",
    "reset",
    "enable",
    "fault",
    "thermal",
    "exposed pad",
    "unused",
    "motor",
    "output",
    "supply",
    "ground",
]


def safe_name(source: str) -> str:
    parsed = urllib.parse.urlparse(source)
    base = Path(parsed.path).name if parsed.scheme else Path(source).name
    if not base:
        base = "datasheet"
    digest = hashlib.sha1(source.encode("utf-8")).hexdigest()[:10]
    stem = re.sub(r"[^A-Za-z0-9._-]+", "_", base)
    return f"{Path(stem).stem}_{digest}{Path(stem).suffix or '.pdf'}"


def _log(message: str, verbose: bool) -> None:
    if verbose:
        print(message, file=sys.stderr)


def looks_like_html(data: bytes) -> bool:
    sample = data[:4096].lstrip().lower()
    return sample.startswith(b"<!doctype html") or sample.startswith(b"<html") or b"<html" in sample[:512]


def looks_like_pdf(data: bytes) -> bool:
    return data[:16].lstrip().startswith(b"%PDF")


class _HTMLTextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.skip_depth = 0
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() in {"script", "style", "noscript"}:
            self.skip_depth += 1
            return
        if tag.lower() in {"p", "br", "div", "tr", "li", "h1", "h2", "h3", "th", "td"}:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() in {"script", "style", "noscript"} and self.skip_depth:
            self.skip_depth -= 1
            return
        if tag.lower() in {"p", "div", "tr", "li", "h1", "h2", "h3"}:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if not self.skip_depth:
            self.parts.append(data)

    def text(self) -> str:
        text = html.unescape(" ".join(self.parts))
        text = re.sub(r"[ \t\r\f\v]+", " ", text)
        text = re.sub(r"\n\s+", "\n", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()


def html_to_text(data: bytes) -> str:
    parser = _HTMLTextExtractor()
    parser.feed(data.decode("utf-8", errors="replace"))
    return parser.text()


def find_pdf_links(data: bytes, base_url: str) -> list[str]:
    text = data.decode("utf-8", errors="replace")
    candidates: list[str] = []
    patterns: Iterable[str] = [
        r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+\.pdf[^"\']*)["\']',
        r'<meta[^>]+content=["\']([^"\']+\.pdf[^"\']*)["\']',
        r'href=["\']([^"\']+\.pdf[^"\']*)["\']',
        r'(https?://[^"\'>\s]+\.pdf(?:\?[^"\'>\s]*)?)',
    ]
    for pattern in patterns:
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            url = html.unescape(match.group(1))
            absolute = urllib.parse.urljoin(base_url, url)
            if absolute not in candidates:
                candidates.append(absolute)
    return candidates


def download_url(url: str, insecure: bool = False, verbose: bool = False) -> bytes:
    _log(f"downloading: {url}", verbose)
    request = urllib.request.Request(url, headers={"User-Agent": "kicad-schematic-review/1.1"})
    context = ssl._create_unverified_context() if insecure else None
    with urllib.request.urlopen(request, timeout=30, context=context) as response:
        return response.read()


def cache_url_datasheet(
    source: str,
    target: Path,
    insecure: bool = False,
    verbose: bool = False,
) -> Path:
    data = download_url(source, insecure=insecure, verbose=verbose)
    if looks_like_html(data):
        _log("downloaded HTML wrapper; searching for linked PDF datasheet", verbose)
        for pdf_url in find_pdf_links(data, source):
            pdf_data = download_url(pdf_url, insecure=insecure, verbose=verbose)
            if looks_like_pdf(pdf_data):
                pdf_target = target.with_name(safe_name(pdf_url))
                pdf_target.write_bytes(pdf_data)
                _log(f"cached resolved PDF: {pdf_target}", verbose)
                return pdf_target
        _log("no downloadable PDF link found in HTML wrapper; caching HTML text source", verbose)
    target.write_bytes(data)
    _log(f"cached: {target}", verbose)
    return target


def fetch(
    source: str,
    cache_dir: Path,
    insecure: bool = False,
    offline: bool = False,
    verbose: bool = False,
) -> Path:
    cache_dir.mkdir(parents=True, exist_ok=True)
    parsed = urllib.parse.urlparse(source)
    if parsed.scheme in {"http", "https"}:
        target = cache_dir / safe_name(source)
        if target.exists() and target.stat().st_size > 0:
            data = target.read_bytes()
            if looks_like_html(data) and not offline:
                _log(f"cache hit is HTML wrapper: {target}", verbose)
                resolved = cache_url_datasheet(source, target, insecure=insecure, verbose=verbose)
                if resolved != target or looks_like_pdf(resolved.read_bytes()):
                    return resolved
            _log(f"cache hit: {target}", verbose)
            return target
        if offline:
            raise FileNotFoundError(f"Datasheet is not in cache and --offline was set: {source}")
        return cache_url_datasheet(source, target, insecure=insecure, verbose=verbose)

    path = Path(source).expanduser()
    target = cache_dir / safe_name(str(path.resolve()))
    if target.exists() and target.stat().st_size > 0:
        _log(f"cache hit: {target}", verbose)
        return target
    if not path.exists():
        raise FileNotFoundError(f"Datasheet path does not exist: {source}")
    if path.resolve() != target.resolve():
        _log(f"copying local datasheet: {path}", verbose)
        shutil.copyfile(path, target)
        _log(f"cached: {target}", verbose)
    return target


def extract_with_pypdf(path: Path) -> str | None:
    try:
        from pypdf import PdfReader  # type: ignore
    except ImportError:
        try:
            from PyPDF2 import PdfReader  # type: ignore
        except ImportError:
            return None

    reader = PdfReader(str(path))
    pages = []
    for index, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        pages.append(f"\n\n--- Page {index} ---\n{text}")
    return "".join(pages).strip()


def extract_with_pdftotext(path: Path) -> str | None:
    if not shutil.which("pdftotext"):
        return None
    result = subprocess.run(
        ["pdftotext", "-layout", str(path), "-"],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def extract_text(path: Path) -> str:
    suffix = path.suffix.lower()
    data = path.read_bytes()
    if suffix in {".html", ".htm"} or looks_like_html(data):
        return html_to_text(data)
    if suffix in {".txt", ".md"}:
        return data.decode("utf-8", errors="replace")
    if suffix != ".pdf":
        raise ValueError(f"Unsupported datasheet format: {path.suffix}")

    text = extract_with_pypdf(path)
    if text:
        return text
    text = extract_with_pdftotext(path)
    if text:
        return text
    raise RuntimeError(
        "No PDF text extractor available. Install pypdf/PyPDF2 or pdftotext, "
        "or provide extracted datasheet text."
    )


def normalize_space(text: str) -> str:
    return re.sub(r"[ \t]+", " ", text).strip()


def keyword_sections(text: str, keywords: list[str], context_chars: int) -> str:
    output = ["# Datasheet Keyword Reading Map\n"]
    lower = text.lower()
    for keyword in keywords:
        pattern = keyword.lower()
        matches = [match.start() for match in re.finditer(re.escape(pattern), lower)]
        if not matches:
            continue
        output.append(f"\n## {keyword}\n")
        selected: list[int] = []
        for start in matches:
            if any(abs(start - existing) < context_chars for existing in selected):
                continue
            selected.append(start)
            if len(selected) >= 8:
                break
        for start in selected:
            left = max(0, start - context_chars)
            right = min(len(text), start + len(keyword) + context_chars)
            snippet = normalize_space(text[left:right])
            output.append(f"- ...{snippet}...\n")
    return "".join(output)


def command_fetch(args: argparse.Namespace) -> None:
    target = fetch(
        args.source,
        args.cache_dir,
        insecure=args.insecure,
        offline=args.offline,
        verbose=args.verbose,
    )
    print(target)


def command_extract(args: argparse.Namespace) -> None:
    text = extract_text(args.path)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
        print(args.out)
    else:
        print(text)


def command_keywords(args: argparse.Namespace) -> None:
    text = args.text_file.read_text(encoding="utf-8", errors="replace")
    keywords = args.keyword or DEFAULT_KEYWORDS
    result = keyword_sections(text, keywords, args.context_chars)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(result, encoding="utf-8")
        print(args.out)
    else:
        print(result)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Datasheet helper for KiCAD schematic review")
    subparsers = parser.add_subparsers(dest="command", required=True)

    fetch_parser = subparsers.add_parser("fetch", help="Cache a URL or local datasheet")
    fetch_parser.add_argument("source", help="HTTP(S) URL or local path")
    fetch_parser.add_argument("--cache-dir", type=Path, required=True)
    fetch_parser.add_argument(
        "--insecure",
        action="store_true",
        help="Skip TLS certificate verification when the local certificate store is broken",
    )
    fetch_parser.add_argument(
        "--offline",
        action="store_true",
        help="Only use an existing cached datasheet; fail instead of downloading on a cache miss",
    )
    fetch_parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print cache-hit/download details to stderr while keeping stdout as the cached path",
    )
    fetch_parser.set_defaults(func=command_fetch)

    extract_parser = subparsers.add_parser("extract", help="Extract text from a cached datasheet")
    extract_parser.add_argument("path", type=Path)
    extract_parser.add_argument("--out", type=Path)
    extract_parser.set_defaults(func=command_extract)

    keyword_parser = subparsers.add_parser("keywords", help="Create a compact keyword reading map")
    keyword_parser.add_argument("text_file", type=Path)
    keyword_parser.add_argument("--out", type=Path)
    keyword_parser.add_argument("--keyword", action="append", help="Keyword to search; can be repeated")
    keyword_parser.add_argument("--context-chars", type=int, default=650)
    keyword_parser.set_defaults(func=command_keywords)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    try:
        args.func(args)
    except Exception as exc:
        print(f"datasheet_tool error: {exc}", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
