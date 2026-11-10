"""
Supply Chain Risk Synthetic Dataset Generator (PRD FR-10).
Generates realistic multi-factor supply chain training records:
- Supplier Reliability Index (0-100)
- Historical Delivery Delays (days)
- Product Rejection Rate (%)
- Document Verification Failures (count)
- Transaction Irregularities Anomaly Score (0-100)
- Ground Truth Risk Classification: Low, Medium, High
"""

import os
import csv
import random
import time
from typing import List, Dict, Any


def generate_synthetic_dataset(num_records: int = 1500, seed: int = 42) -> List[Dict[str, Any]]:
    random.seed(seed)
    records = []

    commodities = ["Durum Wheat", "Arabica Coffee", "Basmati Rice", "Soybean Oil", "Organic Cotton", "Raw Cane Sugar"]
    suppliers = ["FarmerOrgMSP", "AgriCoop-North", "HighlandGrowers", "DeltaFarms", "SunValleyEstates", "GlobalGrainConsortium"]

    for i in range(1, num_records + 1):
        # 3 Archetypes: 60% Low Risk, 25% Medium Risk, 15% High Risk
        scenario = random.choices(["LOW", "MEDIUM", "HIGH"], weights=[0.60, 0.25, 0.15])[0]

        if scenario == "LOW":
            rel = round(random.uniform(75.0, 99.0), 1)
            delays = round(random.expovariate(1.0 / 1.5), 1)
            delays = min(5.0, delays)
            rejection = round(random.uniform(0.1, 4.0), 2)
            doc_fails = 0 if random.random() > 0.1 else 1
            irreg = round(random.uniform(1.0, 15.0), 1)

        elif scenario == "MEDIUM":
            rel = round(random.uniform(50.0, 75.0), 1)
            delays = round(random.uniform(4.0, 14.0), 1)
            rejection = round(random.uniform(4.0, 12.0), 2)
            doc_fails = random.choice([0, 1, 2])
            irreg = round(random.uniform(15.0, 45.0), 1)

        else: # HIGH
            rel = round(random.uniform(15.0, 50.0), 1)
            delays = round(random.uniform(12.0, 30.0), 1)
            rejection = round(random.uniform(12.0, 48.0), 2)
            doc_fails = random.choice([2, 3, 4, 5])
            irreg = round(random.uniform(45.0, 95.0), 1)

        # Baseline weighted calculation for ground truth
        w_rel = ((100.0 - rel) / 100.0) * 30.0
        w_delay = min(1.0, delays / 30.0) * 25.0
        w_rej = min(1.0, rejection / 50.0) * 20.0
        w_doc = (doc_fails / 5.0) * 15.0
        w_irreg = (irreg / 100.0) * 10.0
        calculated_score = round(min(100.0, max(0.0, w_rel + w_delay + w_rej + w_doc + w_irreg)), 1)

        if calculated_score < 40.0:
            classification = "Low"
            class_code = 0
        elif calculated_score < 70.0:
            classification = "Medium"
            class_code = 1
        else:
            classification = "High"
            class_code = 2

        records.append({
            "record_id": f"REC-{i:05d}",
            "commodity": random.choice(commodities),
            "supplier_msp": random.choice(suppliers),
            "supplier_reliability": rel,
            "historical_delays": delays,
            "rejection_rate": rejection,
            "doc_verification_failures": doc_fails,
            "tx_irregularities": irreg,
            "ground_truth_score": calculated_score,
            "classification": classification,
            "class_code": class_code
        })

    return records


def export_dataset_to_csv(records: List[Dict[str, Any]], output_path: str):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    if not records:
        return
    fieldnames = list(records[0].keys())
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)


if __name__ == "__main__":
    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
    out_file = os.path.join(out_dir, "supply_chain_risk_dataset.csv")
    recs = generate_synthetic_dataset(1500)
    export_dataset_to_csv(recs, out_file)
    print(f"Generated {len(recs)} synthetic supply chain records saved to: {out_file}")
