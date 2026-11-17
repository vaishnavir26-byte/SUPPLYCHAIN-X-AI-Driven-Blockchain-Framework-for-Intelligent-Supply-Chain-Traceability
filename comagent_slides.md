---
marp: true
theme: default
paginate: true
header: "ComAgent • Reliability-Aware Wireless Resource Allocation"
footer: "Department of CSE • Presidency University, Bengaluru • 2026"
style: |
  section {
    background-color: #0f172a;
    color: #f8fafc;
    font-family: 'Inter', sans-serif;
  }
  h1, h2, h3 {
    color: #38bdf8;
  }
  table {
    font-size: 0.75rem;
    color: #e2e8f0;
  }
  th {
    background-color: #1e293b;
    color: #38bdf8;
  }
  td {
    border-color: #334155;
  }
  blockquote {
    background: #1e293b;
    border-left: 5px solid #38bdf8;
    color: #94a3b8;
  }
---

<!-- Slide 01 -->
# COMAGENT
## Reliability-Aware Wireless Resource Allocation
**Reference-grounded architecture • model snapshot • concise implementation**

**Research Presentation • 2026**

**Project Team:**
- Vaishnavi R — 20241CSE0706
- Reshma K — 20241CSE0694
- M B Gayatri — 20241CSE0704
- Prakruthi HR — 20241CSE0703

*Department of Computer Science and Engineering • Presidency University, Bengaluru*

---

<!-- Slide 02 -->
# 01 • Presentation Map
### What This Presentation Explains

A concise path from published foundations to the implemented simulator and measured evidence.

- **01 Literature:** What each cited work contributes
- **02 Model:** Network assumptions and Shannon rate equation
- **03 Architecture:** How inputs flow through allocation and evaluation
- **04 Implementation:** Short code excerpts tied to model blocks
- **05 Evidence:** Results, trade-offs, and research limitations

> **Key Distinction:** The references provide established principles and evaluation methods; ComAgent combines them in a controlled simulation study.

---

<!-- Slide 03 -->
# 02 • Research Summary
### Abstract in One Slide

**Research Question:**  
*Can target-aware allocation increase the number of users meeting a required data rate without hiding the costs in throughput or fairness?*

- **4 User Populations:** 5, 10, 20, 50 users
- **3 Target Rates:** 0.5, 1.0, 2.0 Mbps
- **10 Random Seeds:** 42–51 (paired across methods)
- **4 Allocation Methods:** Equal, Greedy, Proportional Fair, Reliability Aware V2
- **Total Evaluations:** 4 × 12 × 10 = **480 evaluations**

**Core Finding:** V2 improves reliability in **8 out of 12 scenarios**, but its Jain fairness is lower than Equal in all 12.

---

<!-- Slide 04 -->
# 03 • Motivation
### Why Resource Allocation Is Difficult

Users compete for limited spectrum and power, but their channel conditions are heterogeneous.

**Network Constraints:**
- Finite bandwidth ($B_{\max} = 10.0\text{ MHz}$) and transmit power ($P_{\max} = 1.0\text{ W}$)
- Different channel power gains ($g_i$)
- Noise floor ($N_i$) and co-channel interference ($I_i$)

**Competing Objectives:**
- High aggregate throughput vs. Meeting per-user target rates ($R_t$)
- Avoid starving weak users vs. Maintaining rate fairness

**Design Implication:** One metric is insufficient. Report reliability and fairness trade-offs simultaneously.

---

<!-- Slide 05 -->
# 04 • Literature Review
### There Is No Single Complete Base Paper

ComAgent synthesizes 5 established research subfields:

1. **Wireless Allocation:** Shams 2014; Yaacoub & Dawy 2012; Ribeiro 2012
2. **Proportional Fairness:** Kelly et al. 1998; Kelly 1997; Mo & Walrand 2000
3. **Fairness Measurement:** Jain et al. 1984
4. **Rate Abstraction:** Shannon 1948; Goldsmith 2005
5. **Uncertainty Analysis:** Efron & Tibshirani 1993; Davison & Hinkley 1997
6. **Future Agent Layer:** ReAct, Toolformer, AutoGen, MetaGPT; wireless LLM surveys

