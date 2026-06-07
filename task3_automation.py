"""
CodeAlpha Internship — Task 3: Task Automation with Python Scripts
Author  : [Your Name]
Purpose : Three production-quality automation utilities in one file:
            1. File Organiser   — move .jpg / .png / .pdf etc. to sorted folders
            2. Email Extractor  — extract all emails from a .txt file
            3. Web Title Scraper— fetch and save the <title> of any URL
          Run the script and pick from the menu, or import individual
          functions into your own projects.
"""

import os
import re
import shutil
from pathlib import Path
from datetime import datetime

# ── Optional third-party imports (graceful fallback) ──────────────────────────
try:
    import requests
    from bs4 import BeautifulSoup
    WEB_AVAILABLE = True
except ImportError:
    WEB_AVAILABLE = False


# ══════════════════════════════════════════════════════════════════════════════
#  AUTOMATION 1 — File Organiser
# ══════════════════════════════════════════════════════════════════════════════
#  Groups files in a source directory into sub-folders by extension.
#  Mapping is customisable; unknown extensions go to "Others".
# ─────────────────────────────────────────────────────────────────────────────
EXTENSION_MAP: dict[str, str] = {
    # Images
    ".jpg": "Images", ".jpeg": "Images", ".png": "Images",
    ".gif": "Images", ".bmp": "Images", ".svg": "Images", ".webp": "Images",
    # Documents
    ".pdf": "Documents", ".docx": "Documents", ".doc": "Documents",
    ".xlsx": "Documents", ".xls": "Documents", ".pptx": "Documents",
    ".txt": "Documents", ".csv": "Documents",
    # Videos
    ".mp4": "Videos", ".mov": "Videos", ".avi": "Videos", ".mkv": "Videos",
    # Audio
    ".mp3": "Audio", ".wav": "Audio", ".flac": "Audio",
    # Code
    ".py": "Code", ".js": "Code", ".html": "Code",
    ".css": "Code", ".json": "Code", ".xml": "Code",
    # Archives
    ".zip": "Archives", ".tar": "Archives", ".gz": "Archives", ".rar": "Archives",
}


def organise_files(source_dir: str, dest_dir: str | None = None,
                   dry_run: bool = False) -> dict:
    """
    Move every file in *source_dir* into category sub-folders.

    Parameters
    ----------
    source_dir : directory to scan (non-recursive by default)
    dest_dir   : where to create sub-folders (defaults to source_dir)
    dry_run    : if True, print what would happen without moving anything

    Returns
    -------
    dict with keys 'moved', 'skipped', 'errors' — each a list of strings
    """
    source = Path(source_dir).resolve()
    dest   = Path(dest_dir).resolve() if dest_dir else source

    if not source.exists():
        raise FileNotFoundError(f"Source directory not found: {source}")

    dest.mkdir(parents=True, exist_ok=True)

    result: dict[str, list[str]] = {"moved": [], "skipped": [], "errors": []}

    for file in source.iterdir():
        if not file.is_file():
            continue

        ext      = file.suffix.lower()
        category = EXTENSION_MAP.get(ext, "Others")
        target   = dest / category / file.name

        # Avoid overwriting — append timestamp if collision
        if target.exists():
            stem    = file.stem
            ts      = datetime.now().strftime("%H%M%S%f")
            target  = dest / category / f"{stem}_{ts}{ext}"

        if dry_run:
            result["skipped"].append(f"[DRY RUN] {file.name}  →  {category}/")
        else:
            try:
                (dest / category).mkdir(exist_ok=True)
                shutil.move(str(file), str(target))
                result["moved"].append(f"{file.name}  →  {category}/")
            except Exception as exc:
                result["errors"].append(f"{file.name}: {exc}")

    return result


def run_file_organiser() -> None:
    print("\n─── File Organiser ───────────────────────────────")
    source = input("  Source folder path : ").strip()
    dest   = input("  Destination folder (Enter = same as source): ").strip() or None
    dry    = input("  Dry run? [y/n]: ").strip().lower() == "y"

    try:
        report = organise_files(source, dest, dry_run=dry)
    except FileNotFoundError as e:
        print(f"  ❌  {e}")
        return

    total = len(report["moved"]) + len(report["skipped"])
    print(f"\n  {'[DRY RUN] ' if dry else ''}Processed {total} file(s).\n")
    for line in report["moved"] + report["skipped"]:
        print(f"    ✅  {line}")
    for line in report["errors"]:
        print(f"    ❌  {line}")


# ══════════════════════════════════════════════════════════════════════════════
#  AUTOMATION 2 — Email Extractor
# ══════════════════════════════════════════════════════════════════════════════
#  Reads any text file, extracts every valid email address (case-insensitive,
#  de-duplicated), and writes them one-per-line to an output file.
# ─────────────────────────────────────────────────────────────────────────────

