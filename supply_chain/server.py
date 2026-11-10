"""
Supply Chain Traceability & Risk Prediction Server.
Provides complete REST API endpoints for all 7 Dashboard Screens,
13 Smart Contract Methods, Raft Consensus Simulator, IPFS/Merkle Verification,
and AI Machine Learning Risk Scoring.

Runs seamlessly via Python 3 Standard Library (ThreadingHTTPServer)
and is 100% compatible with FastAPI / Uvicorn.
"""

import json
import os
import sys
import time
import urllib.parse
from http.server import HTTPServer, SimpleHTTPRequestHandler
from socketserver import ThreadingMixIn
from typing import Dict, Any, List

from supply_chain.core.crypto_identity import list_organizations, get_msp_info
from supply_chain.core.merkle import MerkleTree, hash_leaf
from supply_chain.core.ipfs_storage import IPFSStorage
from supply_chain.core.raft import RaftConsensusCluster
from supply_chain.core.blockchain import BlockchainLedger
from supply_chain.core.ai_risk_engine import AIRiskEngine
from supply_chain.core.smart_contracts import SmartContractEngine
from supply_chain.database.db import SupplyChainDatabase


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Multi-threaded HTTP Server for concurrent REST API calls."""
    daemon_threads = True


# Global Singletons
LEDGER = BlockchainLedger()
RAFT = RaftConsensusCluster()
STORAGE = IPFSStorage()
ENGINE = SmartContractEngine(LEDGER, RAFT)
DB = SupplyChainDatabase()


STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")


class SupplyChainRequestHandler(SimpleHTTPRequestHandler):
    """Handles REST API and static single-page dashboard delivery."""

    def _send_json(self, status_code: int, data: Any):
        body = json.dumps(data, indent=2).encode('utf-8')
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS, PUT, DELETE")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        """Handles CORS pre-flight."""
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def _read_json_body(self) -> Dict[str, Any]:
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length == 0:
            return {}
        raw = self.rfile.read(content_length).decode('utf-8')
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {}

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        # Static assets
        if path == "/favicon.ico":
            self.send_response(204)
            self.end_headers()
            return

        if path == "/" or path == "/index.html":
            index_path = os.path.join(STATIC_DIR, "index.html")
            if os.path.exists(index_path):
                with open(index_path, 'rb') as f:
                    content = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)
                return
            else:
                self._send_json(404, {"error": "Dashboard template not found"})
                return

        # API Endpoints
        try:
            if path == "/api/status":
                active_nodes = RAFT.get_active_nodes()
                self._send_json(200, {
                    "system": "AI & Blockchain Supply Chain Traceability Platform",
                    "version": "1.0",
                    "timestamp": int(time.time()),
                    "total_products": len(ENGINE.products),
                    "total_blocks": len(LEDGER.chain),
                    "total_proposals": len(ENGINE.proposals),
                    "total_documents": len(STORAGE.registry),
                    "raft_status": RAFT.get_cluster_status(),
                    "chain_integrity": LEDGER.verify_chain_integrity()
                })

            elif path == "/api/organizations":
                self._send_json(200, {
                    "organizations": list_organizations()
                })

            elif path == "/api/users":
                self._send_json(200, {
                    "users": DB.get_all_users()
                })

            elif path == "/api/products":
                self._send_json(200, {
                    "products": list(ENGINE.products.values())
                })

            elif path.startswith("/api/products/"):
                p_id = path.split("/api/products/")[1]
                p = ENGINE.read_product(p_id)
                if p:
                    self._send_json(200, {"product": p})
                else:
                    self._send_json(404, {"error": f"Product '{p_id}' not found"})

            elif path == "/api/proposals":
                self._send_json(200, {
                    "proposals": list(ENGINE.proposals.values())
                })

            elif path == "/api/blocks":
                self._send_json(200, {
                    "blocks": LEDGER.get_all_blocks()
                })

            elif path == "/api/history":
                p_id = query.get("product_id", [None])[0]
                self._send_json(200, {
                    "history": ENGINE.get_transaction_history(p_id)
                })

            elif path == "/api/documents":
                self._send_json(200, {
                    "documents": list(STORAGE.registry.values()),
                    "on_chain_hashes": list(ENGINE.documents.values())
                })

            elif path == "/api/merkle/roots":
                self._send_json(200, {
                    "roots": list(ENGINE.merkle_roots.values())
                })

            elif path == "/api/ai/history":
                p_id = query.get("product_id", [None])[0]
                if p_id:
                    self._send_json(200, {"reports": ENGINE.risk_reports.get(p_id, [])})
                else:
                    all_reports = []
                    for reports in ENGINE.risk_reports.values():
                        all_reports.extend(reports)
                    self._send_json(200, {"reports": all_reports})

            elif path == "/api/ai/metrics":
                report_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "model_evaluation_report.json")
                if os.path.exists(report_file):
                    with open(report_file, 'r', encoding='utf-8') as f:
                        self._send_json(200, json.load(f))
                else:
                    self._send_json(200, {"status": "Model not trained yet"})

            elif path == "/api/ai/dataset":
                dataset_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "supply_chain_risk_dataset.csv")
                if os.path.exists(dataset_file):
                    sample_rows = []
                    import csv
                    with open(dataset_file, 'r', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        for i, r in enumerate(reader):
                            if i >= 20: # Return first 20 records as preview
                                break
                            sample_rows.append(r)
                    self._send_json(200, {"total_preview": len(sample_rows), "dataset_sample": sample_rows})
                else:
                    self._send_json(404, {"error": "Dataset not found. Run dataset_generator.py"})

            elif path.startswith("/api/qr/"):
                p_id = path.split("/api/qr/")[1]
                prod = ENGINE.read_product(p_id)
                if not prod:
                    self._send_json(404, {"error": f"Product '{p_id}' not found"})
                else:
                    verification_payload = {
                        "issuer": "TraceChain-Permissioned-Ledger",
                        "product_id": prod["product_id"],
                        "batch_id": prod["batch_id"],
                        "origin": prod["origin"],
                        "current_custodian": prod["current_owner"],
                        "stage": prod["stage"],
                        "status": prod["status"],
                        "verify_url": f"http://127.0.0.1:8000/?verify={p_id}"
                    }
                    self._send_json(200, verification_payload)

            elif path == "/api/raft/status":
                self._send_json(200, RAFT.get_cluster_status())

            elif path == "/api/ledger/verify":
                self._send_json(200, LEDGER.verify_chain_integrity())

            else:
                self._send_json(404, {"error": f"Endpoint '{path}' not found"})

        except Exception as e:
            self._send_json(500, {"error": str(e)})

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        body = self._read_json_body()

        try:
            # 1. RegisterProduct
            if path == "/api/products/register":
                res = ENGINE.register_product(
                    product_id=body.get("product_id", f"PROD-{int(time.time())}"),
                    name=body.get("name", "Unnamed Product"),
                    batch_id=body.get("batch_id", "BATCH-001"),
                    origin=body.get("origin", "Registered Farm"),
                    quantity=body.get("quantity", "100 Units"),
                    sender_msp=body.get("sender_msp", "FarmerOrgMSP"),
                    signature=body.get("signature")
                )
                self._send_json(201, res)

            # 2. UpdateProductStage
            elif path == "/api/products/stage":
                res = ENGINE.update_product_stage(
                    product_id=body["product_id"],
                    new_stage=body["stage"],
                    location=body.get("location", "Standard Transit Facility"),
                    note=body.get("note", "Stage status updated"),
                    sender_msp=body.get("sender_msp", "FarmerOrgMSP")
                )
                self._send_json(200, res)

            # 3. VerifyProduct
            elif path == "/api/products/verify":
                res = ENGINE.verify_product(body["product_id"])
                self._send_json(200, res)

            # 4. ProposeTransfer
            elif path == "/api/proposals/propose":
                res = ENGINE.propose_transfer(
                    product_id=body["product_id"],
                    recipient_msp=body["recipient_msp"],
                    transfer_reason=body.get("reason", "Supply chain sale and custody transfer"),
                    sender_msp=body["sender_msp"]
                )
                self._send_json(201, res)

            # 5. ApproveTransfer
            elif path == "/api/proposals/approve":
                res = ENGINE.approve_transfer(
                    proposal_id=body["proposal_id"],
                    approver_msp=body["approver_msp"],
                    decision=body.get("decision", "APPROVED"),
                    remarks=body.get("remarks", "Digitally signed approval recorded")
                )
                self._send_json(200, res)

            # 6. FinalizeTransfer
            elif path == "/api/proposals/finalize":
                res = ENGINE.finalize_transfer(
                    proposal_id=body["proposal_id"],
                    sender_msp=body["sender_msp"]
                )
                self._send_json(200, res)

            # 7. Document Upload & StoreDocumentHash
            elif path == "/api/documents/upload":
                content = body.get("content", "Standard Certificate of Origin Content").encode('utf-8')
                file_name = body.get("file_name", "document.pdf")
                doc_type = body.get("doc_type", "QUALITY_INSPECTION")
                product_id = body.get("product_id")
                sender_msp = body.get("sender_msp", "FarmerOrgMSP")
                encrypt = body.get("encrypt", False)

                ipfs_res = STORAGE.store_document(
                    file_bytes=content,
                    file_name=file_name,
                    doc_type=doc_type,
                    uploaded_by_msp=sender_msp,
                    encrypt=encrypt
                )

                chain_res = ENGINE.store_document_hash(
                    doc_id=body.get("doc_id", f"DOC-{int(time.time())}"),
                    doc_type=doc_type,
                    sha256_hash=ipfs_res["sha256"],
                    ipfs_cid=ipfs_res["cid"],
                    product_id=product_id,
                    sender_msp=sender_msp
                )

                self._send_json(201, {
                    "ipfs": ipfs_res,
                    "blockchain": chain_res
                })

            # 8. VerifyDocument
            elif path == "/api/documents/verify":
                doc_id = body["doc_id"]
                calculated_hash = body["calculated_hash"]
                res = ENGINE.verify_document(doc_id, calculated_hash)
                self._send_json(200, res)

            # 9. Merkle Tree Generation & SubmitMerkleRoot
            elif path == "/api/merkle/generate":
                batch_id = body.get("batch_id", f"BATCH-{int(time.time())}")
                raw_items = body.get("items", [
                    f"Doc-Cert-Origin-{batch_id}",
                    f"Doc-Lab-Analysis-{batch_id}",
                    f"Doc-PhytoSanitary-{batch_id}",
                    f"Doc-Logistics-Waybill-{batch_id}"
                ])
                sender_msp = body.get("sender_msp", "FarmerOrgMSP")

                tree = MerkleTree(raw_items)
                root = tree.root

                chain_res = ENGINE.submit_merkle_root(
                    batch_id=batch_id,
                    root_hash=root,
                    leaf_count=len(tree.leaf_hashes),
                    sender_msp=sender_msp
                )

                # Generate proof for leaf index 0 as demonstrative sample
                sample_proof = tree.get_proof(0)

                self._send_json(201, {
                    "tree": tree.to_dict(),
                    "sample_proof": sample_proof,
                    "sample_leaf": tree.leaf_hashes[0],
                    "blockchain_receipt": chain_res
                })

            # 10. VerifyMerkleProof
            elif path == "/api/merkle/verify_proof":
                batch_id = body["batch_id"]
                leaf_hash = body["leaf_hash"]
                proof = body["proof"]
                res = ENGINE.verify_merkle_proof(batch_id, leaf_hash, proof)
                self._send_json(200, res)

            # 11. AI Risk Prediction & ReportRisk
            elif path == "/api/ai/predict":
                product_id = body.get("product_id", "PROD-ORG-WHEAT-2026")
                inputs = {
                    "supplier_reliability": float(body.get("supplier_reliability", 88.0)),
                    "historical_delays": float(body.get("historical_delays", 2.0)),
                    "rejection_rate": float(body.get("rejection_rate", 1.5)),
                    "doc_verification_failures": float(body.get("doc_verification_failures", 0.0)),
                    "tx_irregularities": float(body.get("tx_irregularities", 8.0))
                }
                assessment = AIRiskEngine.evaluate_risk(product_id, inputs)

                # Record on blockchain via ReportRisk
                chain_res = ENGINE.report_risk(
                    product_id=product_id,
                    risk_score=assessment["risk_score"],
                    classification=assessment["classification"],
                    factor_details=assessment["contributing_factors"],
                    snapshot_hash=assessment["snapshot_hash"],
                    model_version=assessment["model_version"],
                    sender_msp=body.get("sender_msp", "RegulatorOrgMSP")
                )

                self._send_json(200, {
                    "ai_assessment": assessment,
                    "blockchain_receipt": chain_res
                })

            elif path == "/api/ai/retrain":
                from supply_chain.ai.train_models import train_and_evaluate
                report = train_and_evaluate()
                self._send_json(200, {
                    "success": True,
                    "message": "AI Random Forest Model retrained successfully",
                    "report": report
                })

            # 12. Raft Toggle Node Failure/Recovery
            elif path == "/api/raft/toggle_node":
                node_id = body["node_id"]
                is_active = bool(body["is_active"])
                status = RAFT.set_node_status(node_id, is_active)
                self._send_json(200, status)

            # 13. Raft Force Election
            elif path == "/api/raft/elect":
                new_leader = RAFT.elect_new_leader_if_needed()
                self._send_json(200, {
                    "new_leader": new_leader,
                    "status": RAFT.get_cluster_status()
                })

            else:
                self._send_json(404, {"error": f"POST endpoint '{path}' not found"})

        except PermissionError as pe:
            self._send_json(403, {"error": str(pe), "code": "PERMISSION_DENIED"})
        except KeyError as ke:
            self._send_json(404, {"error": str(ke), "code": "NOT_FOUND"})
        except ValueError as ve:
            self._send_json(400, {"error": str(ve), "code": "VALIDATION_FAILED"})
        except RuntimeError as re:
            self._send_json(503, {"error": str(re), "code": "SERVICE_UNAVAILABLE"})
        except Exception as e:
            self._send_json(500, {"error": str(e), "code": "INTERNAL_SERVER_ERROR"})


def start_server(port: int = 8000, host: str = "0.0.0.0"):
    server = ThreadedHTTPServer((host, port), SupplyChainRequestHandler)
    print(f"🚀 Supply Chain Platform Server active at http://localhost:{port} and http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server gracefully.")
        server.server_close()


if __name__ == "__main__":
    port = 8000
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    start_server(port)