*These works provide foundations—they do not claim that the cited authors proposed ComAgent.*

---

<!-- Slide 06 -->
# 05 • What We Used From References
### Reference → Architecture → Implementation

| Reference | Idea Taken | How Used in ComAgent | Architecture Block |
| :--- | :--- | :--- | :--- |
| **Shams et al. (2014)** | OFDM(A) landscape | Motivates policy comparison | Scenario + Allocator |
| **Yaacoub & Dawy (2012)** | Uplink OFDMA constraints | Explicit resource caps | Resource Budget Model |
| **Kelly et al. (1998)** | Log utility / PF | Basis for PF comparator | PF Strategy |
| **Jain et al. (1984)** | Fairness index | Measures rate equality | Metrics Engine |
| **Shannon (1948) / Goldsmith** | Capacity / rate relation | Achievable rate abstraction | Rate Calculator |
| **Efron & Tibshirani (1993)** | Bootstrap resampling | 95% CIs on paired seeds | Statistical Analysis |

---

<!-- Slide 07 -->
# 06 • Reference Detail: Wireless Surveys
### What Informed the Design

**Literature Covered:** Bandwidth assignment, power control, OFDMA allocation, QoS constrained optimization.

**What ComAgent Borrows:**
- Shared wireless-resource problem framing
- Multiple allocation policies for comparison
- Explicit bandwidth (10 MHz) and power (1.0 W) budgets
- Per-user rates under channel/noise/interference assumptions

**What It Does NOT Claim:**
- Not a complete OFDMA physical scheduler
- Not a 3GPP NR PHY implementation
- Not a calibrated physical radio propagation study

---

<!-- Slide 08 -->
# 07 • Reference Detail: Proportional Fair
### Kelly et al. (1998) as a Comparator Principle

**Core Idea:** Logarithmic utility balances sum-rate with relative user service:
$$\text{maximize} \quad \sum_{i=1}^N \log(r_i)$$

**How It Enters ComAgent:**
- PF is one of four deterministic methods evaluated.
- Evaluated on identical generated scenarios and seeds using throughput, reliability, min rate, and Jain fairness.

**Audit Note:** In reported simulation runs, PF and Equal summaries converged to identical outputs across multiple seeds. We document this honestly as requiring a gradient step audit.

---

<!-- Slide 09 -->
# 08 • Reference Detail: Jain's Fairness Index
### Jain et al. (1984): How Fairness Is Measured

$$J(r) = \frac{\left(\sum_{i=1}^N r_i\right)^2}{N \sum_{i=1}^N r_i^2}$$

- **Range:** $[1/N, 1.0]$
- **Closer to 1:** Rates are completely equal
- **Lower value:** Allocation is uneven / skewed

**Findings in ComAgent:**
- Input: Achieved rate vector $r$
- Reported alongside Throughput and Reliability
- **V2 has lower Jain fairness than Equal in all 12 scenarios.**

---

<!-- Slide 10 -->
# 09 • Reference Detail: Achievable Rate
### Shannon & Goldsmith Rate Abstraction

$$r_i = B_i \log_2\left(1 + \frac{P_i g_i}{N_i + I_i}\right)$$

- $B_i$: Assigned bandwidth (portion of 10 MHz)
- $P_i$: Assigned power (portion of 1.0 W)
- $g_i$: Channel power gain
- $N_i$: Bandwidth-scaled thermal noise floor ($N_0 B_i$)
- $I_i$: Modeled cross-user interference

*Status: Simplified mathematical abstraction for policy comparison, not field-calibrated PHY.*

---

<!-- Slide 11 -->
# 10 • Reference Detail: Bootstrap Resampling
### Efron & Tibshirani (1993): Paired Bootstrap

Because identical seeds are paired across methods, analysis resamples matched seed differences:

