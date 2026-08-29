# PRD — keyed
*Dernière mise à jour : 29 août 2026*

---

## 1. En une phrase

**keyed** est un gestionnaire de clés API minimaliste (hash, scope, rate-limit, revoke) vendu en paiement unique (Lifetime Deal), pensé pour les développeurs solo et indie hackers fatigués des abonnements d'infra à 25-50$/mois.

---

## 2. D'où vient ce projet

### 2.1 Le candidat derrière le projet
Développeur solo béninois, 20 ans, en 3e année (L3) informatique à HECM Cotonou (spécialisation Systèmes Informatiques et Logiciels). Stack maîtrisée : FastAPI, PostgreSQL, React, Flutter. En parallèle de ses candidatures académiques (KAUST VSRP, Master Open Doors 2026), spécialisation choisie en cybersécurité : IAM et gouvernance des identités non-humaines (NHI).

### 2.2 Le point de départ
Analyse du **Playbook SaaS de Mike Hill** (5 SaaS à 200K$ MRR cumulés) comme grille de filtrage stricte :
- Ne jamais choisir une idée "révolutionnaire" ou dépendante d'API IA chères — préférer une idée déjà validée par des concurrents existants ("used idea")
- MVP suffisant, lancé vite
- Toujours faire payer dès le début (jamais de gratuit illimité)
- Lifetime Deal comme premier flux de trésorerie
- Design soigné comme différenciateur

### 2.3 Le processus de sélection de l'idée
1. Une première idée du candidat (extension IA pour transformer des cours en vidéos façon TikTok) a été **rejetée** après analyse : dépend d'API IA vidéo coûteuses, concurrence frontale avec NotebookLM (Google), non "ennuyeuse" au sens du Playbook.
2. Recherche approfondie (Deep Research) → 20 idées de micro-SaaS B2B "ennuyeux" candidates, filtrées selon les contraintes réelles : seul, 0 budget, jamais de caméra/visio, marché international USD/EUR, IA comme multiplicateur de dev (pas comme cœur du produit).
3. Un second rapport plus rigoureux a confirmé et affiné la sélection.
4. **Idée retenue : gestionnaire de clés API** — problème déjà validé par des concurrents réels (Unkey, Kong, etc.), techniquement simple pour la stack maîtrisée, coût d'infra quasi nul.

### 2.4 Vérification critique du marché (correction en temps réel)
Le rapport Deep Research se basait sur une photo datée du marché. Vérification web en direct :
- **Unkey** (concurrent principal) a levé **4,5M$ en avril 2026** (YC, Uncork Capital, Cloudflare/fondateurs Supabase/GitHub comme investisseurs/advisors) et devient une plateforme complète de déploiement d'API (gateway, observabilité), pas juste un gestionnaire de clés.
- Le marché de la **gouvernance NHI/agents IA** est en forte croissance mais déjà saturé de gros acteurs financés (Astrix racheté par Cisco, Oasis, Entro, Okta Entra Agent ID, One Identity) — non viable comme cœur de produit à budget zéro.

### 2.5 Conclusion stratégique (le positionnement actuel)
Ne pas copier Unkey frontalement. Viser le vide qu'ils laissent en montant en gamme :
- **Paiement unique (LTD)** plutôt qu'abonnement — un acteur financé par VC ne peut pas structurellement copier ça (besoin de MRR récurrent pour ses investisseurs).
- **Simplicité radicale** contre la complexité croissante d'Unkey (qui devient une plateforme lourde, orientée équipes/entreprises).
- **Narratif "agents IA"** utilisé comme angle marketing/copywriting ("scoped, revocable keys for your AI agents") **sans** construire les fonctionnalités d'audit/gouvernance enterprise que ça impliquerait normalement.

---

## 3. Objectifs

