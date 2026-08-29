# DM Outreach — Recrutement des 3 bêta-testeurs (Axe 3, PRD §8.1)

*Zéro budget, zéro automatisation. Chaque envoi est un geste manuel, un message par personne, adapté au contexte réel qu'elle a exposé publiquement.*

---

## Grille de Qualification Stricte (3 Filtres Éliminatoires)

Avant d'envisager d'écrire à un développeur, l'issue ou le thread doit valider **les 3 conditions cumulatives** :

1. **Émetteur de clés vers des tiers (Multi-tenant) :** Le projet doit être une API, un SaaS ou un service qui émet des clés d'accès à des utilisateurs, clients ou agents externes. Exclure d'office les projets mono-utilisateurs (ex: un chatbot personnel ou un wrapper local) et les coffres-forts de clés sortantes (.env).
2. **Auteur humain & friction vivante :** L'auteur doit être un être humain (jamais un `bot` ou une sous-tâche générée par un pipeline CI) exprimant une réelle incertitude ou douleur sur l'implémentation (rotation, persistance du hash, rate limiting).
3. **Compatibilité technique :** Ne jamais contacter un développeur dont la contrainte affichée est "zéro dépendance" ou qui a déjà figé son implémentation en dur.

## Règle absolue

Ne jamais écrire "teste mon SaaS" ou "check out my product". Le message doit répondre à un problème déjà exprimé, pas ouvrir une vente.

---

## Template GitHub (réponse à une issue ou un commentaire)

```
Hey, saw your issue about [problème précis, ex: rotating API keys without redeploying].
I've been building a small FastAPI/Node middleware that handles hashing, scoping and instant revocation without a cloud proxy — exactly the kind of thing that would fix what you're describing.

It's not a product yet, just working code. Happy to jump on a 15min call and help you wire it into your staging setup for free, no strings attached. Would that be useful, or is this already solved on your end?
```

## Template Reddit (DM après un thread où la personne a exposé un problème)

```
Hey, saw your post about [problème précis]. I ran into the same thing building keyed, a middleware for hashing/scoping/revoking API keys locally, no external proxy.

Still early, no pricing, nothing to sell. If you want, I can help you drop it into a test project so you can see if it actually solves what you're dealing with. Takes about 15 minutes on a call, or I can just send the snippet if you'd rather try it yourself.
```

## Variante courte (si la personne a juste liké/commenté brièvement, pas un post détaillé)

```
Saw your comment on [contexte]. I'm building a small middleware for API key hashing/scoping/revocation, still early and free to try. If the [problème] you mentioned is still a pain point, happy to help you test it in a staging project, no commitment.
```

---

## Après le "oui"

1. Proposer 2-3 créneaux pour un appel de 15 minutes (ou juste envoyer le snippet directement s'ils préfèrent, ne pas forcer l'appel).
2. Installer avec eux ou les guider, jamais leur envoyer un lien de doc et disparaître.
3. Noter la date d'installation. J+7, un message court, pas un questionnaire :
   ```
   Hey, quick check-in — is [nom du projet] still using the middleware, or did you end up ripping it out? No worries either way, just trying to see if this actually holds up in real use.
   ```
4. Consigner le résultat (toujours actif / retiré / jamais vraiment testé) dans `PRD.md` §8.1, pas ailleurs, pour garder une seule source de vérité.

---

## Ce qu'on ne fait pas

- Pas de message groupé, pas de copier-coller identique à plusieurs personnes le même jour sans adapter le contexte.
- Pas de relance après un silence de plus de 48h sans réponse — un "non" silencieux reste un "non".
- Pas de mention de prix ou de LTD à ce stade, même si la personne demande "et ça coûte combien ?" — répondre honnêtement que rien n'est fixé, que c'est encore en phase de test gratuit.
