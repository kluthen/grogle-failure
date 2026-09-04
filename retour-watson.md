# Retour d'expérience — Watson

> Rédigé après une session d'initialisation de la base worldbuilding du projet
> *Grogle Failure* : lecture des Logs #1 à #25, création d'une cinquantaine de
> topics (personnages, lieux, concepts, objets, factions, bestiaire) et de 5 arcs.
>
> **Périmètre.** Ce retour ne couvre **que** les outils effectivement utilisés :
> `list_topics`, `create_topic`, `update_topic`, `get_topic`, `upsert_arc`,
> `upsert_arc_beat`, et les skills `write-topic` / `write-arc`.
> Les outils d'**analyse** (`analyze_prose`, `sweep`, `crawl`, `get_adjacency`,
> `graph_neighbors`, `search_graph`, `search_topics`, `explore`) **n'ont pas encore
> été testés** — leur évaluation viendra plus tard.

---

## 1. Ce qui fonctionne bien

- **Le modèle « 1 topic = 1 fichier markdown »** est excellent : lisible, éditable
  à la main, versionnable en git, rangé automatiquement par `kind`
  (`world/characters/`, `world/concepts/`, `world/locations/`, `world/items/`,
  `world/factions/`, `world/arcs/`). On garde la main sur ses données.
- **La discipline de frontmatter** imposée par les skills (`name`, `kind`,
  `aliases`, `summary`) est une vraie valeur ajoutée. Le `summary` « une phrase,
  injectée en contexte » force à la concision utile, et la règle « pas de pronom,
  pas de conjonction » donne des résumés homogènes.
- **Les `aliases` comme clés de résolution** : penser les alias comme des clés de
  matching (et pas de la déco) est la bonne abstraction. Couvrir les variantes
  (`A. Bator`, `F. Nakash`/`F. Nakach`, orthographes flottantes du brouillon) a
  été immédiatement utile.
- **Les `[[wikilinks]]`** rendent le tissage du graphe naturel pendant la
  rédaction, sans étape séparée.
- **Le contrôle d'adjacence à la création** (annonce des OVERLAP/DUPLICATE) est un
  bon principe de garde-fou contre les doublons.
- **`upsert_arc` atomique** (ligne de graphe + fichier topic en une fois) et les
  **beat files rattachés à l'arc** (`arc:` en back-reference) : architecture
  d'arc claire et bien pensée.
- **Les skills `write-topic` / `write-arc`** sont remarquables : étapes strictes,
  ordonnées, exemples concrets, squelettes de sections, règles de style. C'est
  le meilleur de l'onboarding actuel (voir §4).

---

## 2. Frictions rencontrées (cas concrets de la session)

- **Coupures MCP en cours de batch.** Le tout premier lot de 3 `create_topic` en
  parallèle a échoué sur `MCP error -32000: Connection closed`. Après relance,
  aucun des trois n'avait été créé — mais ce n'était pas évident *a priori*
  (sémantique d'échec partiel floue : qu'est-ce qui a été committé ?).
- **`update_topic` ne touche ni aux alias ni au frontmatter.** Il ne modifie que
  `body` / `summary`. Pour corriger une collision d'alias, j'ai dû **éditer le
  fichier `.md` à la main**. Incohérence nette : `create_topic` *accepte* des
  alias, `update_topic` ne peut pas les changer.
- **Adressage incohérent entre outils.** `create_topic`/`get_topic` prennent
  `name`, mais `update_topic` prend `path`. On jongle entre deux façons de
  désigner le même objet.
- **`upsert_arc` n'a pas de paramètre `aliases`** (contrairement à
  `create_topic`). J'ai dû encoder « Séquence N » *dans le titre* pour que la
  résolution fonctionne. Incohérence dans la famille d'outils.
- **La détection de doublons rate les collisions d'alias inter-topics.** L'alias
  `NeXT` était revendiqué à la fois par `Groogle` et par `Bracelet NeXT` ; rien
  ne l'a signalé. Le contrôle semble porter sur le chevauchement de *noms*, pas
  sur les *alias vs alias* entre topics existants.
- **Slugs accentués lossy.** `é` devient `_` : `place_de_la_comm_moration.md`,
  `r_alit_augment_e.md`, `syst_me_de_caract_ristiques.md`. Lisibilité dégradée et
  risque de slugs instables. Une translittération (`é`→`e`) serait préférable.
- **Slug de beat dérivé de la mauvaise source.** `upsert_arc_beat` a généré
  `beat_boss_fight_contre_un_amalgame_g_ant_au_seuil_du_bunker_de_la_mairie.md`
  (à partir de la `description`, très longue) alors que j'avais fourni un `name`
  court (« Boss — Amalgame géant »). Résultat : nom de fichier à rallonge **et**
  désynchronisation avec le lien que j'avais écrit dans l'arc master (correction
  manuelle nécessaire).
