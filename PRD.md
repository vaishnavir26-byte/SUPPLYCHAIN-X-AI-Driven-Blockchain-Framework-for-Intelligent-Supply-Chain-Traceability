<USER_REQUEST>
# Product Requirements Document (PRD)

## Project Title
**AI and Blockchain-Based Supply Chain Traceability, Verification and Risk Prediction**

**Version:** 1.0  
**Project Type:** Web-Based Application Prototype  
**Blockchain:** Simulated Permissioned Blockchain (Future Hyperledger Fabric Integration)  
**AI Technology:** Machine Learning-Based Risk Prediction  
**Document Storage:** IPFS Architecture  
**Hardware Requirement:** None — No IoT

---

## 1. Project Overview

The project aims to develop a secure, transparent and intelligent supply chain management system using Artificial Intelligence (AI) and Blockchain technology.

The application provides end-to-end product traceability, secure transaction recording, digital signature verification, multi-party authorization, document integrity verification and AI-based supply chain risk prediction.

The initial version will implement a simulated permissioned blockchain. The architecture will be designed for future integration with Hyperledger Fabric.

The system will allow multiple organizations to participate in the supply chain while maintaining a shared, tamper-evident transaction history.

## 2. Problem Statement

Traditional supply chain systems face several challenges:

- Lack of transparency in product movement.
- Difficulty verifying product origin and authenticity.
- Unauthorized modifications to supply chain records.
- Limited coordination between supply chain participants.
- Risk of counterfeit products and fraudulent documentation.
- Difficulty detecting delays and supplier-related risks.
- Lack of reliable document integrity verification.

A secure and intelligent digital platform is required to address these problems.

## 3. Project Objectives

1. Develop a blockchain-based product traceability system.
2. Maintain a tamper-evident supply chain transaction history.
3. Implement smart contract-based business operations.
4. Provide digital signature-based identity verification.
5. Enable multi-party verification and authorization.
6. Integrate IPFS-based document storage architecture.
7. Implement Merkle tree-based document integrity verification.
8. Demonstrate Raft consensus through a simulated ordering network.
9. Predict supply chain risks using AI and machine learning.
10. Provide an interactive web-based dashboard.

## 4. Scope of the Project

### Included

- Product registration and batch management.
- Supply chain ownership tracking.
- Permissioned organization access.
- Smart contract simulation.
- Digital signature simulation.
- Multi-party approval workflows.
- Blockchain transaction explorer.
- IPFS integration design.
- Document hash verification.
- Merkle tree generation and verification.
- Raft consensus simulation.
- AI risk scoring and prediction.
- Audit trail and reporting dashboard.
- Future Hyperledger Fabric integration.

### Excluded

- IoT sensors.
- Arduino and ESP32.
- GPS tracking hardware.
- RFID and NFC hardware.
- Automatic sensor-based data collection.
- Physical transportation monitoring devices.

All supply chain information will be entered manually or through authorized software interfaces.

## 5. Target Users and Roles

| User | Responsibilities |
|---|---|
| Farmer | Register products and provide origin information |
| Manufacturer | Verify product details and process ownership transfers |
| Distributor | Manage distribution and shipment records |
| Retailer | Verify received products and update inventory |
| Regulator | Verify records and authorize critical operations |
| Administrator | Manage organizations, permissions and system configuration |

Each organization will have a separate digital identity.

## 6. Functional Requirements

### FR-01: User Authentication and Organization Management

- Users must access the system through authenticated accounts.
- Each user must belong to an authorized organization.
- Different roles must have different permissions.
- The system must maintain an identity and activity history.
- Future implementation must use Hyperledger Fabric Certificate Authority and X.509 identities.

### FR-02: Product Registration

The system must allow authorized farmers to register products.

Product information includes:

- Product ID.
- Product name.
- Batch ID.
- Origin.
- Quantity.
- Registration date.
- Current owner.
- Product status.

Every successful registration must generate a blockchain transaction.

### FR-03: Product Traceability

The application must track:

- Product registration.
- Manufacturer processing.
- Distributor ownership.
- Retailer receipt.
- Product verification.
- Complete transaction history.

Users must be able to search using a product ID or batch ID.

### FR-04: Smart Contract Management

Smart contracts will control supply chain operations.

Required functions:

| Smart Contract | Purpose |
|---|---|
| RegisterProduct | Register a new product |
| ReadProduct | Retrieve product information |
| UpdateProductStage | Update supply chain stage |
| ProposeTransfer | Propose ownership transfer |
| ApproveTransfer | Approve ownership transfer |
| FinalizeTransfer | Complete authorized transfer |
| VerifyProduct | Verify product authenticity |
| StoreDocumentHash | Record document hash |
| VerifyDocument | Verify document integrity |
| SubmitMerkleRoot | Store Merkle root |
| VerifyMerkleProof | Verify document inclusion |
| GetTransactionHistory | Retrieve audit history |
| ReportRisk | Record AI risk assessment |

**Future implementation:** Hyperledger Fabric Go chaincode.

### FR-05: Digital Signature Verification

