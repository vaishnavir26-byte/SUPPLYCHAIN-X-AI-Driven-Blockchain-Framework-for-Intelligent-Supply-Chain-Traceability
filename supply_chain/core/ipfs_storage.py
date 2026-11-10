"""
IPFS Content-Addressed Storage Architecture & Document Verification Engine.
Provides SHA-256 cryptographic hashing, deterministic CID generation,
mock decentralized pinning, and document tampering detection.
"""

import hashlib
import base64
import os
import json
import time
from typing import Dict, Any, Optional, Tuple


def compute_sha256(content_bytes: bytes) -> str:
    """Computes standard 32-byte SHA-256 hex digest of raw file contents."""
    return hashlib.sha256(content_bytes).hexdigest()


def generate_cid_v1(content_bytes: bytes) -> str:
    """
    Generates a deterministic IPFS CIDv1 string using raw SHA-256 multihash specification.
    Format: bafkrei + base32(0x12 0x20 [32-byte sha256 digest])
    """
    digest = hashlib.sha256(content_bytes).digest()
    # Multihash prefix: 0x12 (sha2-256), 0x20 (32 bytes length)
    multihash = b'\x12\x20' + digest
    # Base32 encoding (lowercase, no padding)
    b32 = base64.b32encode(multihash).decode('ascii').lower().rstrip('=')
    return f"bafkrei{b32}"


class IPFSStorage:
    """
    Simulated IPFS node storing pinned documents indexed by CID and SHA-256 hash.
    Persists documents in local storage folder with integrity metadata.
    """
    def __init__(self, storage_dir: str = "/tmp/ipfs_repo"):
        self.storage_dir = storage_dir
        os.makedirs(self.storage_dir, exist_ok=True)
        self.registry_file = os.path.join(self.storage_dir, "ipfs_registry.json")
        self.registry: Dict[str, Dict[str, Any]] = self._load_registry()

    def _load_registry(self) -> Dict[str, Dict[str, Any]]:
        if os.path.exists(self.registry_file):
            try:
                with open(self.registry_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save_registry(self):
        with open(self.registry_file, 'w', encoding='utf-8') as f:
            json.dump(self.registry, f, indent=2)

    def store_document(
        self,
        file_bytes: bytes,
        file_name: str,
        doc_type: str,
        uploaded_by_msp: str,
        encrypt: bool = False
    ) -> Dict[str, Any]:
        """
        Stores document into IPFS architecture.
        Calculates SHA-256, generates CID, optionally simulates encryption,
        and returns storage receipt.
        """
        raw_hash = compute_sha256(file_bytes)
        stored_bytes = file_bytes

        if encrypt:
            # Simple reversible XOR mask simulation for sensitive document encryption
            key = b"SUPPLY_CHAIN_REGULATORY_ENCRYPTION_KEY_2026"
            stored_bytes = bytes(b ^ key[i % len(key)] for i, b in enumerate(file_bytes))

        cid = generate_cid_v1(stored_bytes)
        file_path = os.path.join(self.storage_dir, cid)

        with open(file_path, 'wb') as f:
            f.write(stored_bytes)

        record = {
            "cid": cid,
            "sha256": raw_hash,
            "file_name": file_name,
            "file_size": len(file_bytes),
            "doc_type": doc_type,
            "uploaded_by": uploaded_by_msp,
            "is_encrypted": encrypt,
            "pinned_at": int(time.time()),
            "storage_path": file_path
        }

        self.registry[cid] = record
        self._save_registry()
        return record

    def retrieve_document(self, cid: str) -> Optional[Tuple[bytes, Dict[str, Any]]]:
        """Retrieves raw document bytes and metadata using its IPFS CID."""
        record = self.registry.get(cid)
        if not record:
            return None
        file_path = record["storage_path"]
        if not os.path.exists(file_path):
            return None

        with open(file_path, 'rb') as f:
            stored_bytes = f.read()

        if record.get("is_encrypted"):
            key = b"SUPPLY_CHAIN_REGULATORY_ENCRYPTION_KEY_2026"
            raw_bytes = bytes(b ^ key[i % len(key)] for i, b in enumerate(stored_bytes))
        else:
            raw_bytes = stored_bytes

        return raw_bytes, record

    def verify_document_integrity(self, cid: str, provided_bytes: bytes) -> Dict[str, Any]:
        """
        Verifies document bytes against recorded IPFS CID and stored SHA-256 hash.
        Detects tampering or bit-level modifications.
        """
        computed_hash = compute_sha256(provided_bytes)
        record = self.registry.get(cid)

        if not record:
            return {
                "valid": False,
                "error": "CID not found in IPFS repository",
                "computed_hash": computed_hash,
                "expected_hash": None,
                "tampered": True
            }

        expected_hash = record["sha256"]
        is_match = (computed_hash == expected_hash)

        return {
            "valid": is_match,
            "cid": cid,
            "computed_hash": computed_hash,
            "expected_hash": expected_hash,
            "tampered": not is_match,
            "file_name": record["file_name"],
            "uploaded_by": record["uploaded_by"],
            "doc_type": record["doc_type"]
        }

    def list_documents(self) -> Dict[str, Dict[str, Any]]:
        """Returns all documents pinned in the IPFS repository."""
        return self.registry
