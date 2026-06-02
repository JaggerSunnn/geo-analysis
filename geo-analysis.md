# GEO Analysis Skill — Clothing E-commerce

Use this skill to run a **Generative Engine Optimization (GEO)** analysis on any vertical using Claude as the answer engine, following the methodology of Chen et al. (2026).

## What this skill does

1. Sends 50 queries (17 informational / 17 consideration / 16 transactional) to Claude
2. Extracts every cited domain from each response
3. Classifies each domain as **Brand**, **Earned**, or **Social**
4. Computes per-intent and aggregate source typology percentages
5. Ranks the top 25 most-cited domains
6. Benchmarks results against the paper's Google and Claude baselines

## Paper baseline reference (Chen et al. 2026 — consumer electronics)

| System | Brand | Earned | Social |
|--------|-------|--------|--------|
| Google | 25.7% | 40.7% | 33.6% |
| Claude 4.5 Sonnet (paper) | 34.4% | 64.5% | 1.1% |
| GPT-4o | 35.6% | 56.9% | 7.6% |
| Perplexity | 38.7% | 49.9% | 11.4% |
| Gemini 2.5 Flash | 46.4% | 46.2% | 7.3% |

### By intent (Claude 4.5 Sonnet in paper)

| Intent | Brand | Earned | Social |
|--------|-------|--------|--------|
| Informational | 40.5% | 57.8% | 1.7% |
| Consideration | 12.7% | 85.9% | 1.5% |
| Transactional | 52.0% | 48.0% | 0.0% |

## Dimensions measured (all from paper)

### Dimension 1 — Domain overlap with Google
Jaccard overlap between AI-cited domains and Google top-10 results.
- Paper finding: Claude ≈ 12.6% mean overlap (median 8.7%)
- Niche queries raise overlap by +3–4 pp vs. popular queries

### Dimension 2 — Source typology
Three categories:
- **Brand** — official company-owned sites (e.g., nike.com)
- **Earned** — independent media / review outlets (e.g., vogue.com)
- **Social** — user-generated / community platforms (e.g., reddit.com)

Key finding: Claude heavily over-indexes on Earned, near-zero Social.

### Dimension 3 — Content freshness
Metric: median article age (days) of cited URLs.
- Paper: Claude median = 62.3 days (consumer electronics), 148.0 days (automotive)
- Google median = 130.4 days (electronics), 492.9 days (automotive)
- Claude consistently cites newer content than Google

Formula used by paper:
```
F_adj = F × coverage
F = (1/n) Σ 1/(1 + age_i)   [over dated URLs only]
```

### Dimension 4 — Pre-training bias
Two entity classes:
- **Popular entities**: rankings driven by pre-training priors; low sensitivity to snippet order (SS Δavg = 2.30) and entity swap (ESI Δavg = 2.60)
- **Niche entities**: rankings driven by retrieved evidence; high sensitivity (SS Δavg = 4.15, ESI Δavg = 4.63)

Pairwise ranking consistency (Kendall τ):
- Popular: τ = 0.911 (normal), 1.000 (strict grounding)
- Niche: τ = 0.556 (normal), 0.689 (strict grounding)

## How to run the clothing e-commerce experiment

```bash
# From this directory
cd C:\Users\JaggerSun\my-todo\GEO

# Set API key (one-time)
$env:ANTHROPIC_API_KEY = "sk-ant-..."

# Run 50-query experiment
python run_experiment.py
```

Results are saved to `geo_results.json`.

## How to adapt to a different vertical

Edit `QUERIES` dict in `run_experiment.py`. Keep the 17/17/16 split across intents.
Update `BRAND_DOMAINS` with known brand domains for the new vertical.
All analysis and reporting code works without changes.

## GEO implications (from paper Section 4)

For content creators and marketers optimizing for AI search (vs. SEO):

| Factor | SEO (Google) | GEO / AEO (Claude, GPT) |
|--------|-------------|------------------------|
| Top source type cited | Mixed | Earned >> Social |
| Content freshness | Older acceptable | Newer = higher citation rate |
| Popular entity coverage | Backlink authority | Pre-training priors dominate |
| Niche entity coverage | Authority signals | Must appear in real-time retrieval |
| Position in context | Matters for ranking | Less critical once in context window |

Key GEO actions:
1. Publish on **earned media** (independent review sites, fashion press)
2. Maintain **fresh content** (AI favors <90 day old articles)
3. For niche brands: invest in **retrieval coverage** (be cited in review snippets)
4. For popular brands: focus on **pre-training footprint** (authoritative brand presence)

## Files in this directory

| File | Purpose |
|------|---------|
| `run_experiment.py` | Full 50-query experiment runner |
| `geo_results.json` | Latest experiment output (created on run) |
| `geo-analysis.md` | This skill documentation |
