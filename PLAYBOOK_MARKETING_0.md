# Playbook Marketing 0€ — keyed
*Synthèse stratégique, complémentaire à `PRD.md` et `DISTRIBUTION_POSTS.md`, ne les remplace pas.*

---

## 0. Ce que j'ai lu avant d'écrire ça

Le repo `keyed` (`AGENT.md`, `PRD.md`, `DESIGN.md`, `DISTRIBUTION_POSTS.md`, `index.html`, `waitlist.html`) + les 3 études de cas fournies :
- **Jake / Erly** : 0 → 50K$/mois en 4 mois, via UGC influenceurs payés (CPM 2-3$) sur TikTok/Instagram.
- **Benji / Snag** : 0 → 30K$ MRR, via clone-amélioré + UGC + ads Meta/TikTok scalées sur ROAS.
- **Mike Hill / Teachizy** : marketing 0€ pur — contenu, communautés, SEO, netlinking, affiliation.

**Point important à te signaler tout de suite** : les playbooks Jake et Benji reposent structurellement sur du budget publicitaire (CPM aux créateurs, tests ads à 50-300$/jour, Mixpanel à 400$, Superwall). Ce ne sont pas des détails, c'est le moteur de leur croissance. À 0€, on ne peut pas transposer *le mécanisme*, seulement *les principes sous-jacents*. Le seul des trois qui est nativement 0€ de bout en bout, c'est Mike Hill. Le plan ci-dessous part de lui, et récupère de Jake/Benji uniquement ce qui survit sans budget.

---

## 1. Ce qui se transfère de Jake & Benji (sans le budget)

| Principe original | Version 0€ pour keyed |
|---|---|
| "Le dev n'est pas le goulot, la distribution l'est" | Déjà acté dans le PRD (§3.1 : valider avant de coder). Continuer à protéger le temps de pub plutôt que d'ajouter des features au MVP. |
| "Cloner un produit qui marche déjà + améliorer de 10%" | Déjà fait : Unkey validé le marché, keyed prend le vide qu'il laisse (LTD vs abo, simplicité vs plateforme). Rien à changer, juste ne pas dériver. |
| "Verrouiller un seul produit, éviter le syndrome de l'objet brillant" | Directement aligné avec `AGENT.md` §3 : pas de pivot de positionnement sans validation. |
| Power law / gros coups ponctuels | Sans budget, le "gros coup" ne vient pas d'un CPM qui explose, mais d'un post qui prend sur Reddit/HN ou d'une page SEO qui rank. Même logique : publier souvent, accepter que 9 posts sur 10 ne fassent rien, ne pas juger un canal sur un seul essai. |
| Tracking par corrélation de pics | Remplace Mixpanel (400$) par : Cloudflare Web Analytics (gratuit, sans cookie) sur la landing page + horodatage des soumissions Formspree. Si un post sort à 14h et que les inscriptions sautent entre 14h et 16h, le lien est fait à l'oeil, pas besoin d'outil payant. |

Ce qui **ne** se transfère **pas** : payer des créateurs (même à bas CPM, ça reste du budget), acheter des vues, A/B tester des paywalls avec Superwall. On les met de côté tant que le seuil de traction (PRD §8.1) n'est pas fixé et qu'il n'y a pas de premier cash-flow LTD.

---

## 2. Les 5 leviers Mike Hill appliqués à keyed

### 2.1 Contenu texte (le seul format compatible avec la contrainte "jamais de caméra")

Deux couches distinctes, à ne pas mélanger :
- **Couche promo** : déjà figée dans `DISTRIBUTION_POSTS.md` (posts A/B/C, thread X, post Threads). Je n'y touche pas — `AGENT.md` §1.5 est clair là-dessus, et je m'applique la même règle.
- **Couche communautaire** : contenu quotidien/hebdo sans lien produit, qui construit la crédibilité entre deux jalons promo. Si un `COMMUNITY_CALENDAR.md` a déjà été discuté dans une session précédente, il n'est **pas présent dans le repo actuel** — seuls `AGENT.md`, `DESIGN.md`, `DISTRIBUTION_POSTS.md`, `PRD.md`, `index.html`, `waitlist.html` sont clonés. À toi de me dire si ce fichier existe ailleurs et doit être resynchronisé, ou si on le reconstruit.

Formats prioritaires vu ta contrainte 0€ : texte sur X/Threads (quotidien, léger), commentaires longs et utiles sur Reddit (pas de posts, des réponses), articles SEO (section suivante). Vidéo et audio explicitement écartés — hors scope de ce projet.

### 2.2 Infiltration des communautés

Déjà en germe dans le calendrier promo (r/SideProject, r/webdev, r/LocalLLaMA). L'ajout Mike Hill, c'est l'entre-deux : **répondre** dans les threads d'autres personnes qui se plaignent d'API key management, de coûts d'infra, ou d'Unkey/Kong, sans jamais poster soi-même un nouveau fil. Zéro lien, juste de l'aide réelle + "je bricole un truc là-dessus, dispo si ça t'intéresse" seulement si la conversation le demande naturellement.

