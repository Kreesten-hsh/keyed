# Posts de distribution keyed — Version finale révisée (27 août 2026)

> Correctif appliqué : AUCUN lien dans le post initial ni en premier commentaire auto. Le lien
> n'apparaît que si demandé par un commentateur, ou dans la bio/profil du compte.
> Divulgation systématique ("I'm building this") dans chaque post.

---

## Calendrier de publication

| Jour   | Plateforme           | Angle                          |
|--------|----------------------|--------------------------------|
| J0     | r/SideProject        | A — Fatigue SaaS / LTD        |
| J0     | Threads              | D — Build-in-Public authentique|
| J+1    | X/Twitter (Thread)   | D — Build-in-Public            |
| J+3-4  | r/webdev ou r/node   | B — Anti-Bloat / 3 lignes     |
| J+7-8  | r/LocalLLaMA         | C — Sécurité agents IA        |

Priorité de subreddits à faible friction (compte pas encore chauffé) :
r/SideProject > r/AlphaAndBetaUsers > r/IndieBiz > r/IMadeThis > r/SomebodyMakeThis

---

## Post A — r/SideProject ou r/AlphaAndBetaUsers

**Titre :**
I got tired of paying $25–50/mo just to manage API keys, so I'm testing a one-time-payment alternative

**Corps :**
Every time I ship a new project, "add API key auth" quietly becomes another recurring SaaS subscription. The established players in this space are moving upmarket — full gateways, seat-based pricing, enterprise contracts. Makes sense for their business model, but it prices out solo devs who just need hash / verify / rate-limit / revoke and nothing else.

Full disclosure: I'm building this. keyed does bcrypt hashing locally, rate limiting, instant revocation, ~3 lines of middleware to integrate. No gateway to route through, no DNS changes. Sold once as a lifetime deal instead of a recurring line item.

Nothing's built yet — I'm validating the pitch before writing a single line of backend. If this is a pain you've actually hit: what would you expect from something like this, or why would you stick with what you're using now? Genuinely want the pushback too.

---

## Post B — r/webdev ou r/node (J+3-4)

**Titre :**
Why did API key management get this bloated?

**Corps :**
Most side projects and micro-SaaS don't need a distributed proxy gateway, DNS hijacking, or Envoy sidecars just to check an x-api-key header. You usually just need:

1. Hash incoming key against your database/cache (<3ms)
2. Enforce sliding window rate-limits
3. Revoke instant access if compromised

I'm working on (full disclosure, my own project) a zero-overhead local library (Node/TS & Python) that does this in 3 lines of middleware without proxying traffic through 3rd-party servers.

Curious how you handle API key validation today — do you roll your own bcrypt hash table every time, or pay for external infra?

---

## Post C — r/LocalLLaMA (J+7-8)

**Titre :**
Stop giving your autonomous AI agents root API keys with unlimited lifespans

**Corps :**
If an autonomous agent (AutoGPT, LangChain, local LLM scripts) loops out of control or gets prompt-injected, hardcoded master keys get leaked or drain quotas in minutes.

We don't need heavyweight enterprise IAM platforms for small agent workflows. We just need:
- Programmatic issuance of scoped, ephemeral keys
- Hard per-minute usage rate limits
- A kill switch to revoke an agent token without rotating your root secrets

Building a dead-simple, local utility for this (disclosure: it's my project). What's your current workflow for scoping keys given to LLMs?

---

## Thread X/Twitter (J+1)

1/ Unkey just raised $4.5M to build the enterprise AWS of API gateways.

That's great for VC-backed teams. For solo devs, it creates a vacuum below them.

2/ We don't want another $30/mo invoice just to check an API key header on a side project that makes $0-100 MRR.

3/ So I'm building keyed:
- 3 lines of middleware (Node/Python)
- Local hashing, <3ms, zero proxy latency
- Rate-limiting + instant revocation
- One-time payment, not a subscription

4/ Nothing's built yet. Validating the pitch before writing backend code.

If you issue API keys on side projects: what's your actual pain point today?

#BuildInPublic #IndieHackers

> Lien uniquement en réponse si demandé, jamais dans le thread.

---

## Post Threads (J0, avec le premier post Reddit)

Unkey just raised $4.5M. Cool for them, but it means solo devs are no longer their target market.

I'm building the opposite: a dead-simple API key tool, 3 lines of code, one-time payment instead of another $30/mo subscription.

Still validating before I write any backend code. If you've ever built API key auth yourself — what was the annoying part?

**Réponse de suivi à poster soi-même ~60-90s après :**
For context: the annoying part for me was never the hashing itself, it's rate-limiting + clean revocation without adding a whole gateway. That's the actual scope of what I'm building.

---

## Réponse type si quelqu'un demande un lien

"Sure — landing page and waitlist are here: https://kreesten-hsh.github.io/keyed/ (LTD pricing locked at launch for early signups). Appreciate the interest."