- Each organization must have a digital identity.
- Transactions must be associated with the submitting organization.
- Digital signatures must verify transaction authenticity.
- Unauthorized users must not be allowed to perform restricted operations.
- Future implementation must use X.509 certificates, private keys and MSP identity validation.

### FR-06: Multi-Party Verification

Ownership transfers and sensitive operations must require authorized approvals.

Example workflow:

1. Farmer registers a product.
2. Farmer proposes a transfer to the manufacturer.
3. Manufacturer approves the transfer.
4. Regulator provides the required verification.
5. Smart contract validates the approvals.
6. Ownership is updated.
7. The transaction is recorded on the blockchain.

Approval policies must be configurable according to the operation.

### FR-07: IPFS Document Storage

The system must support document management for:

- Product certificates.
- Quality inspection reports.
- Purchase invoices.
- Delivery documents.
- Regulatory approvals.

Document workflow:

1. Authorized user selects a document.
2. The system calculates its cryptographic hash.
3. The document is stored in IPFS in the full implementation.
4. Its Content Identifier (CID) and hash are recorded on the blockchain.
5. Users can retrieve and verify the document.

Sensitive documents must be encrypted before storage.

### FR-08: Merkle Tree Verification

The system must generate a Merkle tree from multiple document hashes.

Requirements:

- Generate leaf hashes.
- Calculate parent hashes.
- Generate the Merkle root.
- Store the Merkle root on the blockchain.
- Generate Merkle inclusion proofs.
- Verify document membership and integrity.

This feature will provide efficient batch verification.

### FR-09: Raft Consensus

The architecture will use a three-node Raft ordering service design.

Requirements:

- Demonstrate leader and follower nodes.
- Simulate transaction ordering.
- Demonstrate quorum-based commitment.
- Simulate node failure and recovery.
- Display network availability.

For three orderers, two nodes are required to maintain quorum.

Raft provides crash-fault tolerance, not Byzantine-fault tolerance.

### FR-10: AI-Based Risk Prediction

The system must analyze supply chain information and calculate risk scores.

Input features:

- Supplier reliability.
- Historical delivery delays.
- Product rejection rate.
- Document verification failures.
- Transaction irregularities.

Proposed algorithms:

- Random Forest.
- XGBoost.
- Isolation Forest.

Risk classification:

| Risk Score | Classification |
|---|---|
| 0–39% | Low |
| 40–69% | Medium |
| 70–100% | High |

The AI module must provide:

- Risk score.
- Risk classification.
- Contributing factors.
- Prediction timestamp.
- Model version.

Risk predictions must be recorded with their relevant input snapshot hash on the blockchain.

AI predictions are decision-support assessments, not proof of fraud.

## 7. User Interface Requirements

The application must provide the following screens:

### Screen 1: Main Dashboard

- Total products.
- Total blockchain transactions.
- Verified products.
- Pending approvals.
- Network status.
- AI risk summary.
- Recent activities.

### Screen 2: Product Management

- Product registration form.
- Product search.
- Batch information.
- Ownership information.
- Product status.
- Traceability history.

### Screen 3: Blockchain Explorer

- Block number.
- Block hash.
- Previous block hash.
- Transaction ID.
- Transaction timestamp.
- Organization identity.
- Digital signature status.

### Screen 4: Multi-Party Verification

- Transfer requests.
- Approval status.
- Organization approvals.
- Transfer completion.
- Rejected transactions.

### Screen 5: Document Verification

- Document upload.
- IPFS CID.
- SHA-256 hash.
- Verification status.
- Tampering detection.
- Merkle root.

### Screen 6: AI Risk Dashboard

- Risk score.
- Risk classification.
- Supplier reliability.
- Delay analysis.
- Rejection rate.
- Risk prediction history.

### Screen 7: Network Management

- Organization information.
- Peer status.
- Orderer status.
- Raft leader and followers.
- Quorum availability.

## 8. System Architecture

The proposed architecture consists of five major layers.

**Layer 1 — Presentation Layer**
- React.js frontend.
- Dashboard.
- Product management.
- Verification interface.
- AI analytics interface.

**Layer 2 — Application Layer**
- Python FastAPI backend.
- Authentication and authorization.
- Business logic.
- API communication.

**Layer 3 — Blockchain Layer**
- Simulated permissioned ledger initially.
- Smart contracts.
- Digital signatures.
- Multi-party endorsement.
- Simulated Raft consensus.
- Future Hyperledger Fabric peers and orderers.

**Layer 4 — Storage Layer**
- IPFS document storage.
- SHA-256 hashes.
- Merkle trees.
- MongoDB application metadata.

**Layer 5 — Artificial Intelligence Layer**
- Python machine learning.
- Random Forest and XGBoost.
- Risk scoring.
- Anomaly detection.
- Prediction history.

## 9. Technology Stack

| Component | Proposed Technology |
|---|---|
| Frontend | React.js |
| UI Styling | Tailwind CSS |
| Backend | Python FastAPI |
| Blockchain | Hyperledger Fabric |
| Smart Contracts | Go Chaincode |
| Identity | Fabric CA and X.509 |
| Consensus | Raft |
| Document Storage | IPFS |
| Hashing | SHA-256 |
| Merkle Tree | Python |
| AI/ML | Scikit-learn, XGBoost |
| Database | MongoDB |
| Containerization | Docker |

