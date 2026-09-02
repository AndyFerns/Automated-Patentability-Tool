# 📚 IPR Audit & Patentability Scoring Tool — Documentation

Welcome! This is the full documentation set for the **IPR Audit & Patentability
Scoring Tool** — a lightweight, modular system for institutional IP auditing,
patent-similarity analysis, and organization-level IPR scoring.

If you just want to get it running, jump straight to
[Getting Started](01-getting-started.md). If you want to understand how the
whole thing hangs together, read on.

---

## What this tool does (in one paragraph)

You feed it intellectual-property **disclosures** (patents, copyrights,
trademarks, and so on). For each patent it runs a **similarity check** against a
reference dataset and assigns a **risk level**. It then rolls everything up per
organization into a single **IPR score** and an **innovation tier**, and can
produce a structured **audit report** describing exactly how it got there. A
Streamlit dashboard wraps the whole thing in a guided, five-step pipeline.

---

## The documentation map

| Doc | What's inside | Read it when… |
|-----|---------------|---------------|
| **[01 · Getting Started](01-getting-started.md)** | Prerequisites, install, build, and run — local, Windows one-click, and Docker. Plus tests & security scan. | You want it running on your machine. |
| **[02 · Architecture](02-architecture.md)** | The pipeline, data flow, every module's job, and the database schema. | You want to understand or extend the code. |
| **[03 · API Reference](03-api-reference.md)** | Every endpoint — request shapes, response shapes, error codes, and examples. | You're integrating with the backend. |
| **[04 · Scoring Methodology](04-scoring-methodology.md)** | The credence table, innovation tiers, the TF-IDF similarity math, and risk thresholds. | You want to know *how the numbers are computed*. |
| **[05 · User Guide](05-user-guide.md)** | A walkthrough of the five-tab dashboard and how to read a patentability score. | You're actually using the app. |

---

## The pipeline at a glance

```
┌───────────┐   ┌────────────┐   ┌───────────┐   ┌──────────┐   ┌───────────┐
│ 1. Upload │ → │ 2. Disclose│ → │ 3. Score  │ → │ 4. Risk  │ → │ 5. Audit  │
│  a PDF    │   │  the IP    │   │  the org  │   │  check   │   │  report   │
└───────────┘   └────────────┘   └───────────┘   └──────────┘   └───────────┘
   extract        persist +         aggregate       ad-hoc         compliance
   inventor       run similarity    credence score  similarity     transparency
```

> 📸 **[ Screenshot placeholder #1 — Dashboard overview showing the five-tab pipeline ]**
>
> _Paste a full-window screenshot of the dashboard here._

---

## Tech stack

| Layer     | Technology              |
|-----------|-------------------------|
| Backend   | FastAPI + Uvicorn       |
| Database  | SQLite (raw SQL, no ORM)|
| NLP       | scikit-learn (TF-IDF)   |
| PDF       | pdfplumber              |
| Frontend  | Streamlit               |
| Schemas   | Pydantic v2             |

---

*This is an internal prototype — for institutional use only.*
