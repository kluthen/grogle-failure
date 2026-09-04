# Rapport — Delta lecture ↔ topics Watson

*Objectif : garantir que les topics sont à jour avec le contenu réel des drafts.
Watson n'offre pas (encore) de `get_topic` indexé sur la timeline → on entretient
ici manuellement la « couverture temporelle » de chaque topic.*

**Méthode :** comparaison de la lecture intégrale (Logs #1-28 + Log A) avec les
topics du dossier `world/`. Trois catégories : **topics manquants**, **topics à
mettre à jour**, **topics en avance sur la narration** (canon auteur ≠ révélé).

---

## 1. 🔴 Topics MANQUANTS (à créer)

Tous issus du **Log A** (interlude POV Cécile Payet) — non couvert par la base.

| Topic à créer | kind | Importance | Notes |
|---|---|---|---|
| **Jochem Maas** | character | 🔴 Haute | Nouveau Maire de Bayeux II (élu Log #27 & Log A), employé lambda absent/fantomatique. Probable antagoniste politique du Livre 2. Fils d'immigré néerlandais (perçu par Cécile, POV biaisé). Mentionné aussi dans la note du stub #28 (« l'horreur de Jochem Maas est pour le Livre 2 »). |
| **Siska** | character (IA) | 🔴 Haute | IA du bunker, comportement déviant (avatar sexualisé, s'individualise, pilote la destitution). Antagoniste IA potentielle. À lier à `La Mise à jour` et `Le Bunker`. |
| **Cécile Payet** | character | 🟠 Moyenne | Adjointe à la Maire, **unique second POV du Livre 1**. Destituée. Seule représentante de l'État côté bunker. |
| **Wal Mertens** (M. Mertens) | character | 🟢 Basse | Vieux technicien, meurt dans le monte-charge en protégeant Cécile. |
| **Nicolas Dubois** | character | 🟢 Basse | Listé en `presence` du Log A ; à confirmer/identifier (rescapé du bunker). |

> **Topics présents et OK** pour les nouveaux venus de la Séquence 5 :
> `armande_legrand` (Armande), `chahid_azuri` (Chahid), `yannick`, et **Santu Ricci**
> (⚠️ stocké dans le fichier `world/characters/yoan.md` — `name: Santu Ricci`,
> alias Yoan/Yoann ; nom de fichier trompeur mais topic valide).

---

## 2. 🟠 Topics à METTRE À JOUR (obsolètes/incomplets)

| Topic | Couverture actuelle | Manque / à corriger |
|---|---|---|
| **`pouvoirs_des_survivants`** | ~#25 | **Crist : « indice non confirmé, piste de brouillon »** → en réalité **CONFIRMÉ** (Log #25, arc électrique sur Raoul + drones grillés). Mettre à jour. Ajouter les **amplifications du beat #28** (Olivia → nuage déconstructeur <1 m ; Julian → projection à distance). |
| **`le_bunker`** | ~#23 | Dit « défenses **inactives** faute d'enclenchement » et « **non encore atteint** ». Or : **mode Forteresse activé** (#26-27), **murs levés**, **défenses automatisées** (non-létal→létal) ; seuil **atteint** (#28) ; **intérieur connu** via Log A (Centre de Commande -4, Siska, Cécile). À réécrire. |
| **`cristobal_turcot`** | ~#25 | Ne mentionne pas son **DÉPART** : Crist **quitte `SuvivantsConscrits_1` et fuit** pendant la course vers la Mairie (#27, « C. Turcot a quitté »). Statut fin Livre 1 = **déserteur, direction inconnue**. |
| **`mike_tesnov`** | ~#22 (Arbre de la Liberté, « big boss ») | Ne couvre pas le **#27** : Mike **descend de l'Arbre, attaque l'avenue de Paris, puis explose la façade de la Mairie** (« FAAARAAA ») au seuil du groupe. Étendre l'History. |
| **`fara_nakach`** | très détaillé jusqu'à #28 | RAS sur le fond. Mais signaler en interne que **la nature constructe = canon non révélé** (cf. §3). Vérifier la graphie Nakach/Nakash. |
| **`bayeux_ii`** | bonne base | Ajouter l'**état Forteresse** et la **bascule politique** (Maire destitué/élu) comme événement majeur d'History. Lier `Le Bunker` à jour. |

---

## 3. 🟡 Topics EN AVANCE sur la narration (canon auteur ≠ révélé au lecteur)

À garder mais **distinguer explicitement** ce qui est *établi* de ce qui est *montré* :

| Topic | Écart |
|---|---|
| **`fara_nakach`** | La **nature constructe** (exosquelette = corps, masse fluide, brèche existentielle, cerveau flottant) est documentée **comme un fait**. Dans les drafts, ce n'est **jamais révélé** — seulement suggéré (visière baissée, voix synthétique, armure jamais retirée). → Le topic est un *bible/canon auteur*, pas l'état des connaissances du lecteur. Ajouter une mention « **[non révélé en Livre 1]** » sur cette section pour éviter qu'un futur passage l'« explique » par erreur comme un acquis. |

---

## 4. ⚠️ Incohérences à arbitrer (impactent les topics)

1. **Élection de Maas : 66 % (#27) vs 9/10 (Log A).** Cf. `06_Rapport_Ville_et_Situation` §2.1. Décider : deux scrutins distincts, ou un seul à harmoniser. **Le topic `Jochem Maas` (à créer) doit figer la bonne version.**
2. **Fara — 3 répliques vocales non filtrées au Log #24** (« Monsieur Turcot ! », « TURCOT ! », « TOUT VA BIEN ? »). Contraires à la règle « IM / haut-parleur d'armure uniquement en S5 ». **À corriger dans le draft** (note projet déjà connue). N'impacte pas le topic, mais le confirme.
3. **Système nanomachines : double unité.** Jauge **« MNM »** (millions, plafond ~250, plancher 20) en #20-22 vs **« NanoMachines : X/100 »** dans le bloc litRPG depuis #25. **Aucun topic ne documente cette mécanique de jauge.** → Recommandation : créer/compléter `systeme_de_caracteristiques` (ou `ruche_nanomachines`) avec : barème MNM, seuils (effondrement <20, danger >250/24 h), et la **relation MNM ↔ /100** (à définir). Sinon risque d'incohérence future.
4. **Format du bloc stats litRPG.** Le Log #25 écrit `Santé : 87 / 100 | Fatigue : … | NanoMachines : …` (ligne unique). Le guide impose une ligne par stat (`> Santé : 87 / 100`). À trancher (linter `stat-format`).
5. **Stats : à partir du Log #20 ou #25 ?** CLAUDE.md dit « stats à partir du Log #20 (upgrade HyperPro) ». Dans les faits : la **jauge MNM** apparaît #20 ; le **bloc Santé/Fatigue/NanoMachines** n'apparaît qu'au **#25** (via Jaz + HyperPro opérationnel). Préciser la formulation pour le linter (la règle `stats-before-upgrade` reste correcte : rien avant #20).
6. **Orthographe « Julian / Julien »** (texte) et **métier « aide-soignant / infirmier »** : flottements dans les drafts (cf. `04_Rapport_Julian`). Le topic est cohérent ; **corriger les drafts**.

---

## 5. Couverture temporelle des topics (synthèse)

*« Jusqu'à quel log le topic reflète-t-il la lecture ? »* — à défaut d'index Watson.

| Topic | À jour jusqu'à | Action |
|---|---|---|
| `aymeric_bator` | ~#25 (stats Jaz, ruche) | ✅ Bon ; ajouter contrôle ruche 30 % (#27) si désiré |
| `fara_nakach` | #28 (beats) | ✅ Bon ; marquer « non révélé » sur la nature constructe |
| `lou_humbert` | #27 | ✅ Bon (pouvoir latent confirmé) |
| `julian_leroy` | #25 | 🟠 Ajouter projection à distance (beat #28) ; vérifier orthographe |
| `olivia_perez` | #25 | 🟠 Ajouter amplification (beat #28) |
| `cristobal_turcot` | #25 | 🟠 Ajouter départ/désertion (#27) |
| `mike_tesnov` | #22 | 🟠 Ajouter attaque Mairie (#27) |
| `pouvoirs_des_survivants` | #25 | 🟠 Crist confirmé + amplifications #28 |
| `le_bunker` | #23 | 🔴 Réécrire (Forteresse, intérieur via Log A) |
| `bayeux_ii` | base | 🟠 Forteresse + bascule politique |
| `la_mise_jour_3_4_3ef`, `amalgames`, `blobs`, `mairie` | stables | ✅ RAS notable |
| **Cécile Payet, Jochem Maas, Siska, Wal Mertens, Nicolas Dubois** | — | 🔴 **À créer** |

---

### Recommandation de priorisation (si une seule passe de mise à jour)
1. Créer **Jochem Maas** + **Siska** (enjeux Livre 2).
2. Réécrire **`le_bunker`** (Forteresse + intérieur).
3. Mettre à jour **`pouvoirs_des_survivants`** (Crist confirmé) et **`cristobal_turcot`** (désertion).
4. Documenter la **mécanique de jauge nanomachines** (MNM ↔ /100) dans un concept.
5. Arbitrer l'**incohérence des 66 % / 9-10** avant de figer le topic Maas.
