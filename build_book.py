#!/usr/bin/env python3
"""
build_book.py — pipeline de génération PDF / EPUB pour Grogle Failure.

Usage :
    uv run python build_book.py [OPTIONS]

Options :
    --lang fr|en|both   Version(s) à générer (défaut : both)
    --fmt  pdf|epub|all Formats de sortie   (défaut : all)
    --cover-only        Regénère seulement les couvertures
    -v, --verbose       Affiche les commandes pandoc complètes
"""

from __future__ import annotations

import argparse
import math
import re
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path

import yaml  # pyyaml


# ---------------------------------------------------------------------------
# Chemins
# ---------------------------------------------------------------------------
ROOT = Path(__file__).parent
CONFIG = ROOT / "book.toml"

FONT_SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
FONT_SANS  = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
def load_config() -> dict:
    with open(CONFIG, "rb") as fh:
        return tomllib.load(fh)


# ---------------------------------------------------------------------------
# Collecte et tri des chapitres
# ---------------------------------------------------------------------------
LOG_RE = re.compile(r"Log #(\d+)\.md$", re.IGNORECASE)
LOG_LETTER_RE = re.compile(r"Log ([A-Z])\.md$", re.IGNORECASE)


def _chapter_sort_key(md_file: Path, special: dict[str, float]) -> float:
    m = LOG_RE.search(md_file.name)
    if m:
        return float(m.group(1))
    m = LOG_LETTER_RE.search(md_file.name)
    if m:
        letter = m.group(1).upper()
        return special.get(letter, 999.0)
    return 999.0


def collect_chapters(
    drafts_dir: Path,
    special: dict[str, float],
) -> list[tuple[str, list[Path]]]:
    """
    Retourne une liste ordonnée de (nom_séquence, [fichiers_md]).
    Les dossiers sont triés par numéro de séquence, les fichiers par chapter_id.
    """
    if not drafts_dir.exists():
        raise FileNotFoundError(f"Dossier introuvable : {drafts_dir}")

    seq_dirs = sorted(
        [d for d in drafts_dir.iterdir() if d.is_dir()],
        key=lambda d: _seq_sort_key(d.name),
    )

    result = []
    for seq_dir in seq_dirs:
        files = sorted(
            seq_dir.glob("*.md"),
            key=lambda f: _chapter_sort_key(f, special),
        )
        if files:
            result.append((seq_dir.name, files))
    return result


def _seq_sort_key(name: str) -> int:
    m = re.search(r"(\d+)", name)
    return int(m.group(1)) if m else 0


# ---------------------------------------------------------------------------
# Frontmatter
# ---------------------------------------------------------------------------
FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Retourne (dict_frontmatter, corps_sans_frontmatter)."""
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    fm = yaml.safe_load(m.group(1)) or {}
    body = text[m.end():]
    return fm, body


# ---------------------------------------------------------------------------
# Assemblage markdown
# ---------------------------------------------------------------------------
SEQUENCE_DIVIDER = "\n\n---\n\n"


def assemble(
    sequences: list[tuple[str, list[Path]]],
    seq_display_names: dict[str, str],
    lang: str,
) -> str:
    parts: list[str] = []

    for seq_name, files in sequences:
        display = seq_display_names.get(seq_name, seq_name)
        parts.append(f"\n\n# {display}\n\n")

        for path in files:
            raw = path.read_text(encoding="utf-8")
            fm, body = parse_frontmatter(raw)

            chapter_name = fm.get("chapter_name", "")
            chapter_id   = fm.get("chapter_id", "")

            # Numéro d'affichage propre
            try:
                num = int(str(chapter_id).lstrip("0") or "0")
                log_label = f"Log #{num}"
            except ValueError:
                log_label = f"Log {chapter_id}"

            if chapter_name:
                heading = f"## {log_label} — {chapter_name}"
            else:
                heading = f"## {log_label}"

            # Retire l'éventuel # Log #N déjà présent en début de body
            body = re.sub(r"^#\s+Log\s+[^\n]+\n", "", body.lstrip("\n"), count=1)

            parts.append(f"{heading}\n\n{body.strip()}\n\n")

    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Page de garde (injectée comme markdown + HTML brut)
# ---------------------------------------------------------------------------
LICENSE_SYMBOLS = {
    "CC BY 4.0":         "Creative Commons Attribution 4.0",
    "CC BY-NC 4.0":      "Creative Commons Attribution–NonCommercial 4.0",
    "CC BY-NC-ND 4.0":   "Creative Commons Attribution–NonCommercial–NoDerivatives 4.0",
    "CC BY-NC-SA 4.0":   "Creative Commons Attribution–NonCommercial–ShareAlike 4.0",
    "All Rights Reserved": "Tous droits réservés / All rights reserved",
}


def build_title_page(cfg: dict, lang: str) -> str:
    lc   = cfg[lang]
    book = cfg["book"]
    lic  = cfg["license"]

    title    = lc["title"]
    subtitle = lc.get("subtitle", f"{'Livre' if lang == 'fr' else 'Book'} {book['volume']}")
    author   = lc["author"]
    year     = lic["year"]
    lic_type = lic["type"]
    lic_text = lic.get(f"text_{lang}", LICENSE_SYMBOLS.get(lic_type, lic_type))
    lic_url  = lic.get("url", "")

    cc_line = ""
    if lic_url and lic_type.startswith("CC"):
        cc_line = f"\n[{lic_type}]({lic_url})\n"

    return f"""\
