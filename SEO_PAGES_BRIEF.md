# Brief d'exécution — 4 pages SEO keyed

*Ce document cadre la construction technique et éditoriale des 4 pages SEO validées.*

---

## 0. Rappel de rôle

Antigravity exécute, il ne décide pas du positionnement. Les 4 sujets ci-dessous sont validés. Le texte final de chaque page reste soumis à relecture humaine avant merge/déploiement. Aucune page ne doit contenir de lien de paiement direct ni de pricing ferme tant que la stratégie LTD (PRD §3.3) n'est pas confirmée — mention du concept "one-time payment" autorisée, chiffre précis interdit sauf s'il est déjà public sur `index.html`.

---

## 1. Les 4 pages à construire

| # | Sujet | Intention de recherche ciblée | Angle |
|---|---|---|---|
| 1 | `keyed vs Unkey` | "unkey alternative", "unkey pricing", "unkey vs" | Comparatif honnête, LTD vs abonnement, simplicité vs plateforme |
| 2 | `How to hash API keys (Node.js & Python)` | "hash api key node", "api key hashing best practice fastapi" | Tutoriel technique réel, indépendant de keyed jusqu'à la conclusion |
| 3 | `API key rate limiting without a gateway` | "rate limit api key without proxy", "sliding window rate limit middleware" | Reprend l'angle du Post B, format long |
| 4 | `Scoped, revocable API keys for AI agents` | "ai agent api key security", "scoped api key llm agent" | Reprend l'angle PRD §2.5 (narratif agents IA comme copywriting) |

---

## 2. Workflow obligatoire par page

1. **Cadrage avec `/prompt-engineering`** : Structure H1/H2, ancrage aux faits du repo, zéro invention sur Unkey, sortie en Markdown brut. Fichiers stockés dans `seo/prompts/`.
2. **Génération du contenu** : Code syntaxiquement valide et testable.
3. **Passage obligatoire par `/humanizer`** : 0 emoji, 0 tiret cadratin, 0 mot de vocabulaire IA, 0 liste corporative avec titres en gras, rythme varié.
4. **Auto-vérification avant soumission** : Checklist validée.

---

## 3. Contraintes techniques

- Pages statiques hébergées sur GitHub Pages.
- Emplacement suggéré : `/blog/keyed-vs-unkey.html`, `/blog/hash-api-keys-node-python.html`, `/blog/api-key-rate-limiting-without-gateway.html`, `/blog/scoped-api-keys-ai-agents.html`.
- Lien retour vers `index.html` ou `waitlist.html`.
