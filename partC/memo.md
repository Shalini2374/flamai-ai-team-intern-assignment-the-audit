# Part C — Decision Memo: Casual Tone for 6 Indian Languages

## Assumptions
- No formal->casual training data exists yet; must be created from scratch.
- Main model already produces correct, formal responses in all 6 languages.
- "Casual" is a per-request need, not a permanent global switch.
- Reviewer is fluent only in Hindi and Kannada; the other 4 languages cannot be human-verified in this timeline.

## Options — Merits and Demerits
- **A) Full SFT:** Merit — fixes tone natively, no added latency. Demerit — needs the most data, highest/hardest-to-undo risk, unverifiable in 4/6 languages.
- **B) <=1B rewriter:** Merit — contained risk, easy to disable, less data needed than SFT. Demerit — adds latency, can drift meaning while casualizing.
- **C) Prompt-engineering only:** Merit — zero cost, instantly reversible, fast to test. Demerit — may be too weak alone for deeply formal output.

## Recommended Approach: Staged B + C, SFT Deferred

```
Day 1-3:   Prompt-only vs baseline -> meets threshold? -> SHIP, stop here
Day 4-10:  If not, train/test rewriter (Hindi/Kannada first)
           -> fails quality/meaning check? -> disable, fall back to prompt-only
Day 11-14: If passes, extend rewriter to remaining 4 languages (lower confidence)
Week 3:    Launch review, final go/no-go
```

**Routing:** system prompt + user signal (explicit setting or informal phrasing) decides casual vs formal. Only casual-tagged responses go through the rewriter, avoiding unnecessary latency/cost for formal requests.

SFT is deferred, not rejected — revisit once broader multilingual review capacity exists. Its permanent, hard-to-verify effect on 4 unchecked languages is a poor fit for this 3-week launch.

## Back-of-Envelope Arithmetic
- Reviewer capacity: 10 hrs/week x 2 weeks = 20 reviewer-hours, Hindi/Kannada only.
- At ~5 min/response: 20 x 60 / 5 = ~240 reviewable responses.
- Planning dataset: 500 formal/casual pairs/language x 6 languages = 3,000 training pairs.
- Planning assumption: a <=1B rewriter trained on ~3,000 pairs is feasible within the 2-week A100-80GB budget; actual training time must be validated by the Day-1 pilot.
- No external API budget is assumed; data generation uses available internal/local resources.

## Success Metric
>=70% of sampled Hindi/Kannada responses rated "casual and natural" by the reviewer, AND >=95% meaning preservation (no safety-relevant content softened or lost). Both required.

## Kill Criterion
By Day 10: if Hindi/Kannada casualness score is <50%, or any safety-relevant meaning-preservation failure is found, abandon the rewriter for launch and fall back to prompt-only across all 6 languages.

## Day-1 Experiment
Compare baseline vs. prompt-only-casual output on 20-30 prompts across all 6 languages. Reviewer scores the Hindi/Kannada subset; other 4 treated as lower-confidence. If prompt-only already clears the threshold, stop — skip building the rewriter entirely.
```
