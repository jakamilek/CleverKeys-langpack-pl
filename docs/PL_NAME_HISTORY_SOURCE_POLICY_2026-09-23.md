# Polish proper-noun historical name source policy — 2026-09-23

Status: accepted design decision, audit-only. No promotion to the language pack.

## Objective

Keep a small, evidence-based historical first-name layer for names associated with older Polish generations, without importing the full PESEL name universe.

## Historical source A — Rymut / PESEL

Primary historical source:

Kazimierz Rymut, *Słownik imion współcześnie w Polsce używanych* (Instytut Języka Polskiego PAN, Kraków, 1995).

The publication metadata states that the work was prepared from materials of the Rządowe Centrum Informatyczne PESEL.

For the historical layer, use the frequency information by birth-period as the primary evidence. The documented periods include:

- 1941–1950
- 1951–1960
- 1961–1970
- 1971–1980
- 1981–1990
- 1991–April 1994

The source is used as a historical frequency reference, not as an automatic import list.

## Historical source B — 1995–1999 bridge

Rymut's PESEL-based book ends in 1994. The 1995–1999 bridge should therefore use a separate scholarly nationwide source rather than extending Rymut artificially.

Preferred bridge:

Paweł Swoboda, *Imiona częste w Polsce w latach 1995–2010 oraz ich zróżnicowanie w czasie i przestrzeni*.

This study analyses nationwide first-name frequency in 1995–2010 and explicitly compares the frequent-name resource with earlier national periods.

Only the 1995–1999 portion is relevant to this historical bridge.

## Selection policy

The historical layer is intentionally smaller and less computationally intensive than the 2006–2025 audit.

Do not:

- import every name present in Rymut;
- import every name present in the 1995–2010 study;
- use a web ranking or blog as an equivalent source;
- automatically promote historical names solely because the name appears in a source.

The eventual historical core should be selected from names with strong long-period frequency evidence, preferably appearing as frequent names across more than one older period, with manual review for common-word collisions and unusual/foreign forms.

## Modern 2006–2025 selection policy

For the modern layer, the quantitative audit is retained in full, but the working candidate split is:

- core: top 215 names per gender by the documented 20-year ranking;
- safety buffer: ranks 216–300 per gender, retained for audit/review only;
- the buffer is not an automatic promotion pool and does not enlarge the core.

The split is a selection boundary for project review, not a claim that rank 216 is categorically unsafe or rank 215 categorically safe. Existing source-safety, collision, language-evidence, morphology and runtime review gates still apply to every candidate.

## Separation from the modern layer

Modern layer:
- full-year 2006–2025 first-name statistics;
- quantitative multi-year ranking and stability analysis.

Historical layer:
- Rymut/PESEL period frequencies through 1994;
- scholarly nationwide bridge for 1995–1999;
- smaller reviewed set;
- no requirement for a second mass morphology audit before candidate review.

## Provenance requirements

Every promoted historical name must retain:

- source identifier/title;
- period(s) supporting the name;
- frequency evidence where available;
- reason for inclusion;
- collision/review status.

Audit staging currently includes a small candidate file at `sources/staging/historical_name_candidates.tsv`. It contains 26 names absent from the modern 2006–2025 core (10 female, 16 male) whose historical support is attested by the Swoboda 2013 comparison tables through 1981–1990 and 1901–1994/XX-century ranks. This is a review queue only. Before promotion, each candidate must be checked directly against the Rymut 1995 entry and retain the relevant period/frequency evidence, collision review, and inclusion reason.

This document does not itself authorize promotion of any name.