1. **Pair:** For each seed $k \in \{42..51\}$, compute $\Delta_k = R_{\text{V2}}(k) - R_{\text{Eq}}(k)$
2. **Resample:** Sample paired differences with replacement
3. **Repeat:** 20,000 bootstrap resamples
4. **Interval:** 2.5th and 97.5th percentiles (95% percentile CI)

**Parameters:** 10 paired seeds • RNG seed 20261029 • 95% Percentile CI

---

<!-- Slide 12 -->
# 11 • System Model Snapshot
### From Users to Achieved Rates

```
+----------------------------------------------------+
|            BASE STATION / RESOURCE POOL            |
|       10 MHz Bandwidth   •   1.0 W Transmit Power  |
+----------------------------------------------------+
                          |
             [ Resource Allocation (B, P) ]
                          |
       +------------------+------------------+
       |                  |                  |
    User 1             User 2             User N
 (Near Tower)        (Mid-Cell)        (Cell-Edge)
g1 • N1 • I1       g2 • N2 • I2       gN • NN • IN
```

Rate model computes $r_i$ for each user $\rightarrow$ compared against target threshold $R_t$.

---

<!-- Slide 13 -->
# 12 • Model Formulation
### Inputs, Decision Variables, and Constraints

**Inputs:**
- $N$ users $\in \{5, 10, 20, 50\}$, Target rate $R_t \in \{0.5, 1.0, 2.0\}\text{ Mbps}$
- Channel gain $g_i$, Noise $N_i$, Interference $I_i$
- Total budgets: $B_{\max} = 10.0\text{ MHz}$, $P_{\max} = 1.0\text{ W}$

**Decision Variables:**
- $B_i \ge 0, \quad P_i \ge 0 \quad \forall i \in \{1 \dots N\}$

**Programmed Budget Checks:**
$$\sum B_i \le 10.0\text{ MHz}, \quad \sum P_i \le 1.0\text{ W}, \quad B_i \ge 0, \quad P_i \ge 0$$
*100% of 480 evaluations passed tolerance-aware budget validation.*

---

<!-- Slide 14 -->
# 13 • Research Architecture
### ComAgent End-to-End Pipeline

```
[ Scenario Generator ]  -->  [ Channel Model ]  -->  [ Allocation Strategies ]
  N, Rt, Seeds 42-51          gi, Ni, Ii             Equal, Greedy, PF, V2
                                                              |
                                                              v
[ Statistical Report ]  <--  [ Metrics Engine ] <--  [ Rate Engine & Validator ]
  Mean +/- SD, 95% CI          T, R, Min, Jain        ri calculation & budgets
```

Decoupled pipeline allows testing new allocation policies without altering rate or metric modules.

---

<!-- Slide 15 -->
# 14 • Proposed Model Snapshot
### Reliability Aware V2: Decision Flow

1. **Input:** Users, target rate $R_t$, channel state $(g_i, N_i, I_i)$
2. **Estimate Need:** Compute bandwidth $\hat{B}_i$ needed to hit $R_t$ under baseline power
3. **Sort / Prioritize:** Order users ascending by required resource footprint
4. **Feasibility Check:** Does need fit within remaining budget?
5. **Allocate:** Commit resources to feasible users first
6. **Surplus Redistribution:** Distribute remaining chunks greedily

*V2 is an engineering heuristic; it is not guaranteed to be Pareto optimal across all dimensions.*

---

<!-- Slide 16 -->
# 15 • Model Improvement
### Old Baseline vs Proposed V2

**Old Model: Equal Allocation**
- $B_i = B_{\max} / N, \quad P_i = P_{\max} / N$
- **Strength:** Simple, predictable, maximal Jain fairness
- **Limitation:** Does not adapt to channel differences or target bit rates

**New Model: Reliability Aware V2**
- Target-aware, feasible-first prioritization + greedy remainder
- **Strength:** Drastically boosts target rate compliance
- **Trade-off:** Jain fairness decreases

*Design change: Equal resource sharing $\rightarrow$ Target-aware allocation.*

---

<!-- Slide 17 -->
# 16 • Experiment Design
### Reproducible Factorial Matrix

