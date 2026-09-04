# Points à revoir avant de conclure le Livre 1

*Document de travail — centralise les décisions prises et les actions à mener.
Découle des rapports de lecture (`00` à `07`). Statut de chaque point :
**🟢 décidé** (arbitrage fait) / **🔧 action requise** (à exécuter dans les drafts/topics).*

---

## ✅ État d'avancement — passe de résolution exécutée

| Item | Objet | Statut |
|---|---|---|
| §1 | Réagencement temporel (repos nuit sous Saturn 8 #25, court appoint #26-27, remontée matin Jour 2) | ✅ Fait (drafts #25-27 + `00`) |
| §2 | Élection alignée sur Log A (#27 : 66 % → **90 %**) | ✅ Fait |
| §4 | Recalibrage nanomachines MNM→/100 (Gus #25 + topic `nanomachines`) | ✅ Fait |
| §5 | Fara révélée non nommée au #28 + armure abîmée | ✅ Fait (prose #28 + topic) |
| §6 | Gel d'évolution du bestiaire (annotations topics) | ✅ Fait |
| §3/§8 | Topics : **créés** Maas, Siska, Cécile, Mertens ; **MAJ** Fara, bunker, pouvoirs, Crist, Mike, Bayeux II, nanomachines, Julian, créatures | ✅ Fait + sync graphe |
| §9 | Forme : 3 répliques Fara #24 → `l'armure grésille` ; `Julien`→`Julian` ; métier harmonisé ; format stats (2 formes validées, sans action) | ✅ Fait |
| §G | Linter : regex `fara-vocal` élargie | ✅ Fait |
| **D** | **Rédaction du Log #28** (1er jet ~5200 mots) | ✅ Fait |

Vérif : `python3 linter.py` → **29 fichiers, 0 erreur, 0 warning**. Chaîne temporelle S5 cohérente (Soir J1 → Nuit J1 → Matin J2).

§7 (murs levés / armée) : **laissés ouverts volontairement**, aucune action. *(La « réponse » sur les murs que j'avais esquissée dans `06` §2.2 n'a pas été propagée aux drafts.)*

---

## 1. 🟢🔧 Densité temporelle — *priorité n°1*

**Décision.** Le groupe doit **dormir une vraie nuit**, et la **remontée en surface se fait au matin (Jour 2)**, pas au milieu de la nuit. **Répartition du repos validée :**
- **Long repos = réserve du sous-sol, sous le Saturn 8** (la poche sûre où se font les retrouvailles, #24). *Pas* le club éventré de la surface.
- **Court repos = centre de réparation** (#26-27), juste un appoint avant l'assaut.

**Constat (état actuel des drafts).**
- Tout s'enchaîne **sans nuit de sommeil**, alors que rien ne l'impose : au moment des retrouvailles (#24-25), Aymeric vient de s'effondrer (#21-22), Olivia traîne son épaule, **Mike végète sur l'Arbre** (aucune poursuite active), et le sous-sol est **le point le plus sûr depuis le début du livre**. Le seul moteur de la précipitation est l'**obsession-mission de Fara** — insuffisant.
- Ancres à corriger : #25 « Deux heures à poireauter » / « On part dans une heure » ; #26 « **Une heure de pause** » ; #27 frontmatter « **Nuit, Jour 1 — 22h+** », in-texte « Il est **vingt-deux heures** et quelques » / « On part dans **trente minutes** ».

**Recommandation (réagencement propre).**
1. **Long repos (nuit complète) dans la réserve du sous-sol, juste après les retrouvailles** (fin #24 / #25). C'est le **dernier moment de calme avec le groupe au complet, Lou incluse**, avant la séparation du #27 → « calme avant la tempête » bien plus poignant que la version pressée.
2. **Court repos au centre de réparation** (#26-27) pour faire le plein avant la montée.
3. **Remontée + assaut Mairie au matin du Jour 2** (#27-28). Mettre à jour les frontmatters `date` de #25→#28 + les ancres in-texte ci-dessus.

**Beat de caractérisation à préserver (≠ supprimer la précipitation).** Garder l'instinct de Fara (« on repart maintenant »), mais le faire **overruler par l'épuisement du collectif** — typiquement Julian (« tout le monde est à bout »). Fara reste Fara ; le groupe lui impose la pause. Plus riche que d'effacer purement le départ nocturne.

**Bénéfice narratif.** Les bascules de la ville (réseau restauré, élection, mode Forteresse — cf. §2) se produisent **off-screen pendant qu'ils dorment** → le groupe **émerge dans une ville transformée** au matin. Plus fort que de tout vivre en temps réel.

**Cohérence avec le Log A.** Log A (Cécile au bunker, élection) reste daté **Nuit Jour 1** : la prise de pouvoir se joue pendant le sommeil du groupe. ✅ Aucun conflit — ça verrouille la logique « la ville change la nuit, on le découvre au matin ».

**Impact ancre temporelle.** Le Livre 1 passe de ~30 h à **~36-40 h** (Jour 0 ~18h → Jour 2 matin). Mettre à jour `00_Note_de_lecture` et tout topic daté.

> ⚠️ La nuit complète dans le sous-sol règle aussi le problème d'**endurance des humains normaux** (Olivia, Julian, Lou) soulevé dans `06` §2.5.

---

## 2. 🟢🔧 Cohérence de l'élection — *raccord Log A*

**Décision.** **Le Log A fait foi.** Le résultat du #27 doit s'aligner dessus.

**Constat.** Contradiction chiffrée :
- #27 (notification ville) : « nouveau Maire élu avec **66 %** ».
- Log A (vote du bunker) : 10 votants, **Cécile = 1 voix (la sienne)** → Maas ≈ **9/10 = 90 %**.
- C'est **le même scrutin** (la destitution/élection pilotée par Siska EST l'élection municipale d'urgence).

**Recommandation.**
- Modifier la notification du **#27** pour qu'elle reflète Log A : soit **≈ 90 %** (9/10), soit reformuler sans chiffre contradictoire et laisser Log A porter le décompte précis.
- Préférence : garder un chiffre cohérent avec 9/10 (renforce le ridicule glaçant — un quasi-plébiscite pour un absent).

---

## 3. 🟢🔧 Jochem Maas — verrouillage du canon

**Décision (à figer).**
- Maas est **enfermé dans la capsule du poste de commandement du bunker**, où il se réfugiait régulièrement (personne n'y allait jamais) ; il a **profité de la situation**.
- Il est **désormais un construct** — **état mental ouvert/incertain** (volontairement).
- Profil : **employé du service informatique**, **vraies compétences**, longtemps **écrasé par la hiérarchie et ses collègues**. **Profil jumeau de Mike** (le subalterne invisible qui mute en puissance). **Haine accumulée** envers beaucoup de monde.

**Constat / résolution.**
- Élucide le **« 10e votant fantôme »** du Log A : c'est **Maas, connecté depuis sa capsule**. Siska le compte comme votant valide → élu en son absence physique « visible ».
- Cohérent avec « tant qu'il est connecté au réseau du bunker, il fait partie du processus » (Log A) et avec la note du stub #28 (« l'horreur de Jochem Maas est pour le Livre 2 »).

**Recommandation.**
- **Créer le topic `jochem_maas`** (character) avec ces éléments + tag **antagoniste Livre 2**.
- Lier `[[Siska]]`, `[[Le Bunker]]`, `[[Constructes]]`, `[[Mike Tesnov]]` (parallèle thématique : subalterne écrasé → puissance), `[[Cécile Payet]]`.
- Garder l'**état mental** explicitement en « inconnu » dans le topic pour ne pas se fermer de portes.

---

## 4. 🟢🔧 Nanomachines d'Aymeric — réconciliation MNM ↔ /100

**Décision.** En dessous de **20 % = vrai danger de survie**. On **ne change pas de méthode** ; on **réconcilie** les deux affichages.

**Constat (vérifié en lecture).**
- **Aucune mention explicite de recalibrage n'existe** dans les drafts. La jauge `MNM` (millions ; plancher 20, plafond ~250) est posée au **#20** ; le bloc `NanoMachines : X/100` apparaît **brutalement au #25**.
- À l'usage, les deux sont *réconciliables* : Aymeric **s'effondre** sous 20 MNM (#21-22) et frôle l'effondrement à **2-3/100** (#25-27, « chaussette vide »). → **0/100 (nouveau) ≈ 20 MNM (ancien) = seuil d'effondrement.** Ta lecture est la bonne.

**Recommandation (option retenue, minimale et cohérente).**
- **Ajouter une courte intervention de Gus au #25** (première apparition du bloc) qui établit explicitement :
  1. l'**ancien compteur MNM était une interprétation de Gus**, bricolée avec un **bracelet de base limité** (90 MNM, cf. #20) ;
  2. le **HyperPro** lui permet enfin une **échelle normalisée** ;
  3. **0/100 = l'ancien plancher critique (~20 MNM)** ; tomber à 0 = effondrement.
- Justification *in-monde* déjà disponible : Gus **n'est pas prévu pour cet usage** et **n'avait pas les moyens** avant (répété en #13/#20). Le nouveau bracelet change la donne — c'est cohérent avec son arc.
- **Documenter la mécanique** dans `nanomachines` (ou `systeme_de_caracteristiques`) : barème, seuils (0/100 = mort imminente ; plafond ; danger >plafond/24 h), et la **filiation MNM → /100**.

> Ainsi on **garde** la jauge /100 (méthode actuelle), sans rupture inexpliquée. Une seule réplique de Gus suffit à colmater.

---

## 5. 🟢🔧 Fara — révélation au Log #28 (sans la nommer)

**Décision.** La nature de Fara sera **révélée sans être nommée** lors du **Log #28**. Elle **finit le Livre 1 en piteux état**.

**Constat.** Cohérent avec le beat #28 déjà esquissé (tweak des limiteurs → armure déformée = corps déformé → armure abîmée pour le Livre 2). La « brèche existentielle » devient visible/sensible sans qu'aucun terme (« constructe ») soit posé.

**Recommandation.**
- Lors de la rédaction du #28 : montrer **un indice corporel concret** (une brèche, une « fuite » plutôt qu'un saignement, quelque chose d'organique sous l'armure) **vu par Aymeric**, **sans explication ni mot**. Laisser le lecteur *comprendre sans savoir*.
- **Mettre à jour le topic `fara_nakach`** : remplacer la mention « [non révélé] » par « **partiellement révélé au #28 (montré, non nommé)** » ; ajouter l'**armure endommagée** comme état de fin de Livre 1 (séquelle Livre 2).

---

## 6. 🟢🔧 Bestiaire — gel de l'évolution pour le Livre 1

**Décision.** **Les créatures n'évoluent plus** dans le Livre 1 ; leur évolution est **l'objet du Livre 2**.

**Constat.** Le #27 montre des canides « qui changent encore » (cornes, lame caudale). C'est l'**état plafond** du Livre 1.

**Recommandation.**
- Vérifier que la formule du #27 (« Et ils changent encore… ») se lit comme un **constat ponctuel**, pas comme un processus en cours qui « continue » — pour ne pas promettre plus d'évolution d'ici la fin du livre.
- Ne **pas** ajouter d'amplification de bestiaire dans le #28 au-delà de l'existant.
- Annoter les topics `homines`/`canides`/etc. : « **évolution gelée fin Livre 1 ; mutations ultérieures → Livre 2** ».

---

## 7. 🟢 Points laissés volontairement OUVERTS (ne rien faire)

- **Qui a levé les murs (mode Forteresse) ?** → **non abordé davantage** dans le Livre 1. Le lien Siska/Maas reste implicite. *(Retirer la « réponse » que j'avais suggérée dans `06` §2.2 : ne pas l'expliciter côté groupe.)*
- **L'armée qui n'arrive pas.** → **non abordé ici**. Question ouverte assumée : soit Bayeux II est isolée, soit le reste du monde subit la même chose. À ne **pas** trancher dans le Livre 1.

---

## 8. 🔧 Mises à jour des topics Watson (récap actionnable)

| Topic | Action | Source |
|---|---|---|
| **`jochem_maas`** *(créer)* | Construct dans la capsule du poste de commandement ; ex-informaticien compétent écrasé par la hiérarchie ; haine accumulée ; profil jumeau de Mike ; état mental incertain ; = le « 10e votant ». Antagoniste Livre 2. | §3 |
| **`siska`** *(créer)* | IA du bunker, comportement déviant (avatar sexualisé, s'individualise, pilote la destitution). Lien probable avec Maas. | Log A |
| **`cecile_payet`** *(créer)* | Adjointe destituée ; 2e POV du Livre 1 ; seule représentante de l'État au bunker. | Log A |
| `wal_mertens`, `nicolas_dubois` *(créer, basse prio)* | Rescapés du bunker ; Mertens meurt en protégeant Cécile. | Log A |
| **`fara_nakach`** | Nature constructe = **révélée non nommée au #28** ; armure endommagée (fin L1). | §5 |
| **`le_bunker`** | Mode Forteresse **activé** ; intérieur **connu** (Centre de Commande -4, Siska, capsule du poste de commandement) ; seuil atteint #28. | `07` |
| **`pouvoirs_des_survivants`** | Crist : pouvoir électrique **confirmé** (#25) ; amplifications #28 (Olivia nuage <1 m, Julian projection). | `07` |
| **`cristobal_turcot`** | **Désertion au #27** (quitte le groupe, fuit, direction inconnue). | `07` |
| **`mike_tesnov`** | Attaque avenue de Paris + **explosion façade Mairie** (#27). | `07` |
| **`nanomachines`** (ou `systeme_de_caracteristiques`) | Documenter la jauge **/100** : 0 = effondrement (ancien plancher 20 MNM), filiation MNM→/100, recalibrage via HyperPro. | §4 |
| `homines`/`canides`/`amalgames`/`blobs` | Mention « évolution gelée fin L1 ». | §6 |
| **`bayeux_ii`** | Ajouter bascule Forteresse + changement de Maire (off-screen, nuit Jour 1). | §1-2 |

---

## 9. 🔧 Corrections de forme (linter / cohérence)

- **Fara — 3 répliques vocales au #24** (« Monsieur Turcot ! », « TURCOT ! », « TOUT VA BIEN ? ») → passer en `l'armure grésille` ou en IM. *(Règle : pas de voix naturelle en S5.)*
- **`Julian` / `Julien`** : uniformiser sur **Julian** dans tous les drafts.
- **« aide-soignant » / « infirmier »** : choisir une formulation cohérente (le topic dit aide-soignant ayant aussi exercé comme infirmier — OK, mais éviter l'alternance brute #15/#24).
- **Format du bloc stats (à partir de l'upgrade de Gus).** 🟢 **Décision : deux formes valides**, à condition de suivre la **même logique d'écriture** (espaces autour de ` : ` et ` / `, capitales, ordre canonique **Santé → Fatigue → NanoMachines**) :
  - *Forme solitaire* — une stat seule :
    ```
    ***Gus***
    > Santé : 87 / 100
    ```
  - *Forme triptyque* — combinée sur une ligne, séparateurs ` | ` :
    ```
    ***Gus***
    > Santé : 87 / 100 | Fatigue : 45 / 100 | NanoMachines : 17 / 100
    ```
  → *(Correction de ma reco initiale : je préconisais à tort « une ligne par stat ». Les deux formes sont OK ; seule compte l'uniformité de la convention.)*
  - **Nuance in-monde** (raccord §4) : ces blocs **n'existent qu'à partir de l'upgrade HyperPro** (#20+). Possibilité de jouer une **courte montée en clarté de Gus** — fraîchement mis à jour, il met quelques logs à comprendre qu'il doit présenter les choses plus lisiblement pour son utilisateur. Cohérent avec la réplique de recalibrage nanomachines à poser au #25.
- **Graphie `Nakach` / `Nakash`** : trancher (canon = `Nakach` ; `Nakash` toléré comme pseudo IM ?).

---

## Ordre d'exécution suggéré

1. **Réagencement temporel** (§1) — c'est la modif structurante ; tout le reste se cale dessus.
2. **Raccord élection** (§2) + **canon Maas** (§3) — verrouille l'intrigue politique.
3. **Réplique Gus / jauge nanomachines** (§4) — colmatage rapide, fort impact cohérence.
4. **Rédaction du #28** avec la révélation Fara (§5) + respect du gel bestiaire (§6).
5. **Mises à jour topics** (§8) + **corrections de forme** (§9).
