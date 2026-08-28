# Posts de distribution keyed (28 aout 2026)

> Regle: AUCUN lien dans le post initial ni en premier commentaire.
> Le lien apparait uniquement si quelqu'un le demande en commentaire, ou dans la bio du compte.
> "I'm building this" dans chaque post.

---

## Calendrier de publication

| Jour   | Plateforme           | Angle                          |
|--------|----------------------|--------------------------------|
| J0     | r/SideProject        | A. Fatigue SaaS / LTD         |
| J0     | Threads              | D. Build in public             |
| J+1    | X/Twitter (Thread)   | D. Build in public             |
| J+3-4  | r/webdev ou r/node   | B. Anti-bloat / 3 lignes       |
| J+7-8  | r/LocalLLaMA         | C. Securite agents IA          |

Subreddits par friction croissante (compte neuf) :
r/SideProject > r/AlphaAndBetaUsers > r/IndieBiz > r/IMadeThis > r/SomebodyMakeThis

---

## Post A (r/SideProject ou r/AlphaAndBetaUsers)

**Titre :**
Tired of paying monthly just to manage API keys, so I'm testing a one-time payment alternative

**Corps :**
Every time I ship a project, "add API key auth" turns into another monthly subscription. Vault, Unkey, whatever, they all moved to seat pricing and enterprise contracts. Fine for funded teams, but if you're solo and your project makes under 200 bucks a month, that recurring cost is hard to justify.

I'm building this myself (full disclosure). It does bcrypt hashing locally, rate limiting, instant revocation. About 3 lines of middleware. No gateway, no DNS changes, no proxy. You buy it once.

Haven't written the backend yet. I'm checking if the pitch makes sense before I build anything. If you've dealt with this problem, what would you actually want? And if you'd stick with what you have now, I want to hear that too.

---

## Post B (r/webdev ou r/node, J+3-4)

**Titre :**
Why did API key management get this bloated?

**Corps :**
For most side projects you don't need a distributed proxy, DNS hijacking or an Envoy sidecar just to check an x-api-key header. What you actually need is pretty boring:

1. Hash the incoming key against your DB (takes about 3ms)
2. Enforce rate limits with a sliding window
3. Revoke access instantly if a key leaks

That's it. But the tools on the market are built for way more than that, and priced accordingly.

I'm working on a local library (Node/TS and Python) that handles these three things in a few lines of middleware without sending traffic through someone else's servers. It's my project, full disclosure.

How do you handle API key validation today? Do you roll your own hash check every time, or do you pay for an external service?

---

## Post C (r/LocalLLaMA, J+7-8)

**Titre :**
Stop giving your autonomous AI agents root API keys with unlimited lifespans

**Corps :**
If an agent loops or gets prompt injected, a hardcoded master key can drain your quota in minutes. I've seen it happen with AutoGPT setups and LangChain scripts that people leave running overnight.

You don't need enterprise IAM for a personal agent workflow. What you need is simpler:

- Generate scoped keys that expire on their own
- Set hard rate limits per minute
- Kill a single agent's token without rotating your root secret

I'm building a local utility that does exactly this (my own project, putting it out there). Curious what your setup looks like when you give API keys to LLMs. Do you just yolo the master key or do you have some kind of wrapper?

---

## Thread X/Twitter (J+1)

1/ Unkey raised 4.5M to build the enterprise version of API key management.

That's great for them. But it means solo devs are no longer who they're building for.

2/ I don't want another 30 bucks a month just to check an API key header on a project that barely covers its own hosting.

3/ So I'm building keyed.
Local hashing, about 3ms, no proxy.
Rate limiting and instant revocation.
A few lines of middleware in Node or Python.
One time payment.

4/ Nothing is built yet. I'm validating the idea first.

If you manage API keys on side projects, what's the part that actually annoys you?

#BuildInPublic #IndieHackers

> Lien uniquement en reponse si quelqu'un demande, jamais dans le thread.

---

## Post Threads (J0, avec le premier post Reddit)

Unkey just raised 4.5M. Good for them, but solo devs aren't their market anymore.

I'm building the opposite: a simple API key tool, a few lines of code, you pay once and that's it. No monthly invoice.

Still figuring out if this is worth building before I write any backend. If you've ever rolled your own API key auth, what was the part that sucked?

**Reponse de suivi (poster soi-meme 60 a 90 secondes apres) :**
For me it was never the hashing. It's the rate limiting and clean revocation without bolting on a full gateway. That's the whole scope of what I'm building.

---

## Reponse type si quelqu'un demande un lien

"Sure, here's the landing page: https://kreesten-hsh.github.io/keyed/ (lifetime pricing locked at launch for early signups). Thanks for asking."
