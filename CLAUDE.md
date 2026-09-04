# Grogle Failure

## Project overview

Il s'agit d'un livre lit-rpg "light" ou l'apocalypse et l'avenement du système sont en cours. 

## Characters

Le livre est centrée autour d'un seul et unique personnage:

Aymeric: Un jeune homme, un looser, se retrouve dans une situation que ni lui ni le reste du monde n'attendait.


## Current arc / chapter

L'action principale du livre se passe a Bayeux II, une ville hexagonale, un template appliqué pour palier au milles et un problèmes qu'a du affronté le monde ces dernières années. 

L'arrivée d'une mise a jour inattendu des Bracelets NeXT, un outil vital pour la survie de l'humanité a mis a bas la société tel qu'elle existait jusqu'alors. 

## Standing notes for Claude

Le style de prose, les règles de mise en page IM et les contraintes par personnage
sont définis dans `world/concepts/style_global.md`. Ce fichier fait autorité.

Points critiques à garder en tête :
- **Headers IM** : toujours `***Nom***` (triple astérisque), jamais `**Nom**`.
- **Stats litRPG** (Santé / Fatigue / NanoMachines) : uniquement dans les blocs
  `***Gus***`, jamais dans la narration, et **seulement à partir du Log #20**
  (upgrade HyperPro au PCA). Format : `> Santé : 87 / 100` (espaces autour de
  `:` et `/`). Ordre canonique : Santé → Fatigue → NanoMachines.
- **Fara** ne parle pas vocalement depuis la Séquence 5 (Log #22+) :
  tout dialogue de Fara passe par IM sur `SuvivantsConscrits_1`.
- **Escapes Google Docs** : les fichiers importés depuis Google Docs contiennent
  parfois des `\!` `\-` `\#` `\[` inutiles. Les corriger avec le linter.
- **Traduction anglaise** : le Livre 1 est traduit dans `drafts/en/` (dossiers
  `Sequence N`, et non `Séquence N`). Le glossaire et les conventions de
  traduction figés sont dans `scraps/translate/Rapport_Sequence_{1..5}.md` —
  **les lire avant toute reprise de l'EN**. Linter dédié : `linter_en.py`.
  ⚠️ L'EN est un **miroir 1:1 du FR, bugs compris** : corriger d'abord le FR,
  puis re-synchroniser l'EN. Ne jamais « réparer » seulement l'EN.

---

## Linter de style (`linter.py`)

Un linter Python est disponible à la racine du projet pour vérifier la conformité
au guide de style et préparer les passes de refactorisation.

### Lancement

```bash
# Tous les drafts
python3 linter.py

# Une séquence spécifique
python3 linter.py "drafts/Séquence 2"

# Un fichier précis
python3 linter.py "drafts/Séquence 3/Log #11.md"

# Avec correction automatique des escapes (--fix)
python3 linter.py --fix "drafts/Séquence 2"

# Erreurs seulement (sans les warnings)
python3 linter.py --errors

# Résumé uniquement
python3 linter.py --quiet
```

### Règles vérifiées

| Règle | Sév. | Ce qu'elle détecte |
|---|---|---|
| `no-frontmatter` | erreur | Frontmatter YAML absent |
| `frontmatter-missing-field` | erreur | Champ obligatoire manquant |
| `escape-chars` | erreur | `\!` `\#` `\-` `\[` — artefacts Google Docs |
| `im-header-double` | erreur | `**Nom**` au lieu de `***Nom***` |
| `stats-before-upgrade` | erreur | Stats Santé/Fatigue/NanoMachines avant Log #20 |
| `stat-format-slash` | erreur | `Santé:87/100` — espaces autour de `/` manquants |
| `stat-format-colon` | erreur | `Santé:87` — espace après `:` manquant |
| `stat-order` | warning | Ordre canonique Santé→Fatigue→NanoMachines non respecté |
| `fara-vocal` | erreur | Fara parle vocalement après chapter_id ≥ 22 |

### Ce que `--fix` corrige automatiquement

Uniquement les escapes inutiles (`\!` → `!`, `\-` → `-`, `\#` → `#`, `\[` → `[`).
Les codes erreur système du type `\_\#NOM\_` sont préservés intacts.

Les autres règles (headers `**` vs `***`, stats, Fara) restent à corriger manuellement.

---

## Linter de style anglais (`linter_en.py`)

Pendant de `linter.py` pour la traduction anglaise (`drafts/en/`). Même
architecture, mêmes options (`--fix`, `--errors`, `--quiet`), `--fix` ne touche
que les escapes. Il vérifie le guide de style traduit **et** les points de forme
propres au passage français → anglais.

### Lancement

```bash
# Tout le draft EN (défaut : drafts/en)
python3 linter_en.py

# Une séquence / un fichier
python3 linter_en.py "drafts/en/Sequence 5"
python3 linter_en.py "drafts/en/Sequence 3/Log #11.md"

# Erreurs seulement (masque la migration du dialogue, en warning)
python3 linter_en.py --errors

# Correction auto des escapes
python3 linter_en.py --fix "drafts/en"
```

Le résumé final ventile le total par règle (utile pour piloter une passe).

### Règles vérifiées

Stats en noms anglais : **Health / Fatigue / NanoMachines** (mêmes contraintes
de format/ordre/Log #20 que le FR). Canal Fara : `ConscriptSurvivors_1`.

| Règle | Sév. | Ce qu'elle détecte |
|---|---|---|
| `no-frontmatter` / `frontmatter-missing-field` | erreur | Frontmatter absent/incomplet |
| `escape-chars` | erreur | `\!` `\#` `\-` `\[` — artefacts Google Docs |
| `im-header-double` | erreur | `**Nom**` au lieu de `***Nom***` |
| `stats-before-upgrade` | erreur | Stats Health/Fatigue/NanoMachines avant Log #20 |
| `stat-format-slash` / `stat-format-colon` | erreur | Espaces manquants dans `Health : 87 / 100` |
| `stat-order` | warning | Ordre ≠ Health→Fatigue→NanoMachines (OK si message système auto) |
| `fara-vocal` | erreur | Fara vocale après Séq. 5 — **cas nommés seulement** (voir limite) |
| `french-guillemets` | erreur | Guillemets `« »` résiduels |
| `french-typography` | warning | Espace avant `; ! ?` (typo française) |
| `french-word` | warning | Mots-outils FR non traduits (toponymes conservés exclus) |
| `unbalanced-quotes` | warning | Nombre impair de `"` dans le fichier (réplique non fermée) |
| `dialogue-em-dash` | warning | **Réplique au tiret cadratin → à migrer vers `"…"`** (1 paragraphe/locuteur) |

**Limite `fara-vocal`** : ne détecte que les lignes où « Fara » est nommée. Les
attributions par pronom (« she adds », « she specifies » — cf. Log #24) ne sont
pas captables au regex ; elles ressortent via `dialogue-em-dash` tant que la
migration du dialogue n'est pas faite.

### Convention de dialogue (à trancher / migrer)

Le dialogue vocal est encore au **tiret cadratin** (calque du FR). La cible
anglaise recommandée : **guillemets droits `"…"`, un paragraphe par locuteur**
(les blocs IM `***Nom***` / `>` restent inchangés). La règle `dialogue-em-dash`
liste tout le travail restant. Cette migration n'est **pas** auto-corrigée par
`--fix` (elle demande une restructuration en paragraphes et la gestion des tags
de parole) — elle se fait à la main, séquence par séquence, objectif
`dialogue-em-dash` → 0.
