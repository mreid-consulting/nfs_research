# Paper Outline (one-page human review)

**Title:** Uncertainty-Aware Fire Risk Assessment for UK Residential Buildings
Using Public Data and Physics-Informed Simulation
**Author:** Matthew Reid

**Core thesis.** UK fire risk assessment is periodic, qualitative, and
compliance-driven. It should instead be dynamic probabilistic inference: a
building's fire risk is a *posterior distribution* over ignition, spread,
evacuation failure, and consequence severity, updated as evidence arrives.
Inspection findings are noisy observations, not ground truth; fire outcomes are
rare events. Scope: residential buildings in England (flats / high-rise / HMOs).

## 1. Introduction
UK FRA is static and compliance-driven (RRO 2005, PAS 79). Anchored by official
statistics (40,350 building fires in England, YE Dec 2025, +5.5%). Post-Grenfell
context: Grenfell Phase 2 Inquiry, Fire Safety Act 2021, Building Safety Act
2022. Gap: risk reported as a score not a distribution; inspections treated as
ground truth; rare-event calibration ignored. Five contributions listed.

## 2. Related Work
Restructured around eight literature themes, each
with a short positioning line keyed to our seven differentiators (A UK-FRA/BSA
integration, B Bayesian latent-state, C calibrated UQ, D inspection-as-noisy-
observation, E rare-event treatment, F physics-informed surrogate, G decision-
theoretic inspection): (1) UK fire-safety landscape and post-Grenfell regulation
(Hackitt 2018; Dauda et al. 2025; Yung 2008); (2) probabilistic / Bayesian-
network fire models incl. the closest competitor line (Matellini et al.
2018/2013) and the Grenfell credal-network PRA (Estrada-Lugo et al. 2019);
(3) UQ, risk-matrix critique and decision-theoretic / risk-based inspection
(Cox 2008; Gneiting et al. 2007; Straub & Faber 2005; Luque & Straub 2019);
(4) fire-risk datasets and geospatial targeting (Li et al. 2022; IberFire 2025);
(5) ML/AI in fire safety and its UQ critiques (Naser 2021; Tapeh & Naser 2022);
(6) physics-informed simulation surrogates (Yarmohammadian et al. 2025); (7)
coupled fire--evacuation modelling (Babrauskas et al. 2010; Cheong et al. 2021);
(8) rare-event / EVT statistical methods (Ramachandran 1974; McNeil 1997). Closes
with a positioning paragraph: no prior work integrates all seven differentiators
in one framework --- that integration is the novelty claim.

## 3. Probabilistic Model *(written out in full, with equations)*
- Risk as expected loss: R_b(t) = P(I_b(t)) · E[C_b(t) | I_b(t)].
- Consequence decomposition: E[C|I] = P(S|I) · P(E_f|S,I) · E[L|E_f,S,I].
- Latent building state z_b, evidence x_b; infer P(z_b|x_b), propagate to
  P(R_b|x_b). Risk is a distribution, not a score.
- Inspection as noisy observation (observation model, expected value of
  inspection).
- Rare events and calibration (hierarchical pooling, proper scoring, coverage).

## 4. Data
Open English datasets (fire incident statistics, EPC register, IMD, Census 2021,
CQC/HMO registers; footprints and weather later). Populated from
`data/sources/*.md`. Includes a dataset table stub.

## 5. Physics-Informed Consequence Surrogate
Synthetic archetype building graphs (detached, terraced, low-rise flat,
high-rise flat, HMO, care-home-like, mixed-use). Stochastic fire-spread +
evacuation simulation on the graph; physics-informed surrogate emulates
consequence distributions feeding the model. No real geometry in v1.

## 6. Results
Fitted end-to-end. Subsections: (a) fire-occurrence model + calibration + ablation
/ BYM2 spatial / subgroups; (b) consequence severity (casualty, serious spread),
alarm ladder, proper scores, full-data agreement; (c) interaction structure
(alarm x occupancy, night x dwelling); (d) simulation + surrogate across the seven
archetypes; (e) synthesis (worked risk decomposition); (f) decision layer
(value-of-targeting, EVI, budget-sweep break-even); (g) real-building stress test
(Grenfell, incl. as-unfolded hindcast); (h) instantiating the inspection layer on
the Camden FRA corpus (measurement model, worked posterior update, assessor-noise
bounds); (i) ignition-source trends.

## 7. Discussion and Limitations
Fit to post-Grenfell regulation; from checklists to live safety intelligence.
Limitations: England-only MVP, archetype (not real) geometry, data-linkage gaps,
rare-event validation only at aggregate level, simplified simulation.

## 8. Conclusion
FRA recast as Bayesian inference; the novelty is the *integration* of all five
elements. Future work: real geometry, dynamic updating, wider building classes,
live deployment.

---
**References:** 69 verified entries in `references.bib` (17 originals plus 51
from the deep literature sweep, de-duplicated by DOI, plus BS 8674:2025).