- **Ambiguïté du frontmatter pour les beats.** Le skill montre un frontmatter à
  écrire (`bucket/kind/name/arc/summary`), mais l'outil génère peut-être déjà le
  sien : risque de double frontmatter, non clarifié.
- **Taxonomie de `kind` trop étroite.** Pas de type « créature/espèce » ni
  « événement ». Le bestiaire (homines, canides, constructes, amalgames, blobs) a
  été casé en `concept` par défaut ; l'apocalypse (« la mise à jour ») est un
  événement vécu comme `concept`. Or des outils `upsert_event` /
  `upsert_character` / `upsert_location` existent par ailleurs — d'où la
  confusion du §3.

---

## 3. Le point le plus important : le double modèle (topics vs graphe)

C'est **le principal angle mort de l'onboarding**. Il existe visiblement deux
familles d'écriture qui semblent se recouvrir :

- **Couche « topics »** : `create_topic` / `update_topic` / `get_topic`
  (fichiers markdown dans `world/`, avec un `kind`).
- **Couche « graphe »** : `upsert_character`, `upsert_location`, `upsert_event`,
  `upsert_arc`, `upsert_arc_beat`.

Rien n'explique **quand utiliser l'une ou l'autre**, ni si elles écrivent dans le
même magasin. Par défaut, j'ai tout fait via `create_topic(kind="character"…)`
plutôt que `upsert_character`, sans savoir si je « ratais » des arêtes de graphe,
des champs structurés, ou si je créais une divergence entre les deux couches.
Pour les arcs, à l'inverse, seul `upsert_arc` existe — ce qui suggère que les arcs
sont *uniquement* graphe+fichier, mais renforce l'impression d'incohérence entre
familles.

**Question ouverte pour l'auteur de l'outil :** `create_topic(kind="character")`
et `upsert_character` produisent-ils le même résultat ? Sinon, lequel est
canonique, et pour quel usage ?

---

## 4. Onboarding — diagnostic

- **Instructions MCP trop minces.** Le serveur fournit un paragraphe
  (« graph queries, topic file management, prose analysis, context assembly »).
  C'est un *quoi*, pas un *comment*. Il manque le **modèle mental** : les deux
  couches (§3), le vocabulaire de `kind`, l'ordre de travail recommandé
  (vérifier doublons → créer → lier), et la nature de l'injection en contexte
  (summary + aliases).
- **Les skills sauvent l'onboarding.** Sans `write-topic` / `write-arc`, j'aurais
  tâtonné sur le format. Mais ils ne sont **pas découvrables depuis les
  instructions MCP** : c'est moi qui ai pensé à les invoquer. Un lien explicite
  « pour écrire un topic, suis le skill write-topic » dans les instructions
  serveur fermerait la boucle.
- **Pas de convention de langue ni de premier exemple.** La base est en français
  (cohérent avec les sources), mais aucune convention n'est suggérée. Un topic
  d'exemple « seed » et un mini-guide « votre première fiche » accéléreraient
  beaucoup le démarrage à froid.
- **Découverte de l'existant peu guidée.** Pour éviter les collisions d'alias, il
  faudrait un réflexe outillé (« liste les alias déjà pris »). `list_topics`
  donne les alias, mais rien n'invite à ce contrôle avant création.

---

## 5. Pistes d'amélioration (priorisées)

**Prioritaire (cohérence & sûreté des données)**
1. **Clarifier topics vs graphe** dans les instructions MCP : un schéma, le
   vocabulaire de `kind`, et la règle « quel outil pour quoi ». C'est le point #1.
2. **Permettre l'édition des alias / du nom** (étendre `update_topic`, ou ajouter
   `rename_topic` / `set_aliases`). Ne plus avoir à éditer le `.md` à la main.
3. **Détecter les collisions d'alias inter-topics** dans le contrôle d'adjacence
   (alias vs alias, pas seulement nom vs nom).
4. **Sémantique d'échec claire / idempotence** sur coupure MCP : indiquer ce qui
   a été committé, rendre les batchs rejouables sans doublon.

**Confort & cohérence d'API**
5. **Uniformiser l'adressage** : accepter `name` *ou* `path` partout.
6. **Ajouter `aliases` à `upsert_arc`** (parité avec `create_topic`).
7. **Slugs** : translittérer les accents (`é`→`e`) au lieu de les remplacer par
   `_` ; dériver le slug de beat du `name` (court), pas de la `description`.
8. **Lever l'ambiguïté du frontmatter de beat** (le doc doit dire si l'outil le
   génère ou si on le fournit).