# RFC-5321-ish email regex — handles most real-world addresses
_EMAIL_REGEX = re.compile(
    r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}",
    re.IGNORECASE,
)


def extract_emails(input_path: str, output_path: str) -> list[str]:
    """
    Extract unique email addresses from *input_path* and write to *output_path*.

    Returns
    -------
    Sorted list of unique email addresses found.
    """
    text   = Path(input_path).read_text(encoding="utf-8", errors="ignore")
    emails = sorted({m.lower() for m in _EMAIL_REGEX.findall(text)})

    Path(output_path).write_text("\n".join(emails) + ("\n" if emails else ""),
                                 encoding="utf-8")
    return emails


def run_email_extractor() -> None:
    print("\n─── Email Extractor ──────────────────────────────")
    inp = input("  Input  .txt file path : ").strip()
    out = input("  Output file path      : ").strip()

    if not Path(inp).is_file():
        print(f"  ❌  File not found: {inp}")
        return

    try:
        emails = extract_emails(inp, out)
    except Exception as exc:
        print(f"  ❌  Error: {exc}")
        return

    print(f"\n  ✅  Found {len(emails)} unique email(s). Saved to '{out}'.")
    if emails:
        preview = emails[:10]
        for e in preview:
            print(f"    • {e}")
        if len(emails) > 10:
            print(f"    … and {len(emails) - 10} more.")


# ══════════════════════════════════════════════════════════════════════════════
#  AUTOMATION 3 — Web Title Scraper
# ══════════════════════════════════════════════════════════════════════════════
#  Fetches the <title> tag (and optional meta-description) from a URL,
#  then appends the result to a plain-text log file.
# ─────────────────────────────────────────────────────────────────────────────
SCRAPE_LOG = "scraped_titles.txt"
HEADERS    = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    )
}


def scrape_title(url: str, timeout: int = 10) -> dict:
    """
    Fetch *url* and return a dict with keys:
      url, title, description, status_code, scraped_at
    Raises requests.RequestException on network errors.
    """
    if not WEB_AVAILABLE:
        raise ImportError("Install 'requests' and 'beautifulsoup4' to use this feature.")

    # Ensure scheme present
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    response = requests.get(url, headers=HEADERS, timeout=timeout)
    response.raise_for_status()

    soup        = BeautifulSoup(response.text, "html.parser")
    title_tag   = soup.find("title")
    title       = title_tag.get_text(strip=True) if title_tag else "N/A"

    meta_desc   = soup.find("meta", attrs={"name": re.compile("description", re.I)})
    description = (meta_desc.get("content", "").strip()
                   if meta_desc else "N/A")

    return {
        "url"        : url,
        "title"      : title,
        "description": description,
        "status_code": response.status_code,
        "scraped_at" : datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


def save_scrape_result(data: dict, log_file: str = SCRAPE_LOG) -> None:
    line = (f"[{data['scraped_at']}]  {data['url']}\n"
            f"  Title      : {data['title']}\n"
            f"  Description: {data['description']}\n"
            f"  Status     : {data['status_code']}\n"
            f"{'─' * 60}\n")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(line)


def run_web_scraper() -> None:
    print("\n─── Web Title Scraper ────────────────────────────")
    if not WEB_AVAILABLE:
        print("  ❌  Missing libraries. Run:")
        print("       pip install requests beautifulsoup4")
        return

    url = input("  Enter URL (e.g. https://example.com): ").strip()
    if not url:
        print("  ⚠  No URL entered.")
        return

    try:
        data = scrape_title(url)
    except Exception as exc:
        print(f"  ❌  Failed to scrape: {exc}")
        return

    save_scrape_result(data)
    print(f"\n  ✅  Scraped successfully!")
    print(f"     Title      : {data['title']}")
    print(f"     Description: {data['description'][:80]}…"
          if len(data["description"]) > 80 else
          f"     Description: {data['description']}")
    print(f"     Saved to   : '{SCRAPE_LOG}'")


# ══════════════════════════════════════════════════════════════════════════════
#  Main menu
# ══════════════════════════════════════════════════════════════════════════════
def main() -> None:
    menu = {
        "1": ("File Organiser",    run_file_organiser),
        "2": ("Email Extractor",   run_email_extractor),
        "3": ("Web Title Scraper", run_web_scraper),
        "0": ("Exit",              None),
    }

    while True:
        print("\n" + "=" * 50)
        print(f"{'🤖  TASK AUTOMATION TOOLKIT':^50}")
        print("=" * 50)
        for key, (label, _) in menu.items():
            print(f"  [{key}]  {label}")

        choice = input("\n  Select option: ").strip()

        if choice == "0":
            print("\n  👋  Goodbye!\n")
            break
        elif choice in menu and menu[choice][1]:
            menu[choice][1]()
        else:
            print("  ⚠  Invalid option.")

        input("\n  Press Enter to return to menu…")


if __name__ == "__main__":
    main()