- **Users ($N$):** 5, 10, 20, 50 (4 populations)
- **Target Rates ($R_t$):** 0.5, 1.0, 2.0 Mbps (3 targets)
- **Seeds:** 42–51 (10 matched random seeds)
- **Methods:** Equal, Greedy, Proportional Fair, Reliability Aware V2

$$\text{Total Runs} = 4 \times 3 \times 10 \times 4 = \mathbf{480\text{ evaluations}}$$

*All 480 evaluations passed programmed resource budget checks.*

---

<!-- Slide 18 -->
# 17 • Rate Calculation & Metrics
### Translating Allocations into Performance

Achievable rate depends on:
- Assigned bandwidth ($B_i$) & power ($P_i$)
- Channel quality ($g_i$) & noise + interference floor ($N_i + I_i$)

**Derived Metrics:**
- **Throughput ($T$):** Sum of user rates $\sum r_i$ (Mbps)
- **Reliability ($R$):** Percentage of users with $r_i \ge R_t$ (%)
- **Minimum Rate:** Starvation floor measurement (Mbps)
- **Jain Fairness ($J$):** Evenness of rate distribution

---

<!-- Slide 19 -->
# 18 • Method Comparison
### How the Four Allocators Differ

- **Equal Allocation:** Splits resources evenly. High fairness, poor outage control.
- **Greedy Allocation:** Assigns resources to maximize immediate aggregate throughput. Starves cell-edge users.
- **Proportional Fair:** Balances sum-rate with relative user service via logarithmic utility.
- **Reliability Aware V2:** Prioritizes meeting target rates for as many users as possible.

---

<!-- Slide 20 -->
# 19 • Validation & Statistics
### Constraints and Resampling

**Resource Budget Validation:**
- Total bandwidth $\le 10.0\text{ MHz}$
- Total power $\le 1.0\text{ W}$
- Finite, non-negative allocations

**Statistical Comparison:**
- Paired-seed evaluation isolates allocation policy from random channel variations.
- Bootstrap 95% confidence intervals indicate whether observed gains are statistically distinct from zero.

---

<!-- Slide 21 -->
# 20 • Benchmark Results
### 10 Users, 1.0 Mbps Target Rate

*(Mean across 10 paired seeds 42–51)*

| Metric | Equal Allocation | Reliability Aware V2 | Observed Delta |
| :--- | :---: | :---: | :---: |
| **Throughput** | 24.722 Mbps | 25.353 Mbps | **+0.631 Mbps (+2.6%)** |
| **Reliability** | 67.000% | 77.000% | **+10.00 pp** |
| **Jain Fairness** | **0.570** | **0.274** | **−0.296 (Lower Fairness)** |

*Key takeaway: Higher throughput and +10 pp reliability at the cost of lower fairness.*

---

<!-- Slide 22 -->
# 21 • Scenario-Wide Results
### Does V2 Improve Reliability Everywhere?

**No. The outcome depends on user population and target rate:**

- **IMPROVED (8 / 12 scenarios):** Under moderate and heavy congestion ($N \ge 10$)
- **UNCHANGED (1 / 12 scenarios):** At 5 users, 1.0 Mbps target (+0.0 pp)
- **DECREASED (3 / 12 scenarios):** Strictly at 5 users (drops by 4–6 pp)

> **Important:** All 3 decreases occur at 5 users, where Equal Allocation already has abundant spectrum and near-perfect reliability. V2's Jain fairness is lower in all 12 scenarios.

---

<!-- Slide 23 -->
# 22 • Visual Result Map
### Reliability Delta Matrix ($\text{V2} - \text{Equal}$ in pp)

| Users \ Target | 0.5 Mbps | 1.0 Mbps | 2.0 Mbps | Verdict |
| :--- | :---: | :---: | :---: | :--- |
| **5 Users** | **-6.0 pp** | **+0.0 pp** | **-4.0 pp** | Equal allocation superior |
| **10 Users** | **+20.0 pp** | **+10.0 pp** | **+18.0 pp** | Substantial gain |
| **20 Users** | **+5.0 pp** | **+19.0 pp** | **+22.5 pp** | Robust gain under load |
| **50 Users** | **+19.6 pp** | **+25.8 pp** | **+20.6 pp** | **Peak gain: +25.8 pp** |

