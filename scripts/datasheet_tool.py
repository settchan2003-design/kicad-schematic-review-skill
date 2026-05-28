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
import hashlib
import re
import shutil
import ssl
import subprocess
import sys
import urllib.parse
import urllib.request
from pathlib import Path


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
            _log(f"cache hit: {target}", verbose)
            return target
        if offline:
            raise FileNotFoundError(f"Datasheet is not in cache and --offline was set: {source}")
        _log(f"downloading: {source}", verbose)
        request = urllib.request.Request(source, headers={"User-Agent": "kicad-schematic-review/1.0"})
        context = ssl._create_unverified_context() if insecure else None
        with urllib.request.urlopen(request, timeout=30, context=context) as response:
            target.write_bytes(response.read())
        _log(f"cached: {target}", verbose)
        return target

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
    if suffix in {".txt", ".md", ".html", ".htm"}:
        return path.read_text(encoding="utf-8", errors="replace")
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
