### 1. Market reality (April 2025 snapshot)
* **Soft hiring + anxious talent pool.** U‑S unemployment sits at **≈ 4.2 %** but tech and business‑services layoffs remain elevated (1 in 5 layoffs in 2024–25 came from tech) citeturn0search6turn0search0  
* **International students squeezed.** FY‑25 H‑1B cap is already hit; new visa rules take effect Jan 17 2025 and hundreds of study visas were summarily cancelled last week citeturn0search1turn0news30  
* **“Spray‑and‑pray” behaviour is normalising.** A mini‑wave of AI “auto‑apply” tools (JobCopilot, BulkApply, Careerflow, etc.) shows clear demand but no single breakout winner citeturn0search2turn0search5  

👉 **Opportunity:** a sharper, psychologically sticky platform that (1) reduces application friction further, (2) de‑risks visa‑related uncertainty, and (3) monetises panic with fast‑acting, credibility‑building features.

---

### 2. Value proposition & positioning
> **JobBright — “From search to shortlist to signed offer, in weeks not months.”**

| Problem felt by user | Psychological lever | Product response |
|----------------------|---------------------|------------------|
| “I’m lost; I apply everywhere.” | **Illusion of progress & clarity** | Visual *Application Pipeline* dashboard with percentage‑to‑offer meter + daily “Next best move” nudge. |
| “I can’t tailor 100 resumes.” | **Ease + competence proof** | GPT‑4o powered *1‑Click Tailor* (uploads JD → rewrites résumé + cover letter). |
| “I fear missing a visa window.” | **Risk removal / safety** | *VisaPulse*: live feed of H‑1B/L‑1 news, personalised reminders, lawyer marketplace. |
| “Everyone else is ahead of me.” | **Social proof / FOMO** | Real‑time ticker “21 users scheduled interviews in the last 24 h”. |
| “Money is tight.” | **Freemium, sunk‑cost fallacy** | Free tier (50 apps/mo); upgrade to Pro for “Unlimited Auto‑Apply + Interview GPT”. Cancellation retains read‑only data to trigger comeback. |

Tag‑lines to A/B‑test on landing page
* “**Stop guessing. Start interviewing.**”
* “**50 tailored applications in the time it takes to make coffee.**”
* “**Visa‑safe job search, powered by AI.**”

---

### 3. Feature map

| Tier | Must‑have (week 1‑3) | Differentiators (week 4‑8) | Revenue accelerators (week 6‑12) |
|------|---------------------|---------------------------|----------------------------------|
| Free | Email / Google sign‑in, profile import (LinkedIn PDF), job‑board scraper (Indeed, Greenhouse, Lever APIs), 50 auto‑applies/mo, Application Pipeline dashboard | Daily streak gamification, 7‑day history of VisaPulse, limited GPT resume edits | n/a |
| Pro $29/mo | Unlimited auto‑apply (queueing via background workers), GPT‑4o resume & cover letter rewriting, Interview Flash‑Cards (LLM Q&A), priority support chat bot | *Assisted Application* (fills embedded ATS forms via browser extension), VisaPulse in‑app lawyer chat, mock interview scheduling, Slack alerts | Referral credits (one free month per paying invite, viral loop) |
| Elite $99/mo | Personal success coach (human or GPT‑agent blend), guaranteed 24‑hour résumé review, custom domain email alias for cold outreach | Auto‑apply throttling to pass ATS spam heuristics, “Warm intro finder” (graph search across public angel‑lists & alumni data) | Annual billing default + 10 % discount, cohort‑based “Elite” webinars |

---

### 4. System architecture (lean‑monolith first)

```
 ┌─────────────────────┐
 │ React/Next.js SPA   │
 └─────────┬───────────┘
           │REST+WS
 ┌─────────▼───────────┐
 │ FastAPI   (Python)  │   Postgres        Stripe
 │  ├─ auth            │<─────────┐    ┌─────────┐
 │  ├─ jobs CRUD       │          │    │ Payments│
 │  ├─ match engine    │          │    └─────────┘
 │  ├─ visa alerts     │          │
 │  └─ subscription    │          │
 └─────────┬───────────┘          │
           │ Celery/RQ            │ Redis (queues, cache)
           ▼                      │
   ┌───────────────────┐          │
   │ Scraper workers   │──────────┘
   │  (Playwright)     │
   └───────────────────┘
           │
           ▼
   Vector DB (Qdrant)  ← résumé & JD embeddings
```

* **Deployment:** Docker‑Compose locally → Render or AWS ECS Fargate.  
* **Observability:** Prometheus + Grafana; Sentry for errors.  
* **Security / compliance:** SOC‑2 controls up‑front (role‑based auth, audit logs); GDPR & CCPA toggles.  

---

### 5. Repo / file‑layout (top‑level)

