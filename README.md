# SUPPLYCHAIN-X — AI-Driven Blockchain Framework for Intelligent Supply Chain Traceability, Verification & Risk Prediction

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://python.org)
[![Blockchain](https://img.shields.io/badge/Blockchain-Permissioned%20Simulated%20%2F%20Fabric-purple.svg)](https://hyperledger-fabric.readthedocs.io/)
[![Consensus](https://img.shields.io/badge/Consensus-Raft%20CFT%20(3--Node)-orange.svg)](https://raft.github.io/)
[![Machine Learning](https://img.shields.io/badge/AI-Random%20Forest%20%2B%20Isolation%20Forest-emerald.svg)](https://scikit-learn.org/)
[![Storage](https://img.shields.io/badge/Document%20Storage-IPFS%20Architecture-cyan.svg)](https://ipfs.tech/)
[![Tailwind CSS](https://img.shields.io/badge/TailwindCSS-3.4-38bdf8.svg)](https://tailwindcss.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Live Demo](https://img.shields.io/badge/Live%20Demo-Available%20Now-success.svg)](https://5a69d615963104.lhr.life)

> 🚀 **Live Interactive Demo:** [https://5a69d615963104.lhr.life](https://5a69d615963104.lhr.life)  
> 📦 **GitHub Repository:** [https://github.com/vaishnavir26-byte/SUPPLYCHAIN-X-AI-Driven-Blockchain-Framework-for-Intelligent-Supply-Chain-Traceability](https://github.com/vaishnavir26-byte/SUPPLYCHAIN-X-AI-Driven-Blockchain-Framework-for-Intelligent-Supply-Chain-Traceability)

---

## 1. Executive Summary

**SUPPLYCHAIN-X** is an enterprise-grade prototype integrating **Artificial Intelligence (AI)** and **Permissioned Blockchain Technology** to provide end-to-end supply chain traceability, multi-party authorization, cryptographic document verification, and proactive disruption risk prediction.

Engineered under a strict **Zero-IoT hardware constraint**, the system eliminates dependency on unreliable RFID/GPS/microcontroller hardware by establishing an incorruptible digital chain of custody powered by **digital signatures**, **Merkle trees**, **IPFS content addressing**, **3-Node Raft ordering consensus**, and **machine-learning risk scoring**.

---

## 2. System Architecture

The architecture is structured across five decoupled layers ensuring high modularity, high performance, and seamless future deployment to **Hyperledger Fabric**.

```
┌────────────────────────────────────────────────────────────────────────┐
│                      Layer 1: Presentation Layer                       │
│    Interactive Web Dashboard (Tailwind CSS, Chart.js, Lucide Icons)    │
│    7 Core Screens: KPI Telemetry, Batch Journey, Explorer, AI Radar    │
└────────────────────────────────────┬───────────────────────────────────┘
                                     │ HTTP / REST / JSON
┌────────────────────────────────────▼───────────────────────────────────┐
│                      Layer 2: Application Layer                        │
│    Python Server & REST API Dispatcher (Multithreaded Stdlib / FastAPI)│
│    Session Auth, Digital Signature Verifier, Payload Serializer        │
└────────────────────────────────────┬───────────────────────────────────┘
                                     │ Internal Dispatch
┌────────────────────────────────────▼───────────────────────────────────┐
│                     Layer 3: Smart Contract Layer                      │
│    13 PRD Chaincode Methods (Go Fabric Chaincode & Python Engine)      │
│    Register, Propose, Multi-Party Approve, Merkle Verify, Report Risk  │
└──────────────────┬─────────────────┴───────────────────┬───────────────┘
                   │                                     │
┌──────────────────▼──────────────────┐ ┌────────────────▼───────────────┐
│     Layer 4: Blockchain & Storage   │ │      Layer 5: AI Analytics      │
│  • Simulated Permissioned Ledger    │ │  • Random Forest (97.3% Acc)   │
│  • 3-Node Raft Consensus (CFT)      │ │  • Isolation Forest Anomaly     │
│  • IPFS Content Identifier (CIDv1)  │ │  • 5 Supply Chain Input Factors │
│  • O(log N) Merkle Inclusion Proofs │ │  • Snapshot Hash Anchor         │
│  • SQLite Audit Ledger (9 Entities) │ │  • 3-Tier Risk (Low/Med/High)   │
└─────────────────────────────────────┘ └───────────────────────────────┘
```

---

## 3. Key Functional Modules

### 🌿 FR-01 to FR-03: Product Traceability & Batch Management
- **Lifecycle Tracking:** Registers batches with origin coordinates, harvesting metadata, and stage tracking (*Harvested $\rightarrow$ Processing $\rightarrow$ Packaged $\rightarrow$ In Transit $\rightarrow$ Received $\rightarrow$ Retail Stocked*).
- **Search & Verification:** Real-time lookup by Product ID or Batch ID with cryptographic proof of authenticity.
- **Batch Passport QR:** Generates on-demand cryptographic QR tokens for audits.

### 📜 FR-04: 13 Smart Contract Methods
Implements all 13 required business operations in both Python and production-ready **Hyperledger Fabric Go chaincode** (`fabric/chaincode/supplychain.go`):

| Smart Contract Method | Purpose |
|---|---|
| `RegisterProduct` | Mints a new product batch with origin and ownership |
| `ReadProduct` | Queries current stage, owner, and verification status |
| `UpdateProductStage` | Advances product through supply chain milestones |
| `ProposeTransfer` | Initiates multi-party ownership transfer workflow |
| `ApproveTransfer` | Collects required signatures from authorized parties |
| `FinalizeTransfer` | Validates quorum endorsement and executes transfer |
| `VerifyProduct` | Cryptographically validates authenticity & origin |
| `StoreDocumentHash` | Records SHA-256 digest and IPFS CID on ledger |
| `VerifyDocument` | Detects zero-byte tampering against on-chain hash |
| `SubmitMerkleRoot` | Anchors batch Merkle root to the blockchain |
| `VerifyMerkleProof` | Audits document inclusion in $\mathcal{O}(\log N)$ time |
| `GetTransactionHistory` | Retrieves immutable audit trail for any batch |
| `ReportRisk` | Anchors AI risk score and snapshot hash to ledger |

### 🔐 FR-05 & FR-06: Digital Signatures & Multi-Party Verification
- **X.509 MSP Simulation:** Organizations (*FarmerOrg, ManufacturerOrg, DistributorOrg, RetailerOrg, RegulatorOrg*) have individual cryptographic keypairs.
- **Strict Role-Based Endorsement:** Transfers require multi-stakeholder consensus (e.g., Farmer proposal + Manufacturer acceptance + Regulator compliance endorsement).

### 🗄️ FR-07 & FR-08: IPFS Storage & Merkle Tree Verification
- **Decentralized Storage:** Calculates deterministic SHA-256 digests and base32 CIDv1 identifiers.
- **Merkle Batch Verification:** Constructs balanced binary trees from document batches, stores the 32-byte Merkle root on-chain, and produces audit paths verified in $\mathcal{O}(\log N)$ operations.

### 🗳️ FR-09: 3-Node Raft Consensus Engine
- **Crash-Fault Tolerant (CFT):** 3-node cluster (`orderer1`, `orderer2`, `orderer3`) with leader election, heartbeat mechanism, and strict quorum checking ($\lfloor 3/2 \rfloor + 1 = 2$).
- **Live Failure Simulation:** UI allows killing leader or follower nodes to witness instantaneous re-election and quorum enforcement.

### 🧠 FR-10: AI Supply Chain Risk Engine
- **Multi-Factor Scoring:** Evaluates 5 key risk vectors:
  1. Supplier Reliability Score (0–100%)
  2. Historical Delivery Delay (Days)
  3. Batch Rejection Rate (0–100%)
  4. Document Verification Failure Count
  5. Transaction Irregularity Index (0–100)
- **Trained ML Models:** Decision Tree & Random Forest classifiers trained on 1,500 historical supply chain records.
- **Model Performance:** **97.33% Test Accuracy**, **86.51% Macro F1 Score**.
- **Cryptographic Anchoring:** Computes a SHA-256 snapshot hash of all inputs and commits the prediction permanently to the ledger.

---

## 4. Web Dashboard (7 Interactive Screens)

1. **Main Dashboard:** Live KPI telemetry, Batch Lifecycle Stages Donut Chart, and Raft Consensus Throughput Timeline.
2. **Product Management:** Interactive batch registration, 6-stage horizontal journey map, and QR batch passport.
3. **Blockchain Explorer:** Cryptographic block ribbon linking block headers (`#0`, `#1`, ...), parent hashes, and transaction payloads.
4. **Multi-Party Verification:** Live proposal and multi-signature authorization queue.
5. **Document Verification:** Upload simulator, zero-byte tamper detection, and hierarchical SVG Merkle Tree visualizer.
6. **AI Risk Dashboard:** Real-time risk sliders, 5-Axis Spider Radar Chart, and ML Confusion Matrix heatmap.
7. **Network Management:** Triangular 3-Node Raft topology diagram with live pulsing heartbeats and quorum gauges.

---

## 5. Quickstart & Installation

### Prerequisites
- Python 3.10+
- Modern Web Browser (Chrome, Firefox, Safari, Edge)

### Run the Application

```bash
# Clone the repository
git clone https://github.com/vaishnavir26-byte/SUPPLYCHAIN-X-AI-Driven-Blockchain-Framework-for-Intelligent-Supply-Chain-Traceability.git
cd SUPPLYCHAIN-X-AI-Driven-Blockchain-Framework-for-Intelligent-Supply-Chain-Traceability

# Launch the server (Zero external dependencies needed - uses Python standard library)
python3 run_supply_chain.py --port 8000
```

Open your browser at **`http://localhost:8000`** or open **`index.html`** directly.

### Run Comprehensive Test Suite

```bash
python3 run_supply_chain.py --test
```
All **14 unit and integration test suites** pass in ~0.003s:
```
test_01_crypto_identity_and_signing ... ok
test_02_blockchain_genesis_and_block_minting ... ok
test_03_blockchain_tamper_detection ... ok
test_04_raft_consensus_and_quorum ... ok
test_05_raft_leader_failure_and_re_election ... ok
test_06_smart_contract_register_and_read ... ok
test_07_smart_contract_lifecycle_stages ... ok
test_08_smart_contract_multi_party_transfer ... ok
test_09_ipfs_storage_and_tamper_detection ... ok
test_10_merkle_tree_proof_generation_and_verification ... ok
test_11_ai_risk_engine_scoring_tiers ... ok
test_12_ai_risk_snapshot_hash_anchoring ... ok
test_13_sqlite_database_audit_trail ... ok
test_14_end_to_end_supply_chain_pipeline ... ok
----------------------------------------------------------------------
Ran 14 tests in 0.003s (OK)
```

---

## 6. Hyperledger Fabric Deployment Ready

The project includes production-ready deployment configurations in `fabric/`:
- **`fabric/chaincode/supplychain.go`**: Official Fabric contract-api Go chaincode.
- **`fabric/network/configtx.yaml`**: Complete channel and Raft orderer configuration.
- **`fabric/network/docker-compose.yaml`**: Multi-peer, multi-orderer network setup.

---

## 7. License

Distributed under the MIT License. See `LICENSE` for details.
