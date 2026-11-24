# Execution strategy (draft for approval)

Owner: vrastogi1235 | Target: AI PM roles at Razorpay, PayPal, Pine Labs | Preference: roles outside India

## Positioning

The portfolio should read as the work of a product manager who can build, not an engineer who writes PRDs on the side. Every project opens with the problem, the evidence, the metric and the trade-offs. The working demo comes second and proves the thinking was real. Docs are written in first person and lead with what you built: "I built", "I chose", "I cut".

## Market lean

- About 60% global payments problems: disputes, fraud, cross-border, checkout failures, merchant lending. These map to PayPal and to the global roles you prefer.
- About 40% India-specific: UPI failure handling, merchant-acquirer workflows, RBI-shaped constraints. These map to Razorpay and Pine Labs and show you can handle a regulated market.
- Every India project gets a short "how this generalises globally" section. Every global project gets a note on where India differs.

## Rhythm

- Daily: one small, finished deliverable. A micro-tool, a one-page analysis, a teardown, a metrics tree, a notebook. Small but real.
- Weekly: one flagship project, sometimes two. Built Thursday to Sunday, researched Monday to Wednesday through the micro-projects.
- Monday to Wednesday work feeds the flagship, so the research, teardown and PRD exist before any build starts.

## Flagships (candidates, each gets a research check before approval)

1. Payment failure and smart retry advisor (week 1).
2. Dispute and chargeback evidence triage copilot (week 2).
3. Merchant cash-flow underwriting signals (week 3).
4. Payments support agent with an evaluation harness (week 4).

## Data and safety rules

- All data is synthetic and labelled synthetic in every README. Generators are in the repo.
- No employer information, no real customer data, no keys, no claims of users or revenue.
- Facts about companies come from public sources and carry links. Estimates and assumptions are marked.
- You have a Claude subscription but no API key. Any LLM feature ships with an offline mode (rules or pre-recorded sample outputs, clearly labelled) so the demo runs for anyone. A key is read from an environment variable and never committed.

## Stack

- Python 3.12, FastAPI, pandas, scikit-learn or LightGBM, DuckDB or SQLite.
- Demo UI: Streamlit for fast demos, React with Vite for flagships where the interface matters.
- Free hosting: GitHub Pages and Streamlit Community Cloud. No paid infrastructure without your approval.
- Tests: pytest, one small meaningful test per logic branch.

## Repositories

- `vrastogi1235/vrastogi1235`: profile README.
- `vrastogi1235/fintech-ai-product-portfolio`: PRDs, teardowns, research, micro-projects, calendar, status, skills registry.
- One repo per flagship, linked from the portfolio and profile.

## Publishing gates

- Nothing public until you approve this plan.
- After approval, I publish inside these boundaries: the repos above, content passing the safety rules and a review pass. I stop and ask for anything outside them.

## Quality bar

Each project is scored 1 to 10 on problem relevance, product thinking, technical implementation, user experience, documentation, originality, industry relevance and recruiter appeal. Target is 8 or higher in each. Scores come with reasons in the repo's review notes, and I won't round them up.

## Skills plan

- Humanizer (`humanizer:humanizer`, installed): every written deliverable.
- Ponytail: coding, once you install it. Keeps code small.
- Product Manager Toolkit (`product-manager-toolkit`, installed): PRDs, RICE prioritisation.
- Superpowers (installed): test-driven development, debugging, verification before completion.
- Skill Finder: used for discovery only. I read each candidate skill before installing and record it in `SKILLS_USED.md`.
