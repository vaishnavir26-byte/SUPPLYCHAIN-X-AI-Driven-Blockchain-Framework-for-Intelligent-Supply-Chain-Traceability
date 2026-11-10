"""
Cryptographic Merkle Tree Engine.
Supports leaf hashing, tree construction, Merkle root calculation,
cryptographic inclusion proof generation, and verification.
"""

import hashlib
from typing import List, Dict, Any, Tuple, Optional


def hash_pair(left: str, right: str) -> str:
    """Concatenates two hexadecimal hashes and returns their SHA-256 digest."""
    combined = (left + right).encode('utf-8')
    return hashlib.sha256(combined).hexdigest()


def hash_leaf(data: str) -> str:
    """Computes SHA-256 hash for a leaf element (document hash, record string)."""
    return hashlib.sha256(data.encode('utf-8')).hexdigest()


class MerkleTree:
    """
    Binary Merkle Tree implementation for batch verification of documents & transactions.
    """
    def __init__(self, raw_leaves: List[str]):
        """
        Initializes Merkle tree with raw items (document hashes or payload strings).
        Leaves are hashed to produce leaf digests.
        """
        if not raw_leaves:
            raise ValueError("Merkle tree requires at least one leaf.")
        
        self.raw_leaves = raw_leaves
        # Ensure all leaves are hashed
        self.leaf_hashes: List[str] = [
            leaf if len(leaf) == 64 and all(c in '0123456789abcdefABCDEF' for c in leaf)
            else hash_leaf(leaf)
            for leaf in raw_leaves
        ]
        self.levels: List[List[str]] = [self.leaf_hashes]
        self.build_tree()

    def build_tree(self):
        """Builds tree from leaves up to the root."""
        current_level = self.leaf_hashes
        while len(current_level) > 1:
            next_level: List[str] = []
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                # If odd number of nodes, duplicate the last node
                right = current_level[i + 1] if i + 1 < len(current_level) else left
                parent = hash_pair(left, right)
                next_level.append(parent)
            self.levels.append(next_level)
            current_level = next_level

    @property
    def root(self) -> str:
        """Returns the 32-byte hexadecimal Merkle root."""
        return self.levels[-1][0]

    def get_proof(self, index: int) -> List[Dict[str, str]]:
        """
        Generates cryptographic inclusion proof (audit path) for leaf at given index.
        Returns list of sibling dictionaries: [{'hash': sibling_hash, 'position': 'left'|'right'}].
        """
        if index < 0 or index >= len(self.leaf_hashes):
            raise IndexError("Leaf index out of bounds.")

        proof: List[Dict[str, str]] = []
        curr_idx = index

        for level in self.levels[:-1]:
            # Sibling index
            if curr_idx % 2 == 0:
                # curr is left child, sibling is right
                sibling_idx = curr_idx + 1 if curr_idx + 1 < len(level) else curr_idx
                position = "right"
            else:
                # curr is right child, sibling is left
                sibling_idx = curr_idx - 1
                position = "left"

            proof.append({
                "hash": level[sibling_idx],
                "position": position
            })
            curr_idx //= 2

        return proof

    @staticmethod
    def verify_proof(leaf_hash: str, proof: List[Dict[str, str]], expected_root: str) -> bool:
        """
        Verifies that a leaf hash is part of the Merkle tree with root expected_root.
        Computes path up to the root in O(log N) operations.
        """
        current_hash = leaf_hash
        for step in proof:
            sibling = step["hash"]
            position = step["position"]
            if position == "left":
                current_hash = hash_pair(sibling, current_hash)
            else:
                current_hash = hash_pair(current_hash, sibling)

        return current_hash.lower() == expected_root.lower()

    def to_dict(self) -> Dict[str, Any]:
        """Serializes Merkle tree structure for visualization and inspection."""
        return {
            "root": self.root,
            "leaf_count": len(self.leaf_hashes),
            "depth": len(self.levels),
            "leaf_hashes": self.leaf_hashes,
            "levels": self.levels
        }
