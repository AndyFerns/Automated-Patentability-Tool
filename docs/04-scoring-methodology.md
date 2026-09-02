# 04 · Scoring Methodology

This is where the numbers come from. Two independent systems produce them:

1. **The IPR score** — a credence-weighted count that measures an organization's
   overall IP output.
2. **The patentability / similarity check** — a TF-IDF + cosine-similarity risk
   assessment for individual patents.

They're separate on purpose. The IPR score is deterministic arithmetic; the
similarity check is an NLP model. Let's take them one at a time.

---

## Part 1 — The IPR score

### The credence table

Every IP type carries a **credence weight** reflecting how much institutional
value it represents. This table is the single source of truth
([credence_table.py](https://github.com/AndyFerns/Automated-Patentability-Tool/blob/master/app/credence_table.py)):

| IP Type | Weight |
|---------|:------:|
| Patent | 3.0 |
| Industrial Design | 2.0 |
| Copyright | 1.0 |
| Trademark | 1.5 |
| Layout Design of Integrated Circuit (LD of IC) | 0.2 |
| Geographical Indication (GI) | 1.5 |
| Trade Secret (TS) | 0.0 |
| Protection of Plant Varieties and Farmers' Rights (PVFR) | 3.0 |

### The formula

```
IPR Score = Σ (count_of_ip_type × credence_weight)
```

That's it — count how many disclosures of each type an org has, multiply by the
weight, and sum. A **breakdown** row is produced per type showing
`count`, `credence`, and `subtotal`.

### Worked example

An organization with **3 patents** and **2 copyrights**:

| IP Type | Count | Credence | Subtotal |
|---------|:-----:|:--------:|:--------:|
| Copyright | 2 | 1.0 | 2.0 |
| Patent | 3 | 3.0 | 9.0 |
| | | **Total** | **11.0** |

**IPR Score = 11.0**

### Innovation tiers

The total score maps to a tier (thresholds are inclusive):

| Score range | Tier |
|-------------|------|
| 0 – 5 | **Emerging** |
| 6 – 15 | **Developing** |
| 16 + | **Strong** |

So our example org (score 11.0) lands in **Developing**. The dashboard renders
this as a colored badge with a progress bar showing how far along you are toward
the next tier.

> **Note:** Trade Secret carries a weight of `0.0`, so it contributes to your
> disclosure *count* and shows in the breakdown, but adds nothing to the score.
> That's intentional — trade secrets are unregistered by nature.

---

## Part 2 — Patentability & similarity

For every disclosure with `ip_type == "Patent"`, the tool estimates **how close
the description is to existing patents**. High similarity = high risk that the
idea isn't novel = lower patentability.

### The algorithm

```
description ─▶ TF-IDF vectorize ─▶ cosine similarity vs. every reference patent
                                        │
                                   take the max
                                        ▼
                          similarity_score  (0–100%)
```

- **TF-IDF** (Term Frequency–Inverse Document Frequency) turns each description
  into a weighted word vector, with English stop-words removed. Common words
  count for little; distinctive terms count for a lot.
- **Cosine similarity** measures the angle between your description's vector and
  each reference patent's vector. `1.0` (100%) means identical direction; `0.0`
  means no shared meaningful terms.
- The **highest** similarity across the reference set becomes your score, and
  that patent's title becomes `most_similar_patent`.

The reference set is `data/mock_patents.json` (10 patents). The vectorizer is
fitted once and cached.

### Risk thresholds

The similarity percentage maps to a risk level
([patent_similarity.py](https://github.com/AndyFerns/Automated-Patentability-Tool/blob/master/app/patent_similarity.py)):

| Similarity | Risk | Meaning |
|------------|------|---------|
| `> 70%` | 🔴 **High** | Significant overlap — thorough prior-art clearance strongly advised. |
| `40 – 70%` | 🟡 **Medium** | Some overlap — a detailed prior-art search is worth doing before filing. |
| `< 40%` | 🟢 **Low** | Minimal overlap with known patents. |

**Reading it as patentability:** low similarity → likely more novel → stronger
patentability case. High similarity → probably not novel → weaker case. The tool
gives you the signal; a patent attorney gives you the verdict.

### Edge cases the engine handles

- **Empty / whitespace-only description** → returns `Low / N/A / 0.0%` instead of
  a bogus match.
- **Description with only stop-words or unknown terms** (zero TF-IDF vector) →
  same safe `Low / N/A / 0.0%`.
- **Missing or corrupt reference dataset** → returns the safe default rather than
  crashing.

### Where this shows up

- **Live, at disclosure time** — `POST /disclosure` runs it inline and stores the
  result (tab 2 in the dashboard).
- **Ad-hoc, non-persisting** — `POST /similarity` runs the exact same math without
  saving anything (tab 4, the "Risk Check").

---

## How the two systems meet

The audit report (`GET /audit/{org}`) stitches them together: it reports the IP
distribution (part 1's raw material) alongside the similarity-score distribution
and risk breakdown (part 2's output), giving a single transparency view of an
organization's portfolio.

---

**Next:** [05 · User Guide](05-user-guide.md) to see all of this in the actual
dashboard.
