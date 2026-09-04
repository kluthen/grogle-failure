#!/usr/bin/env python3
"""
Linter de style pour les drafts ANGLAIS de Grogle Failure (drafts/en/).

Pendant de linter.py (drafts FR), adapté à la traduction anglaise. Il vérifie la
conformité au guide de style traduit ET les points de forme propres au passage
français → anglais identifiés lors de la traduction (voir scraps/translate/).

Règles vérifiées :
  - frontmatter YAML présent et complet
  - escapes Google Docs résiduels  (\\! \\- \\# \\[)            [--fix]
  - headers IM avec ** au lieu de ***
  - stats avant l'upgrade HyperPro (Log #20)
  - format/ordre canonique des stats  Health / Fatigue / NanoMachines
  - dialogue vocal de Fara après la Séquence 5 (cas nommés)
  - guillemets français « » résiduels
  - typographie française résiduelle (espace avant ; ! ?)
  - mots-outils français non traduits (c'est, j'ai, putain…)
  - guillemets droits déséquilibrés (nombre impair de ")
  - dialogue introduit au tiret cadratin  (migration → guillemets "…")

Les deux dernières règles pilotent la passe de migration du dialogue : voir
`dialogue-em-dash`. Tant que la conversion tiret → guillemets n'est pas faite,
cette règle (warning) liste tout le travail restant.

Cas NON détectables automatiquement (à traiter à la main lors de la passe) :
  - Fara attribuée par un pronom seul (« she adds », « she specifies »…) sans
    son nom sur la ligne : le linter ne peut pas la lier à Fara de façon fiable.
    Ces lignes ressortent malgré tout via `dialogue-em-dash` tant qu'on n'a pas
    migré le dialogue.

Usage :
    python3 linter_en.py [options] [path ...]

    path      Fichier(s) ou dossier(s) à analyser (défaut: drafts/en)
    --fix     Corrige automatiquement les escapes dans les fichiers
    --errors  N'affiche que les erreurs (ignore les warnings)
    --quiet   Résumé final uniquement, sans le détail par fichier

Exemples :
    python3 linter_en.py
    python3 linter_en.py "drafts/en/Sequence 5"
    python3 linter_en.py --errors             # masque la migration du dialogue
    python3 linter_en.py --fix "drafts/en"
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


# Champs obligatoires définis dans le skill write-chapter (identiques au FR).
_FRONTMATTER_REQUIRED = [
    "chapter_id",    # tri chronologique
    "chapter_name",  # titre lisible
    "pov",           # point de vue (Aymeric Bator, sauf interlude Log A)
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
# Même artefact que côté FR : \! \# \- \[. Inutiles dans la prose.
# Exception : les codes erreur système \_\#NOM\_ (underscores à préserver).
_ESCAPE_RE = re.compile(r"\\([!#\[\-])")
_ERROR_CODE_RE = re.compile(r"\\_\\#[A-Z0-9_]+\\_")

# — Headers IM —
# Style canonique : ***Nom*** (triple astérisque). On cherche une ligne entière
# en **Nom** (double). Les noms EN n'ont pas d'accents mais on reste tolérant.
_IM_HEADER_DOUBLE_RE = re.compile(
    r"^"
    r"\*\*(?!\*)"                                    # ** mais pas ***
    r"([A-Za-z0-9][A-Za-z0-9 ._'()\-]*)"            # nom (commence par alnum)
    r"\*\*(?!\*)"                                    # ** mais pas ***
    r"\s*$"
)

# — Stats litRPG (noms ANGLAIS) —
# Jauges fournies par Grogle HealthCare, disponibles à partir du Log #20.
# Format attendu : > Health : 87 / 100   (espaces autour de : et /)
# Séparateur multi-stats : |
_STAT_LINE_RE = re.compile(r">\s*(Health|Fatigue|NanoMachines)\b")
STAT_NAMES = ("Health", "Fatigue", "NanoMachines")
STAT_ORDER = ["Health", "Fatigue", "NanoMachines"]   # ordre canonique

# — Fara vocale (cas NOMMÉS) —
# Depuis la Séquence 5 (Log #22), Fara ne parle plus vocalement : IM uniquement,
# ou `the armor crackles` pour les très courtes interventions. On flag une ligne
# qui combine un marqueur de dialogue + le nom « Fara » + un verbe de parole,
# SAUF la forme sanctionnée « armor crackles ».
_SPEECH_VERBS = (
    "says", "said", "adds", "added", "throws", "growls", "answers", "screams",
    "murmurs", "breathes", "lets slip", "repeats", "lays down", "retorts",
    "orders", "snaps", "specifies", "asks", "calls", "hisses", "mutters",
    "whispers", "announces", "points out", "replies", "spits", "exclaims",
)
_SPEECH_VERB_RE = re.compile(
    r"\b(?:" + "|".join(v.replace(" ", r"\s+") for v in _SPEECH_VERBS) + r")\b"
)
# Forme sanctionnée pour Fara : « (Fara's) armor crackles ». À ne pas flagger.
_ARMOR_CRACKLE_RE = re.compile(r"armor\s+crackle", re.IGNORECASE)
_DIALOGUE_MARK_RE = re.compile(r'(^[—―])|(")')   # tiret en tête OU guillemet droit

# — Tiret cadratin de dialogue (migration → guillemets) —
# Une ligne de prose qui DÉBUTE par un tiret cadratin est une réplique au format
# français. À convertir en "…" (un paragraphe par locuteur). Le tiret en milieu
# de ligne (incise) n'est PAS concerné.
_DIALOGUE_EMDASH_RE = re.compile(r"^[—―]\s")

# — Guillemets français résiduels —
_GUILLEMETS_RE = re.compile(r"[«»]")

# — Typographie française : espace avant ; ! ?  (jamais avant : à cause des
#   stats « Health : 87 ») — on exige un alnum avant l'espace et on exclut les
#   émoticônes ( ;-)  ;)  :-) ).
_FRENCH_SPACE_RE = re.compile(r"[A-Za-z0-9] ([;!?])(?![-)])")

# — Mots-outils français non traduits. Liste volontairement étroite : on évite
#   les toponymes légitimement conservés (rue/avenue/place de…, Bayeux, etc.).
_FRENCH_WORD_RE = re.compile(
    r"\b(c'est|j'(?:ai|en|y)|n'(?:est|ai|y)|qu'(?:il|elle|on)|"
    r"putain|merde|voilà|d'accord|est-ce)\b",
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# Analyse d'un fichier
# ---------------------------------------------------------------------------

def lint_file(path: Path) -> list[Issue]:
    """
    Analyse un fichier markdown anglais et retourne la liste des problèmes.
    Le frontmatter YAML est ignoré pour les règles de contenu.
    """
    issues: list[Issue] = []
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    fm = parse_frontmatter(text)
    # PyYAML 1.1 octal quirk : "008"/"009" → str, "010" → int 8 (faux).
    # On normalise via str() pour lire la valeur littérale. L'interlude utilise
    # chapter_id "A" (non numérique) — on laisse chapter_id à None dans ce cas.
    chapter_id: int | None = None
    chapter_id_raw = fm.get("chapter_id")
    if chapter_id_raw is not None:
        try:
            chapter_id = int(str(chapter_id_raw))
        except (ValueError, TypeError):
            pass

    # — Vérification du frontmatter (signalée une fois, sur L1) --------------

    if not fm:
        issues.append(Issue(path, 1, "no-frontmatter",
                            "Frontmatter YAML manquant — voir skill write-chapter"))
    else:
        for field_name in _FRONTMATTER_REQUIRED:
            if field_name not in fm:
                issues.append(Issue(path, 1, "frontmatter-missing-field",
                                    f"Champ frontmatter manquant : '{field_name}'"))

    # — Analyse ligne par ligne du corps ------------------------------------

    body_quote_count = 0   # total de " dans le corps (citations multi-lignes OK)
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

        s = line.rstrip()           # ligne sans espace final
        is_quote = s.startswith(">")  # ligne de contenu IM (blockquote)
        has_error_code = bool(_ERROR_CODE_RE.search(s))
        body_quote_count += s.count('"')

        # 1. Escapes inutiles (\! \# \- \[)
        if not has_error_code:
            found = _ESCAPE_RE.findall(s)
            if found:
                chars = ", ".join(f"\\{c}" for c in found)
                issues.append(Issue(path, i, "escape-chars",
                    f"Escape(s) inutile(s) : {chars} "
                    "(artefact Google Docs — supprimer le \\)",
                    severity="error"))

        # 2. Header IM avec ** au lieu de ***
        if not is_quote and _IM_HEADER_DOUBLE_RE.match(s):
            issues.append(Issue(path, i, "im-header-double",
                f"Header IM avec ** au lieu de *** : {s.strip()} "
                "— triple astérisque obligatoire pour tous les expéditeurs",
                severity="error"))

        # 3. Stats Health/Fatigue/NanoMachines avant le Log #20
        if chapter_id is not None and chapter_id < 20 and _STAT_LINE_RE.search(s):
            issues.append(Issue(path, i, "stats-before-upgrade",
                "Stat Health/Fatigue/NanoMachines avant Log #20 — "
                "module HealthCare pas encore installé (upgrade au PCA, Log #20)",
                severity="error"))

        # 4. Format des stats : > Health : 87 / 100
        if _STAT_LINE_RE.search(s):
            for stat in STAT_NAMES:
                if stat not in s:
                    continue
                # Slash sans espaces : Health : 87/100  ou  Health:87/100
                if re.search(stat + r"\s*:\s*\d+/\d+", s):
                    issues.append(Issue(path, i, "stat-format-slash",
                        f"'{stat}' : espace manquant autour de '/' "
                        "(attendu : X / 100)",
                        severity="error"))
                # Deux-points collé : Health:87
                if re.search(stat + r":\S", s):
                    issues.append(Issue(path, i, "stat-format-colon",
                        f"'{stat}' : espace manquant après ':' "
                        "(attendu : Stat : X / 100)",
                        severity="error"))

        # 5. Ordre canonique des stats sur une même ligne
        #    Health | Fatigue | NanoMachines. NB : les messages système
        #    automatiques peuvent inverser l'ordre (NanoMachines | Health) —
        #    c'est sanctionné par le style ; ce warning est donc à ignorer dans
        #    ce contexte précis.
        if _STAT_LINE_RE.search(s):
            present = [stat for stat in STAT_ORDER if stat in s]
            canonical = [stat for stat in STAT_ORDER if stat in present]
            if len(present) > 1 and present != canonical:
                issues.append(Issue(path, i, "stat-order",
                    f"Ordre des stats : {present} (canonique : {canonical}) — "
                    "OK si message système automatique",
                    severity="warning"))

        # 6. Fara parle vocalement après la Séquence 5 (chapter_id >= 22)
        #    Cas nommés uniquement : dialogue + « Fara » + verbe de parole,
        #    hors forme sanctionnée « armor crackles ».
        if (chapter_id is not None and chapter_id >= 22
                and "Fara" in s
                and _DIALOGUE_MARK_RE.search(s)
                and _SPEECH_VERB_RE.search(s)
                and not _ARMOR_CRACKLE_RE.search(s)):
            issues.append(Issue(path, i, "fara-vocal",
                "Fara ne parle pas vocalement depuis la Séq. 5 — "
                "convertir en bloc IM ConscriptSurvivors_1 "
                "ou `the armor crackles` pour très court",
                severity="error"))

        # 7. Guillemets français « » résiduels
        if _GUILLEMETS_RE.search(s):
            issues.append(Issue(path, i, "french-guillemets",
                "Guillemets français « » — utiliser des guillemets droits \"…\"",
                severity="error"))

        # 8. Typographie française : espace avant ; ! ?
        if _FRENCH_SPACE_RE.search(s):
            issues.append(Issue(path, i, "french-typography",
                "Espace avant ; ! ? (typo française) — coller la ponctuation",
                severity="warning"))

        # 9. Mots-outils français non traduits
        m = _FRENCH_WORD_RE.search(s)
        if m:
            issues.append(Issue(path, i, "french-word",
                f"Mot français non traduit : '{m.group(0)}' "
                "(toponymes conservés exclus de cette règle)",
                severity="warning"))

        # 10. Dialogue au tiret cadratin → migration vers guillemets "…"
        #     (un paragraphe par locuteur). Ne touche pas les tirets d'incise.
        if not is_quote and _DIALOGUE_EMDASH_RE.match(s):
            issues.append(Issue(path, i, "dialogue-em-dash",
                "Réplique au tiret cadratin (style FR) — migrer vers \"…\" "
                "et un paragraphe par locuteur",
                severity="warning"))

    # — Contrôle au niveau fichier ------------------------------------------
    # Guillemets droits déséquilibrés : un nombre impair de " dans tout le corps
    # signale une réplique non fermée. On compte sur le fichier entier pour
    # tolérer les citations multi-lignes (slogans Gus à cheval sur plusieurs
    # lignes), qui se referment plus bas.
    if body_quote_count % 2 == 1:
        issues.append(Issue(path, 1, "unbalanced-quotes",
            f'Nombre impair de " dans le fichier ({body_quote_count}) — '
            "réplique non fermée quelque part",
            severity="warning"))

    return issues


# ---------------------------------------------------------------------------
# Auto-fix des escapes (--fix)
# ---------------------------------------------------------------------------
# Comme côté FR, --fix ne corrige QUE les escapes. La migration du dialogue
# (tiret → guillemets) n'est PAS automatisée : elle demande une restructuration
# en paragraphes et la gestion des tags de parole — réservée à la passe manuelle.

def _protect_error_codes(text: str) -> tuple[str, dict[str, str]]:
    """
    Remplace temporairement les codes erreur système par des sentinelles pour
    que fix_escapes() n'altère pas leurs underscores intentionnels.
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
    Supprime les escapes Google Docs inutiles. \\! → !  \\# → #  \\- → -  \\[ → [
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
    targets = [Path(p) for p in paths_raw] if paths_raw else [project_root / "drafts" / "en"]

    files = collect_files(targets)
    if not files:
        print("Aucun fichier .md trouvé.")
        return 0

    total_errors = total_warnings = files_with_issues = 0
    rule_counts: dict[str, int] = {}

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
        for iss in issues:
            rule_counts[iss.rule] = rule_counts.get(iss.rule, 0) + 1

        if issues:
            files_with_issues += 1
            if not quiet:
                rel = path.resolve().relative_to(project_root)
                print(f"\n{'─' * 64}")
                print(f"  {rel}  ({len(errors)}E  {len(warnings)}W)")
                for iss in issues:
                    print(iss)

    # Résumé final + ventilation par règle (utile pour piloter la migration)
    print(f"\n{'═' * 64}")
    print(f"  {len(files)} fichier(s) analysé(s)   "
          f"{files_with_issues} avec problème(s)")
    print(f"  {total_errors} erreur(s)  ·  {total_warnings} warning(s)")
    if rule_counts:
        print("  Par règle :")
        for rule, count in sorted(rule_counts.items(), key=lambda kv: -kv[1]):
            print(f"    {count:>5}  {rule}")
    if do_fix:
        print("  Escapes corrigés automatiquement dans les fichiers (--fix)")
    print()

    return 1 if total_errors > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
