#!/usr/bin/env python3
"""
Linter de style pour les drafts de Grogle Failure.

Vérifie la conformité au guide de style (world/concepts/style_global.md) :
  - escapes Google Docs résiduels  (\\! \\- \\# \\[)
  - headers IM avec ** au lieu de ***
  - stats avant l'upgrade HyperPro (Log #20)
  - format et ordre canonique des stats Santé/Fatigue/NanoMachines
  - dialogue vocal de Fara après la Séquence 5
  - présence et complétude du frontmatter YAML

Usage:
    python3 linter.py [options] [path ...]

    path      Fichier(s) ou dossier(s) à analyser (défaut: drafts/)
    --fix     Corrige automatiquement les escapes dans les fichiers
    --errors  N'affiche que les erreurs (ignore les warnings)
    --quiet   Résumé final uniquement, sans le détail par fichier

Exemples:
    python3 linter.py
    python3 linter.py "drafts/Séquence 2"
    python3 linter.py --fix "drafts/Séquence 3"
    python3 linter.py --errors --quiet
"""

import re
import sys
from dataclasses import dataclass
from pathlib import Path


# ---------------------------------------------------------------------------
# Modèle
# ---------------------------------------------------------------------------

@dataclass
class Issue:
    """Un problème de style détecté sur une ligne précise d'un fichier."""
    file: Path
    line: int      # numéro de ligne (1-based)
    rule: str      # identifiant de la règle (pour filtrer / scripter)
    message: str   # description lisible
    severity: str = "error"  # "error" | "warning"

    def __str__(self) -> str:
        sev = "ERR " if self.severity == "error" else "WARN"
        return f"  [{sev}] L{self.line:>4}  {self.rule:<28}  {self.message}"


# ---------------------------------------------------------------------------
# Parsing du frontmatter YAML
# ---------------------------------------------------------------------------

# Le frontmatter est délimité par --- au début et à la fin.
# re.DOTALL pour que . matche aussi les sauts de ligne.
_FRONTMATTER_BLOCK_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)

def parse_frontmatter(text: str) -> dict:
    """
    Extrait le frontmatter YAML d'un fichier markdown.
    Retourne un dict vide si absent ou malformé.
    Dépend de pyyaml (pip install pyyaml) ; fallback silencieux si absent.
    """
    m = _FRONTMATTER_BLOCK_RE.match(text)
    if not m:
        return {}
    try:
        import yaml
        return yaml.safe_load(m.group(1)) or {}
    except Exception:
        # yaml absent ou frontmatter invalide — on signalera l'absence de champs
        return {}


# Champs obligatoires définis dans le skill write-chapter.
_FRONTMATTER_REQUIRED = [
    "chapter_id",    # tri chronologique
    "chapter_name",  # titre lisible
    "pov",           # point de vue (toujours Aymeric Bator ici)
    "location",      # lieu(x) de la scène
    "presence",      # personnages présents
    "mood",          # tons dominants
    "description",   # résumé en une phrase
    "arcs",          # beats d'arc accomplis
]


# ---------------------------------------------------------------------------
# Patterns de détection
# ---------------------------------------------------------------------------

# — Escapes Google Docs —
# Google Docs exporte parfois les caractères spéciaux Markdown avec un \
# devant eux (\! \# \- \[). Ces escapes sont inutiles dans la prose.
# Exception : les codes erreur système de la forme \_\#NOM\_
# dont les underscores doivent rester échappés pour afficher _ littéralement.
_ESCAPE_RE = re.compile(r"\\([!#\[\-])")
_ERROR_CODE_RE = re.compile(r"\\_\\#[A-Z_]+\\_")

# — Headers IM —
# Le style canonique est ***Nom*** (triple astérisque = bold+italic).
# On cherche une ligne entière qui est **Nom** (double = bold seul).
# Conditions d'exclusion :
#   - lignes commençant par > (contenu de message blockquote)
#   - **. . .** (indicateur de saisie en cours, commence par un point)
#   - ***...*** (déjà correct, la négation (?!\*) filtre ça)
_IM_HEADER_DOUBLE_RE = re.compile(
    r"^"
    r"\*\*(?!\*)"                                        # ** mais pas ***
    r"([A-Za-zÀ-ÿ0-9][A-Za-zÀ-ÿ0-9 ._'()à-ÿ-]*)"      # nom (commence par alnum)
    r"\*\*(?!\*)"                                        # ** mais pas ***
    r"\s*$"
)

# — Stats litRPG —
# Les jauges Santé/Fatigue/NanoMachines n'existent qu'à partir du Log #20
# (installation du module Grogle HealthCare via le bracelet HyperPro au PCA).
# Format attendu : > Santé : 87 / 100  (espaces autour de / et de :)
# Séparateur multi-stats : |  (> Santé : 87 / 100 | Fatigue : 45 / 100)
_STAT_LINE_RE = re.compile(r">\s*(Santé|Fatigue|NanoMachines)\s*")
STAT_NAMES = ("Santé", "Fatigue", "NanoMachines")
STAT_ORDER = ["Santé", "Fatigue", "NanoMachines"]  # ordre canonique

