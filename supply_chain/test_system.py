"""
Comprehensive System Test Suite.
Verifies all 11 testing requirements specified in PRD Section 13:
1.  Product registration validation
2.  Unauthorized access testing
3.  Digital signature verification testing
4.  Duplicate transaction / ID testing
5.  Multi-party approval testing
6.  Ownership transfer testing
7.  Document tampering detection
8.  Merkle root and inclusion proof verification
9.  Raft quorum failure simulation (crash fault tolerance)
10. AI prediction scoring & classification testing
11. Blockchain transaction history and cryptographic chain validation
"""

import unittest
import time
from supply_chain.core.crypto_identity import sign_payload, verify_signature, ORGANIZATIONS
from supply_chain.core.merkle import MerkleTree
from supply_chain.core.ipfs_storage import IPFSStorage, compute_sha256
from supply_chain.core.raft import RaftConsensusCluster
from supply_chain.core.blockchain import BlockchainLedger, Transaction
from supply_chain.core.ai_risk_engine import AIRiskEngine
from supply_chain.core.smart_contracts import SmartContractEngine


class TestSupplyChainBlockchainAI(unittest.TestCase):

    def setUp(self):
        self.ledger = BlockchainLedger()
        self.raft = RaftConsensusCluster()
        self.engine = SmartContractEngine(self.ledger, self.raft)
        self.storage = IPFSStorage("/tmp/test_ipfs_repo")

    # 1. Product Registration Validation (FR-02)
    def test_01_product_registration(self):
        p_id = f"PROD-TEST-{int(time.time())}"
        res = self.engine.register_product(
            product_id=p_id,
            name="Organic Soybeans",
            batch_id="BATCH-SOY-01",
            origin="Iowa Farm Sector B",
            quantity="100 MT",
            sender_msp="FarmerOrgMSP"
        )
        self.assertTrue(res["success"])
        self.assertEqual(res["product"]["product_id"], p_id)
        self.assertEqual(res["product"]["current_owner"], "FarmerOrgMSP")
        self.assertEqual(res["product"]["stage"], "HARVESTED")
        self.assertGreaterEqual(res["receipt"]["block_number"], 1)

    # 2. Unauthorized Access Testing (FR-01, FR-04)
    def test_02_unauthorized_access(self):
        # A retailer cannot register agricultural harvest
        with self.assertRaises(PermissionError):
            self.engine.register_product(
                product_id="PROD-ILLEGAL-01",
                name="Fake Registration",
                batch_id="BATCH-00",
                origin="Nowhere",
                quantity="1 Unit",
                sender_msp="RetailerOrgMSP"
            )

    # 3. Digital Signature Verification Testing (FR-05)
    def test_03_digital_signatures(self):
        data = {"tx_id": "TX-TEST-01", "action": "Transfer", "amount": 500}
        sig = sign_payload("FarmerOrgMSP", data)
        self.assertTrue(verify_signature("FarmerOrgMSP", data, sig))

        # Tampering with payload fails signature verification
        tampered_data = {"tx_id": "TX-TEST-01", "action": "Transfer", "amount": 999999}
        self.assertFalse(verify_signature("FarmerOrgMSP", tampered_data, sig))

        # Verifying with wrong MSP fails
        self.assertFalse(verify_signature("DistributorOrgMSP", data, sig))

    # 4. Duplicate Transaction / ID Testing
    def test_04_duplicate_registration_prevented(self):
        p_id = "PROD-UNIQUE-99"
        self.engine.register_product(
            product_id=p_id,
            name="Barley",
            batch_id="B-1",
            origin="North Dakota",
            quantity="10 MT",
            sender_msp="FarmerOrgMSP"
        )
        with self.assertRaises(ValueError):
            self.engine.register_product(
                product_id=p_id,
                name="Duplicate Barley",
                batch_id="B-1",
                origin="North Dakota",
                quantity="10 MT",
                sender_msp="FarmerOrgMSP"
            )

    # 5 & 6. Multi-Party Approval & Ownership Transfer Testing (FR-06)
    def test_05_multi_party_transfer_flow(self):
        p_id = f"PROD-TRANSFER-{int(time.time())}"
        self.engine.register_product(
            product_id=p_id,
            name="Organic Cotton",
            batch_id="B-COTTON-55",
            origin="Texas Co-op",
            quantity="50 Bales",
            sender_msp="FarmerOrgMSP"
        )

        # Propose transfer to Manufacturer
        prop_res = self.engine.propose_transfer(
            product_id=p_id,
            recipient_msp="ManufacturerOrgMSP",
            transfer_reason="Spinning mill dispatch",
            sender_msp="FarmerOrgMSP"
        )
        prop_id = prop_res["proposal"]["proposal_id"]

        # Finalizing prematurely must fail (endorsements missing)
        with self.assertRaises(ValueError):
            self.engine.finalize_transfer(prop_id, "FarmerOrgMSP")

        # Step 1: Manufacturer approves
        self.engine.approve_transfer(prop_id, "ManufacturerOrgMSP", "APPROVED")

        # Still missing Regulator endorsement
        with self.assertRaises(ValueError):
            self.engine.finalize_transfer(prop_id, "FarmerOrgMSP")

        # Step 2: Regulator endorses
        self.engine.approve_transfer(prop_id, "RegulatorOrgMSP", "APPROVED")

        # Finalize succeeds!
        fin_res = self.engine.finalize_transfer(prop_id, "FarmerOrgMSP")
        self.assertEqual(fin_res["product"]["current_owner"], "ManufacturerOrgMSP")
        self.assertEqual(fin_res["product"]["stage"], "PROCESSING")

    # 7. Document Tampering Detection (FR-07)
    def test_06_document_tampering_detection(self):
        doc_content = b"Official Phytosanitary Inspection: Grade AAA Pure Organic."
        store_res = self.storage.store_document(
            file_bytes=doc_content,
            file_name="cert.txt",
            doc_type="CERT_OF_ORIGIN",
            uploaded_by_msp="FarmerOrgMSP"
        )
        doc_cid = store_res["cid"]
        doc_hash = store_res["sha256"]

        # Record hash on blockchain
        self.engine.store_document_hash(
            doc_id="DOC-CERT-01",
            doc_type="CERT_OF_ORIGIN",
            sha256_hash=doc_hash,
            ipfs_cid=doc_cid,
            product_id="PROD-ORG-WHEAT-2026",
            sender_msp="FarmerOrgMSP"
        )

        # Authentic verification
        ver_authentic = self.engine.verify_document("DOC-CERT-01", doc_hash)
        self.assertTrue(ver_authentic["verified"])
        self.assertFalse(ver_authentic["tampered"])

        # Tampered verification (1 byte modified)
        tampered_hash = compute_sha256(doc_content + b"X")
        ver_tampered = self.engine.verify_document("DOC-CERT-01", tampered_hash)
        self.assertFalse(ver_tampered["verified"])
        self.assertTrue(ver_tampered["tampered"])

    # 8. Merkle Root and Inclusion Proof Verification (FR-08)
    def test_07_merkle_tree_and_proofs(self):
        leaves = [
            "Doc-Certificate-01",
            "Doc-LabAnalysis-02",
            "Doc-BillOfLading-03",
            "Doc-Insurance-04"
        ]
        tree = MerkleTree(leaves)
        root = tree.root
        self.assertEqual(len(root), 64)

        # Register root on chain
        self.engine.submit_merkle_root("BATCH-MERKLE-01", root, len(leaves), "FarmerOrgMSP")

        # Generate proof for leaf index 1
        leaf_1_hash = tree.leaf_hashes[1]
        proof_1 = tree.get_proof(1)

        # Verification of authentic proof succeeds
        res_valid = self.engine.verify_merkle_proof("BATCH-MERKLE-01", leaf_1_hash, proof_1)
        self.assertTrue(res_valid["verified"])

        # Verification with tampered leaf fails
        tampered_leaf = compute_sha256(b"Tampered-Doc-Content")
        res_invalid = self.engine.verify_merkle_proof("BATCH-MERKLE-01", tampered_leaf, proof_1)
        self.assertFalse(res_invalid["verified"])

    # 9. Raft Quorum Failure Simulation (FR-09)
    def test_08_raft_quorum_failure(self):
        # Initial: 3 nodes active, quorum = 2
        self.assertTrue(self.raft.has_quorum())

        # Kill node 1: 2 nodes remain -> Quorum OK
        self.raft.set_node_status("orderer1.supplychain.net", False)
        self.assertTrue(self.raft.has_quorum())

        # An ordering transaction still succeeds with 2 nodes
        tx = Transaction("TestTx", "FarmerOrgMSP", {"val": 1})
        res = self.raft.order_and_commit_block([tx.to_dict()])
        self.assertEqual(res["status"], "COMMITTED")

        # Kill node 2: Only 1 node remains -> Quorum LOST
        self.raft.set_node_status("orderer2.supplychain.net", False)
        self.assertFalse(self.raft.has_quorum())

        # An ordering transaction must now HALT with RuntimeError
        with self.assertRaises(RuntimeError):
            self.raft.order_and_commit_block([tx.to_dict()])

        # Revive node 1: Quorum RESTORED
        self.raft.set_node_status("orderer1.supplychain.net", True)
        self.assertTrue(self.raft.has_quorum())

    # 10. AI Prediction Testing (FR-10)
    def test_09_ai_risk_prediction(self):
        # Scenario A: Pristine supplier -> Low Risk
        clean_inputs = {
            "supplier_reliability": 95.0,
            "historical_delays": 0.0,
            "rejection_rate": 0.5,
            "doc_verification_failures": 0.0,
            "tx_irregularities": 5.0
        }
        res_low = AIRiskEngine.evaluate_risk("PROD-TEST-A", clean_inputs)
        self.assertEqual(res_low["classification"], "Low")
        self.assertLess(res_low["risk_score"], 40.0)
        self.assertEqual(len(res_low["snapshot_hash"]), 64)

        # Scenario B: Highly compromised supplier -> High Risk
        risky_inputs = {
            "supplier_reliability": 20.0,
            "historical_delays": 25.0,
            "rejection_rate": 35.0,
            "doc_verification_failures": 4.0,
            "tx_irregularities": 85.0
        }
        res_high = AIRiskEngine.evaluate_risk("PROD-TEST-B", risky_inputs)
        self.assertEqual(res_high["classification"], "High")
        self.assertGreaterEqual(res_high["risk_score"], 70.0)

    # 11. Blockchain Ledger Cryptographic Validation
    def test_10_blockchain_cryptographic_continuity(self):
        # Commit 5 blocks
        for i in range(5):
            tx = Transaction(f"Action-{i}", "FarmerOrgMSP", {"index": i})
            self.raft.order_and_commit_block([tx.to_dict()])
            self.ledger.add_block([tx.to_dict()], "orderer1.supplychain.net")

        integ = self.ledger.verify_chain_integrity()
        self.assertTrue(integ["valid"])
        self.assertGreaterEqual(integ["total_blocks"], 6)

    # 12. Large Merkle Tree Scale Verification (32 Leaves)
    def test_11_large_merkle_tree_32_leaves(self):
        leaves = [f"Certificate-Doc-Hash-Batch-2026-N{i:02d}" for i in range(32)]
        tree = MerkleTree(leaves)
        self.assertEqual(len(tree.leaf_hashes), 32)
        self.assertEqual(tree.levels[0], tree.leaf_hashes)
        self.assertEqual(len(tree.levels), 6) # depth = log2(32) + 1 = 6

        # Register on chain
        self.engine.submit_merkle_root("BATCH-SCALE-32", tree.root, 32, "FarmerOrgMSP")

        # Verify proof for first, middle, and last leaf
        for idx in [0, 15, 31]:
            leaf = tree.leaf_hashes[idx]
            proof = tree.get_proof(idx)
            self.assertEqual(len(proof), 5) # log2(32) = 5 sibling steps
            res = self.engine.verify_merkle_proof("BATCH-SCALE-32", leaf, proof)
            self.assertTrue(res["verified"])

    # 13. Stage Progression State Machine Invariants
    def test_12_stage_progression_invariants(self):
        p_id = f"PROD-STAGE-{int(time.time())}"
        self.engine.register_product(
            product_id=p_id,
            name="Sugar Cane",
            batch_id="B-SUGAR-01",
            origin="Louisiana Delta",
            quantity="500 Bags",
            sender_msp="FarmerOrgMSP"
        )
        # Advance through valid stages
        self.engine.update_product_stage(p_id, "PROCESSING", "Mill Site 2", "Crushed", "FarmerOrgMSP")
        prod = self.engine.read_product(p_id)
        self.assertEqual(prod["stage"], "PROCESSING")

        # Reject invalid stage name
        with self.assertRaises(ValueError):
            self.engine.update_product_stage(p_id, "TELEPORTED", "Unknown", "Invalid", "FarmerOrgMSP")

    # 14. Stress Ordering Throughput Test (50 Blocks)
    def test_13_stress_ordering_throughput(self):
        for i in range(50):
            tx = Transaction(
                tx_type="AuditPing",
                sender_msp="OrdererMSP",
                payload={"seq": i, "timestamp": int(time.time())}
            )
            order_receipt = self.raft.order_and_commit_block([tx.to_dict()])
            self.assertEqual(order_receipt["status"], "COMMITTED")
            self.ledger.add_block([tx.to_dict()], order_receipt["leader"])

        integrity = self.ledger.verify_chain_integrity()
        self.assertTrue(integrity["valid"])
        self.assertGreaterEqual(integrity["total_blocks"], 50)

    # 15. End-to-End Consortium Multi-Hop Lifecycle
    def test_14_end_to_end_consortium_lifecycle(self):
        p_id = f"PROD-E2E-{int(time.time())}"

        # 1. Farmer registers
        self.engine.register_product(p_id, "Barley Malt", "B-MALT-99", "Bavaria, Germany", "20 MT", "FarmerOrgMSP")

        # 2. Farmer pins lab inspection to IPFS and anchors on-chain
        doc_bytes = b"Laboratory Inspection Result: Purity 99.8%. Certified."
        ipfs_rec = self.storage.store_document(doc_bytes, "malt_cert.pdf", "QUALITY_INSPECTION", "FarmerOrgMSP")
        self.engine.store_document_hash("DOC-MALT-01", "QUALITY_INSPECTION", ipfs_rec["sha256"], ipfs_rec["cid"], p_id, "FarmerOrgMSP")

        # 3. Farmer proposes transfer to Manufacturer
        prop = self.engine.propose_transfer(p_id, "ManufacturerOrgMSP", "Processing consignment", "FarmerOrgMSP")
        p_id_prop = prop["proposal"]["proposal_id"]

        # 4. Multi-party approvals: Manufacturer + Regulator
        self.engine.approve_transfer(p_id_prop, "ManufacturerOrgMSP", "APPROVED")
        self.engine.approve_transfer(p_id_prop, "RegulatorOrgMSP", "APPROVED")
        self.engine.finalize_transfer(p_id_prop, "FarmerOrgMSP")

        # Verify new owner
        prod = self.engine.read_product(p_id)
        self.assertEqual(prod["current_owner"], "ManufacturerOrgMSP")
        self.assertEqual(prod["stage"], "PROCESSING")

        # 5. Full audit history validation
        history = self.engine.get_transaction_history(p_id)
        self.assertGreaterEqual(len(history), 3)


if __name__ == "__main__":
    unittest.main()
