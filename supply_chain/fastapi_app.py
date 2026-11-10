"""
FastAPI Implementation for Layer 2 Application Layer (PRD Section 8 & 9).
Can be launched using:
    uvicorn supply_chain.fastapi_app:app --reload --port 8000
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import os
import time

from supply_chain.core.crypto_identity import list_organizations
from supply_chain.core.merkle import MerkleTree
from supply_chain.core.ipfs_storage import IPFSStorage
from supply_chain.core.raft import RaftConsensusCluster
from supply_chain.core.blockchain import BlockchainLedger
from supply_chain.core.ai_risk_engine import AIRiskEngine
from supply_chain.core.smart_contracts import SmartContractEngine
from supply_chain.database.db import SupplyChainDatabase

app = FastAPI(
    title="TraceChain AI — Supply Chain Traceability & Risk Prediction API",
    description="Permissioned Blockchain Simulation & AI Risk Scoring Platform (Hyperledger Fabric Architecture)",
    version="1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Global Engine Instances
LEDGER = BlockchainLedger()
RAFT = RaftConsensusCluster()
STORAGE = IPFSStorage()
ENGINE = SmartContractEngine(LEDGER, RAFT)
DB = SupplyChainDatabase()

STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")


# Pydantic Schemas
class ProductRegistrationRequest(BaseModel):
    product_id: str
    name: str
    batch_id: str
    origin: str
    quantity: str
    sender_msp: str = "FarmerOrgMSP"
    signature: Optional[str] = None


class ProductStageUpdateRequest(BaseModel):
    product_id: str
    stage: str
    location: str = "Standard Transit Facility"
    note: str = "Stage updated"
    sender_msp: str


class TransferProposalRequest(BaseModel):
    product_id: str
    recipient_msp: str
    reason: str
    sender_msp: str


class TransferApprovalRequest(BaseModel):
    proposal_id: str
    approver_msp: str
    decision: str = "APPROVED"
    remarks: str = "Signed digitally"


class TransferFinalizeRequest(BaseModel):
    proposal_id: str
    sender_msp: str


class DocumentUploadRequest(BaseModel):
    file_name: str
    doc_type: str
    content: str
    encrypt: bool = False
    product_id: Optional[str] = None
    sender_msp: str = "FarmerOrgMSP"


class DocumentVerifyRequest(BaseModel):
    doc_id: str
    calculated_hash: str


class MerkleGenerateRequest(BaseModel):
    batch_id: str
    items: Optional[List[str]] = None
    sender_msp: str = "FarmerOrgMSP"


class MerkleVerifyProofRequest(BaseModel):
    batch_id: str
    leaf_hash: str
    proof: List[Dict[str, str]]


class AIRiskPredictionRequest(BaseModel):
    product_id: str
    supplier_reliability: float = 85.0
    historical_delays: float = 2.0
    rejection_rate: float = 1.5
    doc_verification_failures: float = 0.0
    tx_irregularities: float = 8.0
    sender_msp: str = "RegulatorOrgMSP"


class RaftToggleNodeRequest(BaseModel):
    node_id: str
    is_active: bool


# Routes
@app.get("/")
def serve_dashboard():
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "TraceChain AI Dashboard UI ready."}


@app.get("/api/status")
def get_system_status():
    return {
        "system": "AI & Blockchain Supply Chain Traceability Platform",
        "version": "1.0",
        "timestamp": int(time.time()),
        "total_products": len(ENGINE.products),
        "total_blocks": len(LEDGER.chain),
        "total_proposals": len(ENGINE.proposals),
        "total_documents": len(STORAGE.registry),
        "raft_status": RAFT.get_cluster_status(),
        "chain_integrity": LEDGER.verify_chain_integrity()
    }


@app.get("/api/organizations")
def get_organizations():
    return {"organizations": list_organizations()}


@app.get("/api/users")
def get_users():
    return {"users": DB.get_all_users()}


@app.get("/api/products")
def get_products():
    return {"products": list(ENGINE.products.values())}


@app.post("/api/products/register", status_code=status.HTTP_201_CREATED)
def register_product(req: ProductRegistrationRequest):
    try:
        return ENGINE.register_product(
            product_id=req.product_id,
            name=req.name,
            batch_id=req.batch_id,
            origin=req.origin,
            quantity=req.quantity,
            sender_msp=req.sender_msp,
            signature=req.signature
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/products/stage")
def update_stage(req: ProductStageUpdateRequest):
    try:
        return ENGINE.update_product_stage(
            product_id=req.product_id,
            new_stage=req.stage,
            location=req.location,
            note=req.note,
            sender_msp=req.sender_msp
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/proposals/propose", status_code=status.HTTP_201_CREATED)
def propose_transfer(req: TransferProposalRequest):
    try:
        return ENGINE.propose_transfer(
            product_id=req.product_id,
            recipient_msp=req.recipient_msp,
            transfer_reason=req.reason,
            sender_msp=req.sender_msp
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/proposals/approve")
def approve_transfer(req: TransferApprovalRequest):
    try:
        return ENGINE.approve_transfer(
            proposal_id=req.proposal_id,
            approver_msp=req.approver_msp,
            decision=req.decision,
            remarks=req.remarks
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/proposals/finalize")
def finalize_transfer(req: TransferFinalizeRequest):
    try:
        return ENGINE.finalize_transfer(
            proposal_id=req.proposal_id,
            sender_msp=req.sender_msp
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/ai/predict")
def predict_risk(req: AIRiskPredictionRequest):
    try:
        inputs = {
            "supplier_reliability": req.supplier_reliability,
            "historical_delays": req.historical_delays,
            "rejection_rate": req.rejection_rate,
            "doc_verification_failures": req.doc_verification_failures,
            "tx_irregularities": req.tx_irregularities
        }
        assessment = AIRiskEngine.evaluate_risk(req.product_id, inputs)
        chain_res = ENGINE.report_risk(
            product_id=req.product_id,
            risk_score=assessment["risk_score"],
            classification=assessment["classification"],
            factor_details=assessment["contributing_factors"],
            snapshot_hash=assessment["snapshot_hash"],
            model_version=assessment["model_version"],
            sender_msp=req.sender_msp
        )
        return {
            "ai_assessment": assessment,
            "blockchain_receipt": chain_res
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/raft/toggle_node")
def toggle_raft_node(req: RaftToggleNodeRequest):
    try:
        return RAFT.set_node_status(req.node_id, req.is_active)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