```
jobbright/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI app factory
│   │   ├── core/config.py
│   │   ├── api/
│   │   │   ├── auth.py
│   │   │   ├── jobs.py
│   │   │   ├── users.py
│   │   │   ├── subs.py
│   │   │   └── visa.py
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── job.py
│   │   │   ├── resume.py
│   │   │   └── payment.py
│   │   ├── services/
│   │   │   ├── scraping.py   # site‑specific adapters
│   │   │   ├── matching.py   # embedding & ranking
│   │   │   ├── autosubmit.py # browser‑automation
│   │   │   └── emailer.py
│   │   ├── workers/tasks.py
│   │   └── tests/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── index.tsx
│   │   │   ├── dashboard.tsx
│   │   │   └── pricing.tsx
│   │   ├── components/
│   │   │   ├── JobCard.tsx
│   │   │   ├── ProgressMeter.tsx
│   │   │   └── VisaPulse.tsx
│   │   ├── hooks/
│   │   └── styles/global.css
│   ├── Dockerfile
│   └── vite.config.ts
├── infra/
│   ├── docker‑compose.yml
│   └── terraform/
├── scripts/seed_db.py
└── README.md
```

Key code snippets to implement first
```python
# backend/app/services/matching.py
from sentence_transformers import SentenceTransformer
import qdrant_client, numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")
db = qdrant_client.QdrantClient("localhost", port=6333)

def rank_jobs(resume_text: str, jobs: list[dict]) -> list[dict]:
    vec = model.encode(resume_text)
    job_vecs = np.vstack([j["embedding"] for j in jobs])
    scores = job_vecs @ vec / (np.linalg.norm(job_vecs, axis=1)*np.linalg.norm(vec))
    return sorted(zip(jobs, scores), key=lambda x: x[1], reverse=True)
```

---

### 6. 30‑day execution roadmap

| Day | Deliverable | Owner | Metric |
|-----|-------------|-------|--------|
| 1–2 | Domain, logo, tagline, wait‑list page (Vercel) | Design | 1,000 sign‑ups |
| 3–7 | 🎯 **MVP**: auth, profile import, 3 job‑board scrapers, Application Pipeline | Eng | 50 beta users test |
| 8–10| Stripe + paywall (launch Pro pre‑orders with 40 % discount) | Growth | $2k ARR presold |
| 11–14| 1‑Click Tailor (GPT‑4o, rate‑limited) | Eng | 85 % user adoption |
| 15  | Product Hunt “Coming Soon” teaser + LinkedIn career‑coach micro‑influencers DM campaign | Growth | 5k wait‑list |
| 16–21| Browser extension for ATS auto‑fill + VisaPulse MVP | Eng | avg. 8 min saved/app |
| 22–24| Referral loop (double credits) + social proof widget | Growth | R₀ ≥ 1.3 |
| 25  | Launch day (PH, HackerNews, r/cscareerquestions AMA) | Founders | 500 paid subs |
| 26–30| Collect NPS, ship bug fixes, prep feature/price ramps | All | NPS > 45 |

---

### 7. Growth & persuasion playbook
* **AIDA funnel copy** on landing page; scroll‑triggered testimonials from international grads.  
* **Loss‑aversion timer**: “VisaPulse free tier ends in 4 d 12 h”.  
* **Mini‑milestones**: confetti when 10 applications submitted; badge share‑able on LinkedIn.  
* **Founder “build‑in‑public” posts** twice weekly → humanises brand, builds trust.  
* **Affiliate rev‑share (20 %)** with university career centres and TikTok job influencers.  
* **Risk‑reversal offer:** “30‑day full refund if you don’t land an interview” → requires proof of 100 auto‑applies to avoid abuse.

---

### 8. Compliance, risk & ethics
1. **Terms of Service checks** for every scraped board; pivot to official APIs if C&D received.  
2. **ATS throttling** to avoid bot‑detection; randomised intervals, human‑like keystrokes.  
3. **GDPR/CCPA** data‑delete button; encrypted PII at rest.  
4. **Honest marketing:** promises revolve around *speed* and *efficiency*, **not** job guarantees.  
5. **Visa advice = curated lawyers**, not legal advice from the platform.

---

### 9. Next steps for you (today)
* Register `jobbright.ai`, create wait‑list page on Vercel (use shadcn/ui for quick polish).  
* Spin up repo scaffold above (`cookiecutter-fastapi-postgres` + `create-t3-app`).  
* Book 5 international‑student focus calls; capture language & pain‑points for copywriting.  
* Draft privacy policy & ToS (use OneTrust template, add AI‑disclosure section).  

Execute the sprint, track daily active users → iterate. If retention > 30 % on Day 7, pour fuel (ads, influencers); if not, tighten onboarding copy and job matches first.   

**Build fast, stay ethical, and monetise the true value—time saved and stress reduced.**