<div class="title-page">

# {title}

<p class="subtitle">{subtitle}</p>

<p class="author">{author}</p>

</div>

---

<p style="font-size:0.8em; color:#666; margin-top:3em;">
© {year} {author}<br>
{lic_text}
{cc_line}
</p>

---

"""


# ---------------------------------------------------------------------------
# Couverture (Pillow)
# ---------------------------------------------------------------------------
def generate_cover(cfg: dict, lang: str, out_path: Path) -> None:
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("  [cover] Pillow absent — couverture ignorée.", file=sys.stderr)
        return

    W, H = 1600, 2560
    img  = Image.new("RGB", (W, H), color=(10, 12, 20))
    draw = ImageDraw.Draw(img)

    # Grille hexagonale (thème Bayeux II)
    _draw_hex_grid(draw, W, H)

    lc = cfg[lang]
    title    = lc["title"].upper()
    subtitle = lc.get("subtitle", "")
    author   = lc["author"]

    try:
        font_title  = ImageFont.truetype(FONT_SERIF, 130)
        font_sub    = ImageFont.truetype(FONT_SANS,  70)
        font_author = ImageFont.truetype(FONT_SANS,  55)
    except OSError:
        font_title = font_sub = font_author = ImageFont.load_default()

    # Titre
    _draw_centered(draw, title, W, H * 0.45, font_title, (230, 230, 230))
    # Sous-titre
    _draw_centered(draw, subtitle, W, H * 0.55, font_sub, (160, 160, 180))
    # Auteur
    _draw_centered(draw, author, W, H * 0.88, font_author, (130, 130, 150))

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(out_path), "PNG", optimize=True)
    print(f"  [cover] {out_path}")


def _draw_hex_grid(draw: "ImageDraw.ImageDraw", W: int, H: int) -> None:
    size  = 80          # rayon d'un hexagone
    color = (20, 30, 55)
    dx    = size * math.sqrt(3)
    dy    = size * 1.5
    cols  = int(W / dx) + 2
    rows  = int(H / dy) + 2

    for row in range(-1, rows + 1):
        for col in range(-1, cols + 1):
            cx = col * dx + (dx / 2 if row % 2 else 0)
            cy = row * dy
            pts = _hex_points(cx, cy, size - 4)
            draw.polygon(pts, outline=color)


def _hex_points(cx: float, cy: float, r: float) -> list[tuple[float, float]]:
    return [
        (cx + r * math.cos(math.radians(60 * i - 30)),
         cy + r * math.sin(math.radians(60 * i - 30)))
        for i in range(6)
    ]


def _draw_centered(
    draw: "ImageDraw.ImageDraw",
    text: str,
    W: int,
    y: float,
    font: "ImageFont.FreeTypeFont",
    color: tuple,
) -> None:
    bbox = draw.textbbox((0, 0), text, font=font)
    tw   = bbox[2] - bbox[0]
    draw.text(((W - tw) / 2, y), text, font=font, fill=color)


# ---------------------------------------------------------------------------
# Build EPUB
# ---------------------------------------------------------------------------
def build_epub(
    md_path: Path,
    cover_path: Path | None,
    output_path: Path,
    cfg: dict,
    lang: str,
    css_path: Path,
    verbose: bool = False,
) -> None:
    lc   = cfg[lang]
    book = cfg["book"]
    title    = f"{lc['title']} — {lc.get('subtitle', '')}"
    author   = lc["author"]
    language = lc["language"]

    cmd = [
        "pandoc",
        str(md_path),
        "--from", "markdown+smart",
        "--to", "epub3",
        "--output", str(output_path),
        "--toc",
        "--toc-depth=2",
        f"--metadata=title:{title}",
        f"--metadata=author:{author}",
        f"--metadata=lang:{language}",
        f"--css={css_path}",
        "--split-level=2",
    ]
    if cover_path and cover_path.exists():
        cmd += [f"--epub-cover-image={cover_path}"]

    _run(cmd, verbose)
    print(f"  [epub] {output_path}")


# ---------------------------------------------------------------------------
# Build PDF (pandoc HTML → WeasyPrint)
# ---------------------------------------------------------------------------
def build_pdf(
    md_path: Path,
    output_path: Path,
    cfg: dict,
    lang: str,
    css_path: Path,
    verbose: bool = False,
) -> None:
    lc = cfg[lang]
    title  = f"{lc['title']} — {lc.get('subtitle', '')}"
    author = lc["author"]

    with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as tmp:
        html_path = Path(tmp.name)

    try:
        # Étape 1 : pandoc md → HTML standalone
        cmd_html = [
            "pandoc",
            str(md_path),
            "--from", "markdown+smart",
            "--to", "html5",
            "--standalone",
            "--toc",
            "--toc-depth=2",
            f"--metadata=title:{title}",
            f"--metadata=author:{author}",
            f"--css={css_path}",
            "--output", str(html_path),
        ]
        _run(cmd_html, verbose)

        # Étape 2 : WeasyPrint HTML → PDF
        from weasyprint import HTML as WP_HTML
        WP_HTML(filename=str(html_path)).write_pdf(str(output_path))
        print(f"  [pdf]  {output_path}")

    finally:
        html_path.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Utilitaires
# ---------------------------------------------------------------------------
def _run(cmd: list[str], verbose: bool) -> None:
    if verbose:
        print("  $", " ".join(cmd))
    result = subprocess.run(cmd, capture_output=not verbose)
    if result.returncode != 0:
        msg = result.stderr.decode() if result.stderr else "(pas de détail)"
        raise RuntimeError(f"Commande échouée : {cmd[0]}\n{msg}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(
        description="Génère PDF et EPUB pour Grogle Failure."
    )
    parser.add_argument(
        "--lang", choices=["fr", "en", "both"], default="both",
        help="Version à générer (défaut: both)",
    )
    parser.add_argument(
        "--fmt", choices=["pdf", "epub", "all"], default="all",
        help="Format de sortie (défaut: all)",
    )
    parser.add_argument(
        "--cover-only", action="store_true",
        help="Regénère seulement les couvertures",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true",
        help="Affiche les commandes pandoc",
    )
    args = parser.parse_args()

    cfg = load_config()
    langs = ["fr", "en"] if args.lang == "both" else [args.lang]

    book_cfg = cfg["book"]
    special  = {k: float(v) for k, v in cfg.get("special_chapters", {}).items()}

    styles_dir = ROOT / book_cfg["styles_dir"]
    covers_dir = ROOT / book_cfg["covers_dir"]
    output_dir = ROOT / book_cfg["output_dir"]

    for lang in langs:
        print(f"\n=== {lang.upper()} ===")
        lc         = cfg[lang]
        drafts_dir = ROOT / lc["drafts"]
        out_lang   = output_dir / lang
        out_lang.mkdir(parents=True, exist_ok=True)

        # Cover
        cover_path = covers_dir / f"cover_{lang}.png"
        if not cover_path.exists() or args.cover_only:
            generate_cover(cfg, lang, cover_path)
        else:
            print(f"  [cover] existant → {cover_path}")

        if args.cover_only:
            continue

        # Assemblage
        seq_names  = lc.get("sequences", {})
        sequences  = collect_chapters(drafts_dir, special)
        title_page = build_title_page(cfg, lang)
        body       = assemble(sequences, seq_names, lang)
        full_md    = title_page + body

        slug  = f"grogle-failure-{'livre' if lang == 'fr' else 'book'}{book_cfg['volume']}-{lang}"
        epub_path = out_lang / f"{slug}.epub"
        pdf_path  = out_lang / f"{slug}.pdf"

        css_epub = styles_dir / "epub.css"
        css_pdf  = styles_dir / "pdf.css"

        with tempfile.NamedTemporaryFile(
            suffix=".md", delete=False, mode="w", encoding="utf-8"
        ) as tmp:
            tmp.write(full_md)
            md_path = Path(tmp.name)

        try:
            do_epub = args.fmt in ("epub", "all")
            do_pdf  = args.fmt in ("pdf",  "all")

            if do_epub:
                build_epub(md_path, cover_path, epub_path, cfg, lang, css_epub, args.verbose)
            if do_pdf:
                build_pdf(md_path, pdf_path, cfg, lang, css_pdf, args.verbose)

        finally:
            md_path.unlink(missing_ok=True)

    print("\nTerminé.")


if __name__ == "__main__":
    main()