*Largest observed gain: **+25.8 pp** at 50 users, 1.0 Mbps target.*

---

<!-- Slide 24 -->
# 23 • Uncertainty Analysis
### Paired Bootstrap Confidence Intervals (20,000 Resamples)

- **10 Users • 1.0 Mbps Target:**  
  Mean Delta: **+10.0 pp** | 95% CI: **[−8.0 pp, +23.0 pp]**  
  *Includes Zero: Statistically uncertain under small seed size ($N=10$).*

- **20 Users • 2.0 Mbps Target:**  
  Mean Delta: **+22.5 pp** | 95% CI: **[+12.5 pp, +31.0 pp]**  
  *Excludes Zero: Statistically significant.*

- **50 Users • 1.0 Mbps Target:**  
  Mean Delta: **+25.8 pp** | 95% CI: **[+15.6 pp, +34.6 pp]**  
  *Excludes Zero: Statistically significant.*

---

<!-- Slide 25 -->
# 24 • Limitations & Research Integrity
### What the Current Evidence Does Not Prove

**Model Boundaries:**
- Shannon-style capacity abstraction; not 3GPP NR PHY, no multipath Doppler.
- 10 seeds per scenario (preliminary exploration).
- V2 is a heuristic, not a mathematically guaranteed global optimum.
- PF implementation audit is needed (matched Equal outputs in baseline runs).

**Evidence Boundaries:**
- 480 checks validate programmed budgets only.
- LLM selector hit API rate limits in automated tests; current evidence validates deterministic algorithms.

---

<!-- Slide 26 -->
# 25 • Conclusion & Literature Mapping
### Summary of Findings & References

**Conclusion:**  
V2 improves reliability in **8 out of 12 scenarios**, but Jain fairness is lower than Equal in all 12. It represents a **reliability-focused engineering trade-off**, not a universal drop-in replacement.

**Selected Foundational References:**
1. Kelly et al. (1998) — Proportional fairness utility
2. Jain et al. (1984) — Fairness index metric
3. Shams et al. (2014) — OFDMA resource allocation survey
4. Yaacoub & Dawy (2012) — Uplink OFDMA constraint formulation
5. Shannon (1948) & Goldsmith (2005) — Capacity & rate modeling
6. Efron & Tibshirani (1993) — Paired bootstrap statistics

---

<!-- Slide 27 -->
# 26 • Implementation Mapping Detail
### Distinguishing Implementation from Motivation

- **Directly Implemented:** Jain's Fairness Index formula $(\sum r_i)^2 / (N \sum r_i^2)$ coded directly into metrics engine.
- **Model Abstraction:** Simplified Shannon equation $r_i = B_i \log_2(1 + \text{SINR}_i)$ for user rate calculation.
- **Analysis Method:** 20,000-resample paired bootstrap for 95% confidence intervals.
- **Conceptual Context:** Kelly PF log utility and Shams OFDMA surveys provide comparison framing.

*Academic distinction: We implemented a comparative simulation framework, not full hardware transceivers.*

---

<!-- Slide 28 -->
# 27 • Experiment Dataset Log
### Reproducible 480-Row CSV Matrix

Sample configuration record from experiment database:
```csv
experiment_id,num_users,target_rate_mbps,random_seed,allocation_method,bandwidth_budget_mhz,power_budget_w
CA-50-1-42-equal,50,1.0,42,Equal,10.0,1.0
CA-50-1-42-greedy,50,1.0,42,Greedy,10.0,1.0
CA-50-1-42-proportional_fair,50,1.0,42,Proportional Fair,10.0,1.0
CA-50-1-42-reliability_aware_v2,50,1.0,42,Reliability Aware V2,10.0,1.0
```

**Live Deployment:** https://spectacular-peony-b06cf6.netlify.app  
**GitHub Repository:** https://github.com/vaishnavir26-byte/ComAgent-Wireless-Optimization.git

*Thank you! We welcome questions and discussion.*
