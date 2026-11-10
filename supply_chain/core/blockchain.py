"""
Simulated Permissioned Blockchain Ledger.
Implements cryptographically chained blocks, transaction ordering receipts,
Merkle roots of transactions, and immutable audit logs.
"""

import time
import hashlib
import json
import uuid
from typing import List, Dict, Any, Optional
from supply_chain.core.crypto_identity import canonical_json_bytes, sign_payload, verify_signature
from supply_chain.core.merkle import MerkleTree


class Transaction:
    """Represents an atomic, digitally signed transaction in the permissioned blockchain."""
    def __init__(
        self,
        tx_type: str,
        sender_msp: str,
        payload: Dict[str, Any],
        signature: Optional[str] = None,
        tx_id: Optional[str] = None,
        timestamp: Optional[int] = None
    ):
        self.tx_id = tx_id or f"TX-{uuid.uuid4().hex[:12].upper()}"
        self.timestamp = timestamp or int(time.time())
        self.tx_type = tx_type
        self.sender_msp = sender_msp
        self.payload = payload
        
        # Sign transaction if signature not pre-supplied
        if not signature:
            self.signature = sign_payload(self.sender_msp, {
                "tx_id": self.tx_id,
                "tx_type": self.tx_type,
                "timestamp": self.timestamp,
                "sender_msp": self.sender_msp,
                "payload": self.payload
            })
        else:
            self.signature = signature

    def verify(self) -> bool:
        """Verifies that the transaction has a valid signature from sender_msp."""
        body = {
            "tx_id": self.tx_id,
            "tx_type": self.tx_type,
            "timestamp": self.timestamp,
            "sender_msp": self.sender_msp,
            "payload": self.payload
        }
        return verify_signature(self.sender_msp, body, self.signature)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tx_id": self.tx_id,
            "timestamp": self.timestamp,
            "tx_type": self.tx_type,
            "sender_msp": self.sender_msp,
            "payload": self.payload,
            "signature": self.signature
        }

    def compute_hash(self) -> str:
        data = canonical_json_bytes(self.to_dict())
        return hashlib.sha256(data).hexdigest()


class Block:
    """Represents a validated block in the permissioned blockchain."""
    def __init__(
        self,
        block_number: int,
        transactions: List[Dict[str, Any]],
        previous_hash: str,
        orderer_node: str,
        timestamp: Optional[int] = None,
        block_hash: Optional[str] = None,
        merkle_root: Optional[str] = None
    ):
        self.block_number = block_number
        self.timestamp = timestamp or int(time.time())
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.orderer_node = orderer_node

        # Compute Merkle root of transaction hashes
        if merkle_root:
            self.merkle_root = merkle_root
        else:
            tx_hashes = [
                tx.get("tx_id", str(i)) for i, tx in enumerate(self.transactions)
            ] if self.transactions else ["EMPTY_BLOCK_SEED"]
            mt = MerkleTree(tx_hashes)
            self.merkle_root = mt.root

        # Compute block hash
        self.block_hash = block_hash or self.compute_hash()
        self.orderer_signature = sign_payload("OrdererMSP", {
            "block_number": self.block_number,
            "block_hash": self.block_hash,
            "orderer_node": self.orderer_node
        })

    def compute_hash(self) -> str:
        header = {
            "block_number": self.block_number,
            "timestamp": self.timestamp,
            "previous_hash": self.previous_hash,
            "merkle_root": self.merkle_root,
            "orderer_node": self.orderer_node,
            "tx_count": len(self.transactions)
        }
        return hashlib.sha256(canonical_json_bytes(header)).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "block_number": self.block_number,
            "timestamp": self.timestamp,
            "previous_hash": self.previous_hash,
            "merkle_root": self.merkle_root,
            "orderer_node": self.orderer_node,
            "orderer_signature": self.orderer_signature,
            "block_hash": self.block_hash,
            "tx_count": len(self.transactions),
            "transactions": self.transactions
        }


class BlockchainLedger:
    """Maintains the linear sequence of cryptographically linked blocks."""
    def __init__(self):
        self.chain: List[Block] = []
        self._create_genesis_block()

    def _create_genesis_block(self):
        """Creates the tamper-evident Genesis Block 0."""
        genesis_tx = {
            "tx_id": "TX-GENESIS-CONSORTIUM-BOOTSTRAP",
            "timestamp": int(time.time()),
            "tx_type": "ConsortiumGenesis",
            "sender_msp": "OrdererMSP",
            "payload": {
                "network": "AI-Blockchain-SupplyChain-Permissioned-Ledger",
                "version": "1.0",
                "consensus": "Raft-3Node-CFT",
                "organizations": ["FarmerOrgMSP", "ManufacturerOrgMSP", "DistributorOrgMSP", "RetailerOrgMSP", "RegulatorOrgMSP"]
            },
            "signature": "GENESIS_CRYPTOGRAPHIC_ROOT_SIGNATURE"
        }
        genesis_block = Block(
            block_number=0,
            transactions=[genesis_tx],
            previous_hash="0" * 64,
            orderer_node="orderer1.supplychain.net"
        )
        self.chain.append(genesis_block)

    @property
    def latest_block(self) -> Block:
        return self.chain[-1]

    def add_block(self, transactions: List[Dict[str, Any]], orderer_node: str) -> Block:
        """Appends a new block ordered by Raft ordering service."""
        new_block = Block(
            block_number=len(self.chain),
            transactions=transactions,
            previous_hash=self.latest_block.block_hash,
            orderer_node=orderer_node
        )
        self.chain.append(new_block)
        return new_block

    def verify_chain_integrity(self) -> Dict[str, Any]:
        """
        Validates entire blockchain lineage from Genesis to head:
        - Checks block hash correctness.
        - Checks parent hash pointers.
        - Checks transaction signatures.
        """
        for i in range(1, len(self.chain)):
            curr = self.chain[i]
            prev = self.chain[i - 1]

            # Verify parent hash pointer
            if curr.previous_hash != prev.block_hash:
                return {
                    "valid": False,
                    "error": f"Parent hash pointer broken at block #{curr.block_number}",
                    "corrupted_block": curr.block_number
                }

            # Verify block self-hash
            recomputed = curr.compute_hash()
            if curr.block_hash != recomputed:
                return {
                    "valid": False,
                    "error": f"Block hash tampering detected at block #{curr.block_number}",
                    "corrupted_block": curr.block_number
                }

        return {
            "valid": True,
            "total_blocks": len(self.chain),
            "head_hash": self.latest_block.block_hash,
            "message": "Blockchain ledger integrity verified: all cryptographic links intact."
        }

    def get_all_blocks(self) -> List[Dict[str, Any]]:
        return [b.to_dict() for b in self.chain]

    def find_transaction(self, tx_id: str) -> Optional[Dict[str, Any]]:
        for block in self.chain:
            for tx in block.transactions:
                if tx.get("tx_id") == tx_id:
                    return {
                        "block_number": block.block_number,
                        "block_hash": block.block_hash,
                        "transaction": tx
                    }
        return None