# — Fara vocale —
# Depuis la Séquence 5 (Log #22), Fara communique uniquement par IM.
# Tout dialogue introduit par un tiret cadratin attribué à Fara est une erreur.
_FARA_VOCAL_RE = re.compile(
    r"[―—]\s*.+?[,!?…]\s*"                              # réplique + ponctuation de fin
    r"(?:dit|ajoute|lance|grogne|répond|crie|murmure|souffle|lâche|"
    r"s['’]exclame|s['’]énerve|répète|assène|rétorque|ordonne|réplique)\s+"
    r"Fara"                                              # attribuée à Fara
)


# ---------------------------------------------------------------------------
# Analyse d'un fichier
# ---------------------------------------------------------------------------

def lint_file(path: Path) -> list[Issue]:
    """
    Analyse un fichier markdown et retourne la liste des problèmes trouvés.
    Le frontmatter YAML est ignoré pour les règles de contenu.
    """
    issues: list[Issue] = []
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    fm = parse_frontmatter(text)
    # PyYAML 1.1 octal quirk : "008"/"009" → str, "010" → int 8 (faux).
    # On normalise systématiquement via str() pour lire la valeur littérale.
    chapter_id: int | None = None
    chapter_id_raw = fm.get("chapter_id")
    if chapter_id_raw is not None:
        try:
            chapter_id = int(str(chapter_id_raw))
        except (ValueError, TypeError):
            pass

    # — Vérification du frontmatter (une seule fois, signalé sur L1) --------

    if not fm:
        issues.append(Issue(path, 1, "no-frontmatter",
                            "Frontmatter YAML manquant — voir skill write-chapter"))
    else:
        for field_name in _FRONTMATTER_REQUIRED:
            if field_name not in fm:
                issues.append(Issue(path, 1, "frontmatter-missing-field",
                                    f"Champ frontmatter manquant : '{field_name}'"))

    # — Analyse ligne par ligne du corps ------------------------------------

    in_frontmatter = False
    for i, line in enumerate(lines, start=1):

        # Sauter le frontmatter (délimité par les deux `---`)
        if i == 1 and line.strip() == "---":
            in_frontmatter = True
            continue
        if in_frontmatter:
            if line.strip() == "---":
                in_frontmatter = False
            continue

        s = line.rstrip()  # ligne sans espace final

        # 1. Escapes inutiles (\! \# \- \[)
        #    On exclut les lignes contenant un code erreur système (\_\#NOM\_)
        #    dont les escapes sont intentionnels pour afficher _ littéralement.
        if not _ERROR_CODE_RE.search(s):
            found = _ESCAPE_RE.findall(s)
            if found:
                chars = ", ".join(f"\\{c}" for c in found)
                issues.append(Issue(path, i, "escape-chars",
                    f"Escape(s) inutile(s) : {chars} "
                    "(artefact Google Docs — supprimer le \\)",
                    severity="error"))

        # 2. Header IM avec ** au lieu de ***
        #    Une ligne blockquote (>) ne peut pas être un header — les **gras**
        #    à l'intérieur des messages sont du contenu légitime.
        if not s.startswith(">") and _IM_HEADER_DOUBLE_RE.match(s):
            issues.append(Issue(path, i, "im-header-double",
                f"Header IM avec ** au lieu de *** : {s.strip()} "
                "— le style impose triple astérisque pour tous les expéditeurs",
                severity="error"))

        # 3. Stats Santé/Fatigue/NanoMachines avant le Log #20
        #    Ces jauges sont fournies par le module Grogle HealthCare,
        #    disponible seulement après l'installation du bracelet HyperPro au PCA
        #    (Log #20, Séquence 4).
        if chapter_id is not None and chapter_id < 20:
            if _STAT_LINE_RE.search(s):
                issues.append(Issue(path, i, "stats-before-upgrade",
                    "Stat Santé/Fatigue/NanoMachines avant Log #20 — "
                    "module HealthCare pas encore installé (upgrade au PCA, Log #20)",
                    severity="error"))

        # 4. Format des stats
        #    Attendu : > Santé : 87 / 100   (espace avant et après :, / entouré d'espaces)
        if _STAT_LINE_RE.search(s):
            for stat in STAT_NAMES:
                if stat not in s:
                    continue
                # Slash sans espaces : Santé : 87/100 ou Santé:87/100
                if re.search(stat + r"\s*:\s*\d+/\d+", s):
                    issues.append(Issue(path, i, "stat-format-slash",
                        f"'{stat}' : espace manquant autour de '/' "
                        "(attendu : X / 100)",
                        severity="error"))
                # Deux-points collé : Santé:87
                if re.search(stat + r":\S", s):
                    issues.append(Issue(path, i, "stat-format-colon",
                        f"'{stat}' : espace manquant après ':' "
                        "(attendu : Stat : X / 100)",
                        severity="error"))

        # 5. Ordre canonique des stats sur une même ligne
        #    Quand plusieurs stats sont affichées, l'ordre doit être :
        #    Santé | Fatigue | NanoMachines (du plus visible au plus technique)
        if _STAT_LINE_RE.search(s):
            present = [stat for stat in STAT_ORDER if stat in s]
            if len(present) > 1 and present != [stat for stat in STAT_ORDER if stat in present]:
                issues.append(Issue(path, i, "stat-order",
                    f"Ordre des stats incorrect : {present} "
                    f"(canonique : {[stat for stat in STAT_ORDER if stat in present]})",
                    severity="warning"))

        # 6. Fara parle vocalement après la Séquence 5 (chapter_id >= 22)
        #    Depuis sa blessure, Fara communique uniquement via IM sur
        #    SuvivantsConscrits_1, ou par `l'armure grésille` pour les très
        #    courtes interventions. Tout tiret cadratin attribué à Fara est une
        #    erreur de continuité.
        if chapter_id is not None and chapter_id >= 22:
            if _FARA_VOCAL_RE.search(s):
                issues.append(Issue(path, i, "fara-vocal",
                    "Fara ne parle pas vocalement depuis la Séq. 5 — "
                    "convertir en bloc IM SuvivantsConscrits_1 "
                    "ou `l'armure grésille` pour très court",
                    severity="error"))

    return issues