**Modélisation**
9. **Élargir la taxonomie `kind`** (au moins `creature`/`species` et `event`), ou
   **documenter les conventions de mapping** si l'on doit rester sur `concept`.

**Onboarding**
10. **Relier les skills depuis les instructions MCP** (« pour écrire/maj : skill
    write-topic ; pour un arc : write-arc »).
11. **Fournir un seed** : un topic d'exemple + un mini-README « première fiche /
    premier arc », et une note sur la langue/les conventions de nommage.

---

## 6. Bilan

Le **socle conceptuel est solide** (fichiers markdown + frontmatter discipliné +
alias-clés + wikilinks + arcs/beats), et les **skills sont d'excellents garde-fous**.
Les principaux irritants sont (a) le **flou topics/graphe** au démarrage, (b) les
**incohérences d'API** entre outils (alias non éditables, `name` vs `path`, arcs
sans alias), et (c) quelques **détails de slug/erreur** qui obligent à corriger à
la main. Aucun n'est bloquant — la base a été montée sans peine — mais les régler
rendrait l'outil nettement plus fluide et sûr.

*À compléter après usage des outils d'analyse (sweep, crawl, get_adjacency,
graph_neighbors, search_graph, analyze_prose, explore).*

---

## Addendum — Session 2 (2026-05-29)

### A. Renommer un topic : cas concret Yoan → Santu Ricci

Pendant la relecture des brouillons, on a découvert que le personnage enregistré
sous le nom « Yoan » (fichier `world/characters/yoan.md`) était en réalité la même
personne que « Santu / S. Ricci » (nom apparu en premier, dans le Log #24). Le nom
canonique a été tranché : **Santu Ricci**.

Workflow effectué manuellement :
1. Édition de `yoan.md` : `name` → `Santu Ricci`, `aliases` mis à jour.
2. Find-replace dans `Log #25.md` (5 occurrences de Yoan/Yoann → Santu).
3. Correction du lien dans l'arc master.
4. Le fichier **reste nommé `yoan.md`** — Watson n'offre pas d'outil pour le
   renommer. La référence frontmatter `name: Santu Ricci` et le nom de fichier
   `yoan.md` sont désormais désynchronisés.

**Demande :** un outil `rename_topic` (ou extension de `update_topic`) qui :
- accepte l'ancien nom (ou `path`) et le nouveau nom ;
- renomme le fichier physique ;
- met à jour les `[[wikilinks]]` dans tout `world/` en conséquence.

Ce point complète la friction §2 (« `update_topic` ne touche ni aux alias ni au
frontmatter ») déjà documentée plus haut.

---

### B. Slugs accentués → underscore : ampleur du problème (exemples réels)

Le §2 mentionnait le principe ; voici les fichiers réellement créés par Watson
lors de la session 1, tous avec des `_` à la place des voyelles accentuées :

```
world/arcs/s_quence_1_l_effondrement/
world/arcs/s_quence_2_la_travers_e/
world/arcs/s_quence_3_le_refuge/
world/arcs/s_quence_4_l_exp_dition/
world/arcs/s_quence_5_l_assaut/
world/arcs/arc_th_matique_la_m_tamorphose_d_aymeric/
world/arcs/arc_th_matique_la_fusion_de_fara/
world/arcs/arc_th_matique_l_veil_de_lou/
world/arcs/arc_th_matique_la_chute_de_mike/
beat_boss_fight_contre_un_amalgame_g_ant_au_seuil_du_bunker_de_la_mairie.md
beat_aymeric_cesse_de_chercher_une_r_ponse_la_question_de_son_humanit_…md
beat_sur_la_place_de_la_mairie_aymeric_affronte_mike_tesnov_son_miroir_invers_…md
```

La collision est fréquente : `é`, `è`, `ê`, `à`, `â`, `î`, `ô`, `û` → tous `_`.
Le résultat est des slugs **illisibles et ambigus** (`travers_e` = traversée ou
traverse ?). La translittération standard (`é`→`e`, `è`→`e`, `à`→`a`, etc.) — le
comportement attendu et standard sur tous les outils comparables — suffirait à
régler le problème.

**Statut :** la translittération est apparemment déjà corrigée pour les *nouveaux*
fichiers. Le problème restant est donc la **migration des fichiers existants** :
les dossiers et fichiers créés pendant la session 1 portent encore les anciens
slugs cassés. Un script de migration (renommage + mise à jour des `[[wikilinks]]`
dans tout `world/`) serait nécessaire pour assainir la base. Sans lui, les anciens
chemins (`s_quence_5_l_assaut/`, etc.) coexistent indéfiniment avec les futurs
slugs propres, ce qui fragmente les liens.
