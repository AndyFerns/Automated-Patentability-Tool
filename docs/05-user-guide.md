# 05 · User Guide

This is the hands-on walkthrough. We'll go through the dashboard tab by tab,
following the same left-to-right pipeline the UI is built around. By the end
you'll know how to file a disclosure, read a patentability score, and pull an
audit report.

Assuming both processes are running (see
[Getting Started](01-getting-started.md)), open **http://localhost:8501**.

---

## The layout

The dashboard has two parts:

- **The sidebar** (left) — branding, a light/dark toggle, a **Backend Status**
  badge, a **Pipeline Progress** stepper that lights up as you complete each
  step, and a **Reset workflow** button.
- **The five tabs** (main area) — the pipeline, in order:

```
1 · 📄 Upload   2 · 📝 Disclose   3 · 🏢 Score   4 · ⚠️ Risk   5 · 📋 Audit
```

> 📸 **[ Screenshot placeholder #2 — The dashboard with the sidebar and five tabs visible ]**
>
> _Paste a screenshot showing the sidebar (status + pipeline stepper) and the tab bar._

You don't *have* to go in order — every tab works on its own — but the "Next
step" cards will nudge you along the natural path.

---

## Tab 1 · Upload a document (optional)

Got a PDF of an invention disclosure or patent brief? Drop it here.

1. Upload a PDF (max 20 MB). You'll see the filename and size.
2. Click **Extract Information**.
3. The tool pulls out the **inventor name** (if it can find one) and shows a
   text preview.

The extracted inventor name is remembered — when you move to tab 2, it's
auto-filled for you. If no name is found (or the PDF is image-only, since there's
no OCR), you'll just enter it by hand in the next step. This tab **never saves
anything**; it's purely for extraction.

---

## Tab 2 · Add a disclosure

This is the core action — where an idea becomes a stored record **and** gets its
patentability check.

1. Fill in **Title** and **Description** (both required).
2. Pick an **IP Type**. This drives everything downstream — the credence weight,
   and whether a similarity check runs (only `Patent` triggers it).
3. Choose an **Organization** — pick an existing one from the dropdown, or select
   **"＋ Add a new organization…"** to type a fresh name.
4. **Inventor Name** is optional (and pre-filled if you came from tab 1).
5. Hit **Submit Disclosure**.

### Reading the result

On success you get a confirmation with the new disclosure ID. If it was a
**patent**, you also get the patentability check right there:

- **Similarity** — the highest match percentage against the reference dataset.
- **Risk Level** — Low / Medium / High.
- **Closest Match** — which reference patent it resembles most.
- **A risk gauge** — a horizontal bar showing your score against the 40% and 70%
  threshold markers, so you can see *how close* you are to the next tier.
- **A colored banner** spelling out what the risk means.

> 📸 **[ Screenshot placeholder #3 — A submitted patent showing the similarity metrics, risk gauge, and banner ]**
>
> _Paste a screenshot of the disclosure result with the risk gauge visible._

A **"Next step"** card then points you onward — to the Risk Check tab if the
patent flagged Medium/High, or to the Organization Score tab otherwise.

---

## Tab 3 · Organization score — *checking patentability at the org level*

This tab answers "how's this organization's IP portfolio doing overall?"

1. Pick an organization from the dropdown (pre-selected if you just filed one).
2. Click **Get Score**.

You'll see:

- **A tier badge** — the **Innovation Tier** (Emerging / Developing / Strong)
  with the total **IPR Score** and a progress bar toward the next tier.
- **A breakdown table** — per IP type: count, credence weight, and subtotal, so
  you can see exactly what's driving the score.
- **Patent Risk Flags** — any patents in this org that scored Medium or High
  risk, listed with their similarity and closest match. This is your at-a-glance
  "which of our patents might have novelty problems" view.

> 📸 **[ Screenshot placeholder #4 — The organization score with tier badge, breakdown table, and risk flags ]**
>
> _Paste a screenshot of the org score view._

**How to read patentability here:** the risk flags surface the weak spots. An org
can have a healthy IPR score but still carry a couple of high-risk patents worth
a closer prior-art look — this tab makes both visible at once.

---

## Tab 4 · Patent risk check — *testing patentability without committing*

Want to sanity-check an idea's patentability *before* filing it? This is the
sandbox.

1. Paste a description into the box.
2. Click **Analyse Similarity**.

You get the same metrics and risk gauge as tab 2 — similarity, risk level,
closest patent — **plus a "Top 5 matches" table** for context. The key
difference: **nothing is saved.** Tweak the wording, run it again, compare. It's
built for iteration.

When you're happy with a Low-risk result, the "Next step" card sends you to tab 2
to file it for real.

---

## Tab 5 · Audit report

The compliance and transparency view for a whole organization.

1. Pick an organization.
2. Click **Generate Audit Report**.

You get a structured report with:

- **Search scope** — databases and classifications considered, disclosures
  analysed.
- **Search logic validation** — boolean validity, keyword expansion, filters.
- **Quantitative metrics** — comparisons performed, risk threshold, scored docs.
- **System configuration** — the algorithm, feature limit, and risk thresholds.
- **Visual insights** — a result funnel, a similarity-vs-threshold chart, an IP
  type distribution, and a risk-level breakdown.

This is the doc you'd hand to someone who asks "okay, but *how* did you assess
these?" It's deterministic — it summarizes what already happened, it doesn't run
any new analysis.

---

## Putting it together — a typical session

1. **Upload** a disclosure PDF → inventor name extracted.
2. **Disclose** it as a Patent → stored, and you instantly see it's Medium risk.
3. Pop over to the **Risk Check** to test a reworded description → now Low risk.
4. Check the **Organization Score** → the org just moved from Emerging to
   Developing.
5. Generate an **Audit Report** for the record.

The sidebar's pipeline stepper tracks you the whole way, and **Reset workflow**
clears the slate when you want to start fresh.

---

## Tips

- **Backend status badge says "Unreachable"?** Your FastAPI server isn't running
  or isn't on the expected port. See [Getting Started](01-getting-started.md).
- **Only patents get a similarity score** — that's by design. Other IP types
  still count toward the IPR score via their credence weight.
- **Organization names are case-insensitive** — "Agnel", "agnel", and "Agnel "
  all resolve to the same org, so don't worry about exact casing.

---

That's the whole tool. For the mechanics behind these numbers, see
[Scoring Methodology](04-scoring-methodology.md); for the raw endpoints, see the
[API Reference](03-api-reference.md).
