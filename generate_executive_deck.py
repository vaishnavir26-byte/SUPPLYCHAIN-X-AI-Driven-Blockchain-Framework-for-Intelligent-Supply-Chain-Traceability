#!/usr/bin/env python3
"""
generate_executive_deck.py
Generates a focused 10-Slide Executive Presentation (.pptx)
for university viva / project reviews (7–10 minute slot).
"""

from generate_all_presentations import build_pptx

executive_slides = [
    {
        "category": "Project Review • Presidency University",
        "title": "COMAGENT: Reliability-Aware Wireless Resource Allocation",
        "speaker": "Vaishnavi R",
        "bullets": [
            "Department of Computer Science & Engineering • Presidency University, Bengaluru (2026)",
            "Project Team: Vaishnavi R (0706) • Reshma K (0694) • M B Gayatri (0704) • Prakruthi HR (0703)",
            "Core Premise: Maximum aggregate throughput does not equal network reliability",
            "Deployed Simulator: https://spectacular-peony-b06cf6.netlify.app",
            "GitHub Repository: https://github.com/vaishnavir26-byte/ComAgent-Wireless-Optimization.git"
        ]
    },
    {
        "category": "Problem Statement",
        "title": "The Outage Dilemma in Shared Spectrum",
        "speaker": "Vaishnavi R",
        "bullets": [
            "Physical Limits: 50 heterogeneous users competing for 10.0 MHz bandwidth & 1.0 W transmit power",
            "Channel Heterogeneity: Distance pathloss, multipath fading, and interference create massive rate disparities",
            "The Flaw of Sum-Rate Maximization: Greedy allocators favor near-tower users, achieving high speed while starving cell-edge users",
            "Research Objective: Maximize the percentage of users meeting target bit rates (Rt) while quantifying fairness costs"
        ]
    },
    {
        "category": "Mathematical Model",
        "title": "Rate Abstraction & Fairness Metrics",
        "speaker": "Reshma K",
        "bullets": [
            "Shannon Achievable Rate: r_i = B_i * log2( 1 + [ P_i * g_i ] / [ N_i + I_i ] )",
            "Bandwidth-Scaled Noise: N_i = N0 * B_i with modeled cross-user coupling interference I_i",
            "Jain's Fairness Index: J(r) = (sum r_i)^2 / [ N * sum(r_i^2) ], bounded in [1/N, 1.0]",
            "Proportional Fairness Benchmark: Log-utility maximization based on Kelly et al. (1998)"
        ]
    },
    {
        "category": "System Constraints",
        "title": "Architecture & Resource Budget Caps",
        "speaker": "Reshma K",
        "bullets": [
            "Global Budget Constraints: sum(B_i) <= 10.0 MHz and sum(P_i) <= 1.0 W with B_i >= 0, P_i >= 0",
            "Decoupled 6-Stage Pipeline: Scenario Generator -> Channel Model -> Allocators -> Rate Engine -> Validator -> Metrics",
            "Programmed Budget Checks: 100% of 480 simulation evaluations strictly passed tolerance-aware budget assertions",
            "Paired Seed Control: Same random seed (42–51) evaluated across all methods to eliminate channel bias"
        ]
    },
    {
        "category": "Proposed Method",
        "title": "Reliability Aware V2: Feasible-First Allocation",
        "speaker": "M B Gayatri",
        "bullets": [
            "Step 1 (Estimate Need): Inverts rate equation to compute minimum bandwidth needed to achieve Rt",
            "Step 2 (Sort by Feasibility): Prioritizes users requiring the least bandwidth to become reliable",
            "Step 3 (Feasible-First): Allocates resources sequentially until budgets are exhausted; prunes unserviceable users",
            "Step 4 (Surplus Reallocation): Greedily assigns leftover spectrum chunks to maximize aggregate sum-rate",
            "Comparison: Shifts from blind symmetric splitting (Equal) to target-aware threshold optimization"
        ]
    },
    {
        "category": "Experimental Setup",
        "title": "480-Run Factorial Simulation Matrix",
        "speaker": "M B Gayatri",
        "bullets": [
            "User Populations: 5, 10, 20, 50 users (evaluating light traffic to severe congestion)",
            "Target Data Rates: 0.5, 1.0, 2.0 Mbps per user",
            "Evaluated Strategies: Equal Allocation, Greedy Allocation, Proportional Fair, Reliability Aware V2",
            "Statistical Sampling: 10 paired seeds (42–51) = 4 * 3 * 10 * 4 = 480 total simulation runs",
            "Evaluation Metrics: Total Throughput (Mbps), Reliability (%), Minimum Rate (Mbps), Jain Fairness Index"
        ]
    },
    {
        "category": "Benchmark Evaluation",
        "title": "Benchmark Results: 10 Users, 1.0 Mbps Target",
        "speaker": "Prakruthi HR",
        "bullets": [
            "Throughput: Equal = 24.722 Mbps vs V2 = 25.353 Mbps (+0.631 Mbps / +2.6% increase)",
            "Reliability (% Meeting Target): Equal = 67.0% vs V2 = 77.0% (+10.0 percentage point gain)",
            "Jain Fairness: Equal = 0.570 vs V2 = 0.274 (-0.296 drop in rate equality)",
            "Key Insight: V2 satisfies 10% more users while maintaining sum-rate, but intentionally trades away rate uniformity"
        ]
    },
    {
        "category": "Empirical Evidence",
        "title": "Scenario-Wide Matrix: The 4x3 Heatmap",
        "speaker": "Prakruthi HR",
        "bullets": [
            "Reliability Improved in 8/12 Scenarios: Consistent gains across congested regimes (10, 20, 50 users)",
            "Peak Observed Advantage: +25.8 percentage points at 50 users and 1.0 Mbps target rate",
            "Where V2 Decreased (3 Scenarios): Strictly at 5 users (-4 to -6 pp), where Equal already achieved ~100% reliability",
            "The Universal Trade-Off: V2 had lower Jain fairness than Equal Allocation in all 12 scenarios",
            "Engineering Takeaway: Target-aware allocation excels under spectral congestion, but is unnecessary under light loads"
        ]
    },
    {
        "category": "Statistical Rigor",
        "title": "Bootstrap Uncertainty & Academic Boundaries",
        "speaker": "Prakruthi HR",
        "bullets": [
            "20,000 Paired Bootstrap Resamples: 95% CIs at 20 & 50 users strictly exclude zero ([+12.5, +31.0 pp] and [+15.6, +34.6 pp])",
            "Statistical Honesty: At 10 users (1 Mbps), 95% CI [-8.0, +23.0 pp] crosses zero due to 10-seed variance",
            "Model Boundaries: Shannon capacity abstraction; not link-level 3GPP NR PHY, no Doppler or HARQ retransmissions",
            "Proportional Fair Audit Note: PF outputs matched Equal across several seeds, noted for code audit",
            "Agent Layer: Automated LLM tests hit API rate limits; current findings test deterministic heuristics"
        ]
    },
    {
        "category": "Conclusion & Viva Summary",
        "title": "Conclusion & Project Deliverables",
        "speaker": "Vaishnavi R",
        "bullets": [
            "Core Conclusion: V2 successfully improves reliability in 8/12 scenarios, but represents a reliability-fairness trade-off",
            "Deliverables: Live interactive simulator on Netlify • Complete GitHub repository • 480-run reproducible dataset",
            "Foundational Grounding: Kelly (1998), Jain (1984), Shams (2014), Yaacoub (2012), Shannon (1948), Efron (1993)",
            "Thank You! We welcome questions and viva examination."
        ]
    }
]

def main():
    build_pptx(
        filename="ComAgent_Executive_10_Slides.pptx",
        deck_title="COMAGENT EXECUTIVE DECK",
        subtitle="10-Slide Fast-Track Review",
        slides_data=executive_slides,
        accent_color="38BDF8"
    )

if __name__ == "__main__":
    main()