Sous-reddits/communautés à surveiller passivement (pas à spammer) : r/webdev, r/node, r/Python, r/SaaS, r/indiehackers, r/selfhosted (angle "pas de vendor lock-in"). Un compte qui commente utilement pendant 2-3 semaines avant de poster a beaucoup moins de friction karma/mod que ce que fait `DISTRIBUTION_POSTS.md` en solo.

### 2.3 SEO — le levier le plus sous-exploité dans le repo actuel

Aucune page de contenu SEO n'existe encore (seulement `index.html` landing + `waitlist.html`). C'est gratuit à part le nom de domaine (déjà pris, GitHub Pages en plus). Pages à écrire à la main (pas de génération IA en masse, cf. conseil Mike Hill) :

- `keyed vs Unkey` — comparatif honnête, LTD vs abonnement, capte les recherches "unkey alternative", "unkey pricing".
- `How to hash API keys in Node.js` / `... in Python (FastAPI)` — contenu technique réel, capte le trafic dev qui cherche une solution avant même de connaître keyed.
- `API key rate limiting without a gateway` — reprend l'angle du Post B déjà écrit.
- `Scoped, revocable API keys for AI agents` — reprend l'angle marketing "agents IA" du PRD §2.5, sans construire les features enterprise que ça impliquerait.

Chaque page se termine par une mention discrète de keyed (pas un pitch, un lien "je documente ça en construisant keyed"). Techniquement : fichiers `.html` statiques de plus sur le même GitHub Pages, zéro coût.

### 2.4 Netlinking / annuaires — absent du plan actuel, gratuit, à fort ROI pour un dev tool

Le repo ne mentionne aucune soumission à des annuaires. Pour un produit dev anglophone, l'équivalent des "Pépites Tech" citées dans la vidéo, ce sont :
- **Show HN** (Hacker News) — gratuit, forte audience dev exacte, mais un seul essai sérieux (le compte grille vite si le post flop, à traiter comme un jalon promo au même titre que les posts Reddit, avec validation humaine).
- **BetaList, Uneed, Fazier, StartupBase, SaaSHub, AlternativeTo** — soumissions gratuites, backlinks + trafic de découverte.
- **Listes GitHub "awesome-\*"** (awesome-selfhosted, awesome-api-devtools si elles existent) — PR gratuite, backlink durable, crédibilité auprès d'une audience dev qui fait confiance à GitHub plus qu'à une pub.
- **Product Hunt "Upcoming"** — gratuit avant lancement, permet de collecter des followers avant le vrai launch day.

Aucun de ces canaux n'a de coût, mais chacun mérite le même traitement que les posts Reddit : validation humaine du texte, pas d'automatisation, un seul shot bien préparé plutôt que du spam sur 10 annuaires le même jour.

### 2.5 Affiliation / parrainage — activable seulement après le premier cash-flow

Cohérent avec la structure PRD (§3.3 : LTD d'abord, puis contenu SEO, puis marketplace). Le principe "je ne paie que quand la vente est faite" colle exactement à la contrainte 0 budget — donc pas de contradiction avec `AGENT.md` §3 (pricing = décision à valider), mais c'est un levier **post-validation**, pas maintenant. À poser comme question ouverte n°6 dans le PRD plutôt qu'à activer tout de suite.

---

## 3. Ce qu'on laisse explicitement de côté

- Toute dépense CPM/ads, même minime — hors contrainte 0 budget stricte du PRD §4.
- Mixpanel, Superwall, Grow.io, Instantly.ai — remplacés par Cloudflare Web Analytics (gratuit) + lecture manuelle des horodatages Formspree.
- UGC influenceurs — sans budget, sans caméra, structurellement hors scope.

---

## 4. Rappel garde-fou avant d'exécuter quoi que ce soit de tout ça

Deux points du repo à ne pas perdre de vue, indépendamment de la stratégie marketing :
1. **Sécurité** : `PRD.md` §6 et `AGENT.md` §4 signalent qu'une clé API n8n a été exposée en clair deux fois dans des échanges avec un assistant. Si ce n'est pas déjà fait, vérifie qu'elle a été régénérée avant de considérer quoi que ce soit d'autre.
2. **Discipline de publication** : rien de ce document ne doit partir automatiquement. Chaque post, chaque soumission d'annuaire, chaque page SEO passe par ta validation manuelle, exactement comme le prévoit déjà `AGENT.md` §1.

---

## 5. Ce qui reste à trancher avec toi

- Le `COMMUNITY_CALENDAR.md` mentionné dans une session précédente existe-t-il ailleurs et doit-il être resynchronisé dans ce repo, ou on le reconstruit à partir de ce document ?
- Priorité d'exécution : je peux rédiger les 4 pages SEO listées en §2.3 maintenant, ou les textes de soumission pour Show HN / BetaList / Product Hunt Upcoming — lequel en premier ?
- Confirmation que la clé API n8n a bien été régénérée (bloquant pour tout le reste tant que ce n'est pas fait).
