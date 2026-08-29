# Distribution and Community Strategy (14-Day Hybrid Plan)

This document establishes the hybrid distribution strategy for keyed and the founder's personal brand. It combines spaced promotional posts for keyed with frequent community-building posts to connect with solo founders and indie hackers.

---

## 1. Operating Rules and Guardrails

1. Zero automated publishing. Every post and reply requires explicit human review before posting.
2. Zero links in initial Reddit posts or initial automated comments. Links are shared on X and Threads only in replies when requested, or placed in the profile bio.
3. Maximum one post per platform per day.
4. Never post on all three platforms (Reddit, X, Threads) on the same calendar day.
5. Promotional posts for keyed strictly follow the existing spaced schedule (Thread on X at J+1, r/webdev or r/node at J+3/4, r/LocalLLaMA at J+7/8).
6. Community posts are daily or quasi-daily on X and Threads, but strictly weekly on a fixed day on Reddit.
7. Never expose secrets, credentials, or private API keys in examples or screenshots.
8. Writing standards:
   - Zero emojis.
   - Zero em dashes. Use commas or split sentences.
   - Zero AI vocabulary (crucial, pivotal, showcase, delve, landscape, tapestry, foster, enhance).
   - Zero corporate bullet lists with bold headers followed by colons.
   - Varied sentence structure with a direct, practical developer voice.
   - Every post ends with a clear, specific prompt or question.

---

## 2. 14-Day Hybrid Calendar (J0 to J+14)

| Day | Platform | Post Type | Tone / Angle | Promotional Tie-in |
|---|---|---|---|---|
| J0 (Fri 28/08) | Reddit + Threads | Promo keyed | Serious (SaaS fatigue, LTD) | Completed (r/alphaandbetausers, r/indiebiz, Threads) |
| J+1 (Sat 29/08) | X | Promo keyed (Thread) | Serious (Build in public) | J+1 Official Promo (4-tweet thread) |
| J+2 (Sun 30/08) | Threads | Community | Light (Solo dev reality) | None |
| J+3 (Mon 31/08) | Reddit + X | Promo Reddit + Com X | Serious / Technical debate | J+3 Official Promo (r/webdev or r/node) |
| J+4 (Tue 01/09) | Threads | Community | Light (Stack dilemma) | None |
| J+5 (Wed 02/09) | X | Community | Serious (Solo tools curation) | None |
| J+6 (Thu 03/09) | Reddit + Threads | Com Reddit + Com Threads | Neutral / Peer support | Weekly Reddit check-in (r/SideProject) |
| J+7 (Fri 04/09) | Reddit + X | Promo Reddit + Com X | Serious (AI agent key security) | J+7 Official Promo (r/LocalLLaMA) |
| J+8 (Sat 05/09) | Threads | Community | Humor (Time spent on minor details) | None |
| J+9 (Sun 06/09) | X | Community | Serious (Validation and pricing feedback) | None |
| J+10 (Mon 07/09) | Threads | Community | Light (Solo dev vs bloated agencies) | None |
| J+11 (Tue 08/09) | X | Community | Technical debate (Boring tech vs new frameworks) | None |
| J+12 (Wed 09/09) | Threads | Community | Serious (Real process, headline copy fix) | None |
| J+13 (Thu 10/09) | Reddit + X | Com Reddit + Com X | Neutral / Peer showcase | Weekly Reddit check-in (r/SideProject) |
| J+14 (Fri 11/09) | Threads | Community | Retrospective (Two weeks of validation learnings) | None |

---

## 3. Post Bank Ready for Validation

### Post 1: Open Question (Technical Friction)
* Platform: X or Threads (Day J+3 or J+9)
* Format: Open question inviting experience sharing
* Context: Developers enjoy discussing real implementation friction. It creates natural conversation and invites peers to drop their project name in replies.

```text
Solo devs, what is one feature in your current project that took three times longer to build than you planned?

For me it is always auth edge cases and token cleanup.

Drop your project and the feature that broke your estimate.
```

---

### Post 2: Choice / Dilemma (Self-deprecating Developer Habit)
* Platform: Threads or X (Day J+4)
* Format: Multiple choice dilemma
* Context: Low friction format requiring only a one-letter or one-sentence answer, driving high initial engagement.

```text
When you build a side project, which trap do you fall into first?

A) Spending three days picking UI components and color tokens
B) Over engineering the database schema for users you do not have yet
C) Writing docs before writing any code

I am guilty of B almost every single time. Where are you stuck today?
```

---

### Post 3: Peer Curation (Creator Hub / Ecosystem Support)
* Platform: X or Threads (Day J+5)
* Format: Curation of independent tools
* Context: Demonstrates genuine interest in the indie developer ecosystem and brings builders into the thread without any pitch.

```text
Three solo built tools I checked out this week that do one thing well:

A sqlite backup helper that runs as a single binary without docker.
A tiny terminal pomodoro timer that logs directly to a text file.
A dead simple webhook debugger with zero sign up required.

Building a focused micro tool on your own? Reply with what it does.
```

---

### Post 4: Weekly Reddit Community Check-in
* Platform: Reddit (r/SideProject or r/IndieBiz, Day J+6 / J+13)
* Format: Recurring Thursday thread
* Context: A fixed weekly schedule respects Reddit anti-spam norms and positions the account as a helpful community member.

```text
Weekly check-in: what are you shipping this week, solo founders?

Drop your project, your stack, and the one problem you are trying to solve right now.

No essays, just practical stuff. I will check every reply and give feedback.
```

---

### Post 5: Real Process and Learning (Authentic Technical Bug)
* Platform: X or Threads (Day J+12)
* Format: Factual incident (real bug encountered, fix applied, developer takeaway)
* Context: True build-in-public incident from building the keyed landing page, creating authentic developer relatability without fabricated metrics.

```text
Shipped a static landing page for my project yesterday and tested the waitlist form live.

Forgot that without intercepting the submit event with preventDefault, the form does a native POST and dumps the user onto an external confirmation screen instead of handling the response with fetch.

Fixed the handler in two lines of vanilla JavaScript.

What is the dumbest frontend bug you pushed to production recently?
```

---

### Post 6: Solo Developer Reality (Dry Humor)
* Platform: Threads (Day J+8)
* Format: Observation / relatability
* Context: Casual weekend content that generates spontaneous replies and human connection.

```text
The hardest part of being a solo developer is not the code.

It is sitting alone in front of a terminal at midnight deciding whether you should fix a minor CSS alignment bug or finally go to sleep.

The alignment bug always wins.

What is the most pointless detail you spent hours fixing this week?
```

---

## 4. Daily Operational Routine (Max 30 Minutes)

1. Morning (5 minutes): Publish the scheduled post (Track A promo or Track B community).
2. Midday (10 minutes): Review and answer incoming comments with direct technical responses.
3. Evening (15 minutes): Final pass on replies and leave 3 to 4 meaningful comments on other solo founders' posts.