### 3.1 Objectif immédiat (phase actuelle)
Valider la demande **avant** de coder quoi que ce soit. Méthode : poster le pitch (texte seul) sur plusieurs plateformes, mesurer les réactions.
- **Seuil de décision** : nombre minimum d'inscriptions/réactions positives à définir formellement avec le candidat (pas encore fixé) avant de basculer vers le code du MVP.
- **Alternative si échec** : 4 autres idées candidates gardées en réserve par le rapport Deep Research (coffre-fort .env, monitoring uptime/SSL, checklists de conformité).

### 3.2 Objectif produit (si validation positive)
MVP minimal : SDK TypeScript/Node + SDK Python (middleware FastAPI/Flask), hash local (bcrypt/argon2), rate-limiting, révocation instantanée. Architecture pressentie : FastAPI + PostgreSQL pour le cœur/dashboard, éventuellement un Worker Cloudflare léger pour le chemin de vérification à faible latence (repoussable en v2).

### 3.3 Objectif business
Suivre les étapes pertinentes du Playbook Mike Hill adaptées au solo/0 budget :
1. Validation du pitch (en cours)
2. LTD privé (premier cash-flow)
3. Contenu SEO / pages comparatives dès que possible
4. Distribution marketplace (AppSumo) une fois la traction confirmée
5. Avis clients (Trustpilot/G2) pour la crédibilité et le SEO

---

## 4. Contraintes non négociables

- **Seul** — pas de co-fondateurs, pas de budget dédié à des sous-traitants
- **0 budget de départ** — hébergement gratuit (GitHub Pages, Vercel/Netlify), pas de coûts d'infra IA récurrents
- **Jamais de caméra/visio/streaming** — pas de personal branding visuel
- **Marché international**, payé en USD/EUR
- **IA comme multiplicateur de développement** (Claude Code, Codex), jamais comme moteur central du produit — exclusion de tout SaaS dont la valeur dépend d'appels API IA coûteux et récurrents

---

## 5. Positionnement & différenciation

| Axe | keyed | Plateformes enterprise (Unkey, Kong) |
|---|---|---|
| Prix | Paiement unique (LTD, $29-99) | Abonnement $20-50/mo + overages |
| Intégration | 3 lignes de code | Gateway, routage DNS, dashboards lourds |
| Lock-in | Aucun — hash dans la DB du client | Infra propriétaire du vendeur |
| Cible | Devs solo, indie hackers | Équipes d'ingénierie, entreprises |
| Clés agents IA | Scopées, courte durée, révocation 1 clic (angle marketing) | Gouvernance enterprise lourde |

---

## 6. Où en est le projet aujourd'hui (état factuel au 29 août 2026)

- **Page d'attente en ligne** : https://kreesten-hsh.github.io/keyed/ — déployée sur GitHub Pages, formulaire Formspree connecté (`mqaejvqd`).
- **Bug connu identifié et corrigé** dans une version locale du fichier (gestion `fetch`/`preventDefault` correcte + footer 2026) — déployé et synchronisé en production.
- **4 textes de pitch finalisés** (angles A/B/C/D) + thread X + post Threads — version finale et révisée dans `DISTRIBUTION_POSTS.md`, avec correctif anti-spam appliqué (aucun lien dans le post initial ni en premier commentaire automatique).
- **Calendrier de publication défini** : J0 = r/SideProject + Threads, J+1 = thread X, J+3/4 = r/webdev, J+7/8 = r/LocalLLaMA.
- **n8n actif en local** (Docker) avec un workflow Telegram → Claude Opus (via GoRouter) → Telegram, utilisé pour générer des brouillons de réponse aux commentaires. 4 briques supplémentaires en cours de spec/construction : scheduler de rappels, veille RSS Reddit, logging des interactions, webhook Formspree.
- **Alerte sécurité réglée** : Régénération de la clé API n8n confirmée par le fondateur le 29 août 2026.
- **Analytics** : PostHog Cloud US intégré sur `index.html`, `waitlist.html` et les pages `/blog/`, validé explicitement par le fondateur le 29 août 2026.
- **Blog SEO** : 4 pages statiques publiées dans `/blog/` sur un calendrier étalé (30 août, 2, 5 et 8 septembre 2026), voir `SEO_PAGES_BRIEF.md` et `COMMUNITY_CALENDAR.md`.

