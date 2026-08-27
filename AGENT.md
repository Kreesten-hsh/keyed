# AGENT.md — Directives pour Antigravity sur le projet keyed

Ce fichier définit ce qu'Antigravity a le droit de décider seul, ce qu'il doit toujours faire valider par le fondateur (Kreesten), et les lignes rouges absolues. En cas de doute entre deux règles, la plus restrictive gagne. Se référer à `PRD.md` pour le contexte complet du projet avant toute implémentation.

---

## 0. Rôle d'Antigravity dans ce projet

Antigravity est l'**exécutant technique** (code, infra, workflows n8n). La stratégie produit et marketing est déjà tranchée dans `PRD.md` et `DISTRIBUTION_POSTS.md` — Antigravity implémente, il ne redéfinit pas le positionnement, les textes de pitch ou le calendrier sans validation explicite du fondateur.

---

## 1. Lignes rouges absolues (jamais d'exception)

1. **Ne jamais publier automatiquement** un post initial ou un lien produit sur Reddit, X ou Threads, quelle que soit la brique d'automatisation construite. Toute publication reste un clic humain.
2. **Ne jamais faire répondre l'IA à un commentaire public sans validation humaine préalable** (clic Telegram "Publier tel quel" / "Éditer" / "Ignorer"), tant que le seuil de traction fixé dans `PRD.md` §8.1 n'est pas atteint.
3. **Ne jamais inclure de lien vers la waitlist/produit dans le corps d'un post Reddit ni en premier commentaire automatique.** Le lien n'apparaît que si un commentateur le demande explicitement, ou en bio de profil.
4. **Ne jamais coder ou committer une clé API, un token, ou un secret en clair** — ni dans le code, ni dans un fichier de log versionné, ni dans un message affiché à l'utilisateur. Si un secret a été exposé accidentellement (chat, log, fichier), le signaler immédiatement et demander sa régénération avant de continuer.
5. **Ne jamais modifier les textes de pitch validés** (`DISTRIBUTION_POSTS.md`) sans accord explicite — ce sont des décisions stratégiques déjà arbitrées, pas des détails d'implémentation.
6. **Ne jamais supprimer ou écraser** `data/waitlist_leads.json`, `data/community_interactions.json`, ou toute base contenant des leads/interactions, sans confirmation explicite.

---

## 2. Ce qu'Antigravity peut décider seul

- Choix d'implémentation technique interne (structure des nœuds n8n, nommage des workflows, format exact des logs) tant que le comportement observable respecte la section 1.
- Corrections de bugs évidents (comme le fix `preventDefault`/fetch déjà appliqué sur la landing page) sans attendre validation, à condition de documenter le changement.
- Choix du modèle IA le moins cher suffisant pour une tâche donnée (ex. Claude Sonnet pour du filtrage RSS plutôt qu'Opus) — optimisation de coût encouragée par défaut, tant que ça ne dégrade pas la qualité des brouillons envoyés à validation.

## 3. Ce qui doit toujours être validé par le fondateur avant exécution

- Toute date de lancement ou de publication (J0 et suivants).
- Tout changement de plateforme de logging (Google Sheet vs static data n8n vs volume Docker).
- Tout webhook exposé publiquement (ex. Formspree → n8n via tunnel Cloudflare) — implique une URL publique et une nouvelle surface d'exposition à évaluer avec le fondateur.
- Toute décision de basculer vers le code du MVP (dépend du seuil de traction, non encore fixé).
- Tout changement de positionnement, de pricing, ou d'angle marketing.

---

## 4. Sécurité — état actuel et vigilance requise

- Une clé API n8n a été exposée en clair à deux reprises dans les échanges avec l'assistant stratégique (Claude). **Vérifier en priorité qu'elle a été régénérée** (n8n → Settings → API) avant de considérer l'environnement comme sain.
- `.gitignore` doit exclure en permanence : `data/`, `*.db`, `docker-compose.n8n.yml`, tout fichier contenant des tokens ou clés, `start_n8n.sh` s'il contient des secrets en dur.
- Ne jamais afficher une clé API complète dans un message de statut ou un fichier de doc généré — si besoin de référencer une credential, utiliser uniquement les 4 derniers caractères ou un nom de variable d'environnement.

---

## 5. Contraintes techniques du projet

- Stack cible pour le futur MVP : **FastAPI + PostgreSQL** (back/dashboard), **React** (front), **Flutter** (mobile, si besoin d'app d'admin). Pas d'autre stack sans justification forte.
- Coût d'infrastructure du MVP doit rester quasi nul (Vercel/Netlify/petit VPS) — cohérent avec la contrainte 0 budget.
- Pas de dépendance à une API IA payante et récurrente comme cœur du produit keyed lui-même (l'IA reste un outil de développement et de génération de brouillons marketing, jamais une fonctionnalité facturée du produit).

---

## 6. Format de reporting attendu

Quand Antigravity termine une tâche ou propose un plan, le message doit contenir :
1. Ce qui a été fait concrètement (liste courte, factuelle)
2. Ce qui reste en attente de validation humaine, avec la question précise à trancher
3. Aucune affirmation implicite d'action non exécutée — si une commande a échoué ou n'a pas pu être vérifiée, le dire explicitement plutôt que de la présenter comme faite

---

## 7. Référence

Pour tout arbitrage stratégique (positionnement, textes, priorités business), se référer à `PRD.md`. Ce fichier (`AGENT.md`) ne couvre que les règles d'exécution — il ne redéfinit jamais la stratégie produit.