# ---------------------------------------------------------------------------
# Auto-fix des escapes (--fix)
# ---------------------------------------------------------------------------

def _protect_error_codes(text: str) -> tuple[str, dict[str, str]]:
    """
    Remplace temporairement les codes erreur système par des sentinelles
    pour que fix_escapes() ne touche pas à leurs underscores intentionnels.
    Exemple : \\_\\#ERROR_CODE\\_ → \\x00ERRCODE0\\x00
    """
    placeholders: dict[str, str] = {}

    def replace(m: re.Match) -> str:
        key = f"\x00ERRCODE{len(placeholders)}\x00"
        placeholders[key] = m.group(0)
        return key

    return _ERROR_CODE_RE.sub(replace, text), placeholders


def _restore_error_codes(text: str, placeholders: dict[str, str]) -> str:
    for key, val in placeholders.items():
        text = text.replace(key, val)
    return text


def fix_escapes(text: str) -> str:
    """
    Supprime les escapes Google Docs inutiles dans un texte markdown.
    \\! → !   \\# → #   \\- → -   \\[ → [
    Les codes erreur système (\\_\\#NOM\\_) sont préservés intacts.
    """
    text, ph = _protect_error_codes(text)
    text = re.sub(r"\\([!#\[\-])", r"\1", text)
    return _restore_error_codes(text, ph)


# ---------------------------------------------------------------------------
# Collecte des fichiers cibles
# ---------------------------------------------------------------------------

def collect_files(paths: list[Path]) -> list[Path]:
    """
    Résout une liste de chemins (fichiers ou dossiers) en fichiers .md.
    Les dossiers sont parcourus récursivement. Les doublons sont éliminés.
    """
    result = []
    for p in paths:
        if p.is_file() and p.suffix == ".md":
            result.append(p)
        elif p.is_dir():
            result.extend(sorted(p.rglob("*.md")))
    return sorted(set(result))


# ---------------------------------------------------------------------------
# Point d'entrée
# ---------------------------------------------------------------------------

def main() -> int:
    args = sys.argv[1:]
    do_fix   = "--fix"    in args
    only_err = "--errors" in args
    quiet    = "--quiet"  in args
    paths_raw = [a for a in args if not a.startswith("--")]

    project_root = Path(__file__).parent
    targets = [Path(p) for p in paths_raw] if paths_raw else [project_root / "drafts"]

    files = collect_files(targets)
    if not files:
        print("Aucun fichier .md trouvé.")
        return 0

    total_errors = total_warnings = files_with_issues = 0

    for path in files:

        # Correction automatique des escapes avant l'analyse
        if do_fix:
            original = path.read_text(encoding="utf-8")
            fixed = fix_escapes(original)
            if fixed != original:
                path.write_text(fixed, encoding="utf-8")

        issues = lint_file(path)
        if only_err:
            issues = [iss for iss in issues if iss.severity == "error"]

        errors   = [iss for iss in issues if iss.severity == "error"]
        warnings = [iss for iss in issues if iss.severity == "warning"]
        total_errors   += len(errors)
        total_warnings += len(warnings)

        if issues:
            files_with_issues += 1
            if not quiet:
                rel = path.resolve().relative_to(project_root)
                print(f"\n{'─' * 64}")
                print(f"  {rel}  ({len(errors)}E  {len(warnings)}W)")
                for iss in issues:
                    print(iss)

    # Résumé final
    print(f"\n{'═' * 64}")
    print(f"  {len(files)} fichier(s) analysé(s)   "
          f"{files_with_issues} avec problème(s)")
    print(f"  {total_errors} erreur(s)  ·  {total_warnings} warning(s)")
    if do_fix:
        print("  Escapes corrigés automatiquement dans les fichiers (--fix)")
    print()

    return 1 if total_errors > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