The first prototype will simulate blockchain and consensus behavior. Live integrations will be added in later development stages.

## 10. Non-Functional Requirements

### Security
- Role-based access control.
- Digital identity verification.
- Encrypted sensitive documents.
- Secure private key management.
- Transaction authorization.

### Performance
- Responsive dashboard.
- Efficient product searches.
- Fast transaction history retrieval.
- Efficient document integrity checks.

### Reliability
- Persistent application data.
- Blockchain transaction validation.
- Network failure simulation.
- Error handling and audit logging.

### Usability
- Simple navigation.
- Clear status indicators.
- Responsive design.
- Easy-to-understand risk reports.

### Scalability
- Support multiple organizations.
- Support increasing product batches.
- Allow future Fabric network expansion.

## 11. Database and Data Management

Proposed entities:

| Entity | Important Fields |
|---|---|
| Users | User ID, role, organization |
| Organizations | Organization ID, MSP ID |
| Products | Product ID, batch ID, owner |
| Transactions | Transaction ID, type, hash |
| Approvals | Request ID, approver, status |
| Documents | CID, document hash, metadata |
| Merkle Records | Root hash, proof, timestamp |
| Risk Records | Score, classification, model version |
| Network Nodes | Node ID, status, role |

The blockchain will be the source of truth for critical traceability records in the full implementation.

## 12. Expected Project Workflow

1. Farmer logs into the application.
2. Farmer registers a product.
3. Product registration is recorded on the blockchain.
4. Manufacturer requests ownership transfer.
5. Authorized organizations approve the transfer.
6. Smart contract validates approvals.
7. Product ownership is updated.
8. Product documents are stored through IPFS.
9. Document hashes are verified using Merkle trees.
10. AI analyzes supply chain history.
11. Risk prediction is generated.
12. Prediction and relevant metadata are recorded on the blockchain.
13. Retailer or regulator verifies the complete product history.

## 13. Testing Requirements

The project must undergo the following tests:

- Product registration validation.
- Unauthorized access testing.
- Digital signature verification testing.
- Duplicate transaction testing.
- Multi-party approval testing.
- Ownership transfer testing.
- Document tampering detection.
- Merkle root and proof verification.
- Raft quorum failure simulation.
- AI prediction testing.
- Blockchain transaction history validation.

## 14. Expected Outcomes

The completed application should demonstrate:

- Transparent supply chain tracking.
- Tamper-evident product records.
- Secure organization-level transactions.
- Multi-party verification.
- Document authenticity checking.
- Efficient Merkle-based integrity verification.
- Consensus and network failure demonstration.
- AI-based supply chain risk prediction.
- A scalable architecture for future Hyperledger Fabric deployment.

## 15. Development Timeline

| Phase | Development Activity |
|---|---|
| Phase 1 | Requirement analysis and UI design |
| Phase 2 | Frontend dashboard development |
| Phase 3 | Backend API development |
| Phase 4 | Simulated blockchain and smart contracts |
| Phase 5 | Digital identity and approval workflows |
| Phase 6 | IPFS and Merkle tree integration |
| Phase 7 | Raft consensus simulation |
| Phase 8 | AI risk prediction |
| Phase 9 | Testing and integration |
| Phase 10 | Hyperledger Fabric integration design and deployment |

## 16. Project Success Criteria

The project will be considered successful when:

1. Products can be registered and traced.
2. Transactions are recorded with linked block hashes.
3. Organization-level permissions are enforced.
4. Transfers require the configured approvals.
5. Document changes can be detected.
6. Merkle roots and inclusion proofs can be verified.
7. Raft quorum behavior can be demonstrated.
8. AI risk scores can be generated and explained.
9. The dashboard displays all major system operations.
10. The architecture supports migration to a real Hyperledger Fabric network.

## 17. Future Enhancements

- Full Hyperledger Fabric deployment.
- Production-grade cryptographic signatures.
- Actual IPFS network integration.
- Trained machine learning models using real supply chain datasets.
- Advanced fraud and anomaly detection.
- QR-code-based product verification.
- Advanced analytics and reporting.
- Mobile-friendly application.

---

## Final Project Definition

The proposed project is a software-based, AI-powered supply chain traceability platform that uses a permissioned blockchain architecture to secure product information, verify transactions, manage multi-party approvals, validate documents and predict supply chain risks.

**The central innovation is the integration of blockchain-based trust and verification with AI-based risk intelligence, without requiring any IoT hardware.**
</USER_REQUEST>
<ADDITIONAL_METADATA>
The current local time is: 2026-11-10T11:35:36+05:30.
</ADDITIONAL_METADATA>
<USER_SETTINGS_CHANGE>
The user changed setting `Model Selection` from None to Gemini 3.8 Flash (High). No need to comment on this change if the user doesn't ask about it. If reporting what model you are, please use a human readable name instead of the exact string.
</USER_SETTINGS_CHANGE>