---

## 7. Garde-fous stratégiques (à ne jamais perdre de vue)

- **Aucune publication automatique** du post initial ou du lien produit sur Reddit/X/Threads — reste un geste manuel, pour préserver l'authenticité (le vrai avantage face à un concurrent financé par VC) et éviter le shadowban.
- **Toute automatisation de réponse aux commentaires passe par une validation humaine** (clic Telegram) jusqu'au seuil de traction fixé.
- **Ne jamais reproduire le pattern "lien en premier commentaire immédiat après le post"** — identifié comme un signal de spam en 2026.
- **Le temps est la ressource rare, pas l'argent** — ne pas laisser l'outillage (n8n, automatisation) retarder la publication effective des pitchs.
- **Rester sceptique sur les rapports de recherche IA** (Deep Research, etc.) — vérifier les affirmations sur les concurrents avant de les répéter, comme cela a déjà été fait une fois pour Unkey.

---

## 8. Questions ouvertes (à trancher avec le candidat)

1. **Seuil exact d'inscriptions/réactions avant de basculer vers le code du MVP — TRANCHÉ le 29 août 2026, trajectoire de validation par l'usage :**
   * *Point de données empirique (29 août 2026, r/digital_ocean) :* 1k+ vues en 48h (#1 du sub, 50% audience US/UK/CA) mais ratio d'upvotes faible (40%, 0 net) et 3 commentaires. Ce pattern confirme que le titre capte l'attention, mais suscite de la friction/scepticisme sur la monétisation fermée d'un outil d'infra basique.
   * *Signal produit clé :* Demande explicite non sollicitée d'un développeur (Mr-Shortman) pour une distribution open source / self-hosted. À intégrer dans la réflexion de packaging (lib open-core / source-available + dashboard payant).
   * **Axe 1 — Pas de pré-vente Stripe tant que le signal qualitatif est faible.** Aucun prix affiché sur `index.html` pour l'instant. Le signal actuel (0 upvote net) ne justifie pas d'encaisser de l'argent réel sur un produit non livré — risque réputationnel jugé disproportionné face à un public dev qui ne pardonne pas le vaporware.
   * **Axe 2 — Construction du cœur minimal réel (pas un faux Wizard-of-Oz).** FastAPI + PostgreSQL pour le hash/scope/revoke, SDK middleware minimal (Node ou Python selon la demande observée). Rien au-delà : pas de dashboard équipe, pas d'analytics avancées, pas d'app mobile d'admin. Délai indicatif large, pas de deadline serrée artificielle.
   * **Axe 3 — Validation par rétention d'usage à 7 jours, pas par les inscriptions.** Objectif : 3 développeurs tiers qui installent le middleware gratuit dans un projet de staging/test réel. Engagement de support rapide de notre côté pendant cette fenêtre — un bug non résolu invalide la mesure, indépendamment de la qualité du produit. Validation acquise si le code est toujours actif chez au moins 3 d'entre eux après 7 jours.
   * **Axe 4 — Le déclencheur Stripe devient une conséquence, pas une hypothèse.** LTD privée (prix à confirmer, ordre de grandeur 49$) proposée uniquement quand un bêta-testeur demande explicitement à passer en production. L'argent suit l'usage réel, pas l'inverse.
   * *Conséquence sur le discours public :* dès que le code du cœur existe, les réponses publiques ("still validating demand before writing the code") doivent évoluer vers "building the core now, testing with a few devs" — ne pas laisser deux discours contradictoires coexister sur Reddit/X.
2. Date J0 de lancement de la campagne de publication (validée au 28 août 2026).
3. Méthode de logging des interactions communautaires (Google Sheet vs static data n8n vs volume Docker monté).
4. Faut-il câbler un webhook Formspree → n8n (nécessite un tunnel Cloudflare stable) ou rester sur les notifications email Formspree pour l'instant.
