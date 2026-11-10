"""
Simulated Raft Consensus Ordering Service.
Implements Crash-Fault Tolerant (CFT) 3-Node Raft Consensus for Hyperledger Fabric ordering.
Tracks Leader, Followers, Heartbeats, Log Replication, Quorum-based Commitments,
and dynamic fault injection (node crash & recovery).
"""

import time
import random
import threading
from typing import Dict, List, Any, Optional, Tuple


class RaftNode:
    """Represents a single Raft ordering service node."""
    def __init__(self, node_id: str, address: str):
        self.node_id = node_id
        self.address = address
        self.is_active = True
        self.role = "FOLLOWER"  # LEADER, FOLLOWER, CANDIDATE
        self.current_term = 1
        self.voted_for: Optional[str] = None
        self.log: List[Dict[str, Any]] = []
        self.commit_index = 0
        self.last_heartbeat = time.time()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "address": self.address,
            "is_active": self.is_active,
            "role": self.role,
            "current_term": self.current_term,
            "commit_index": self.commit_index,
            "log_length": len(self.log),
            "last_heartbeat": int(self.last_heartbeat)
        }


class RaftConsensusCluster:
    """
    3-Node Raft Consensus Ordering Service Cluster.
    Cluster Size: 3 Nodes. Quorum: 2 Nodes.
    """
    def __init__(self):
        self.nodes: Dict[str, RaftNode] = {
            "orderer1.supplychain.net": RaftNode("orderer1.supplychain.net", "grpc://10.0.0.11:7050"),
            "orderer2.supplychain.net": RaftNode("orderer2.supplychain.net", "grpc://10.0.0.12:7050"),
            "orderer3.supplychain.net": RaftNode("orderer3.supplychain.net", "grpc://10.0.0.13:7050"),
        }
        # Initial leader
        self.leader_id = "orderer1.supplychain.net"
        self.nodes[self.leader_id].role = "LEADER"
        self.term = 1
        self.quorum_size = 2  # (3 // 2) + 1
        self.uncommitted_txs: List[Dict[str, Any]] = []
        self._lock = threading.RLock()

    def get_active_nodes(self) -> List[RaftNode]:
        """Returns list of currently online nodes."""
        return [node for node in self.nodes.values() if node.is_active]

    def has_quorum(self) -> bool:
        """Checks whether the number of active nodes satisfies the Raft quorum threshold."""
        return len(self.get_active_nodes()) >= self.quorum_size

    def get_leader(self) -> Optional[RaftNode]:
        """Returns the current active leader node if alive."""
        leader = self.nodes.get(self.leader_id)
        if leader and leader.is_active and leader.role == "LEADER":
            return leader
        return None

    def elect_new_leader_if_needed(self) -> Optional[str]:
        """
        Runs Raft leader election if current leader is offline and quorum is present.
        """
        with self._lock:
            active_nodes = self.get_active_nodes()
            if len(active_nodes) < self.quorum_size:
                # Quorum lost, cannot elect leader
                for node in self.nodes.values():
                    if node.role == "LEADER":
                        node.role = "FOLLOWER"
                self.leader_id = ""
                return None

            current_leader = self.get_leader()
            if current_leader:
                return self.leader_id

            # Current leader is down, elect candidate among active followers
            self.term += 1
            candidate = active_nodes[0]
            candidate.current_term = self.term
            candidate.role = "LEADER"
            candidate.voted_for = candidate.node_id
            self.leader_id = candidate.node_id

            # Set other active nodes to followers
            for node in active_nodes[1:]:
                node.role = "FOLLOWER"
                node.current_term = self.term
                node.voted_for = candidate.node_id

            return self.leader_id

    def set_node_status(self, node_id: str, is_active: bool) -> Dict[str, Any]:
        """Simulates crashing or reviving an orderer node."""
        with self._lock:
            if node_id not in self.nodes:
                raise ValueError(f"Unknown orderer node {node_id}")

            node = self.nodes[node_id]
            node.is_active = is_active
            node.last_heartbeat = time.time()

            if not is_active and node.role == "LEADER":
                node.role = "FOLLOWER"
                self.leader_id = ""

            # Check leader and quorum status after state change
            self.elect_new_leader_if_needed()

            return self.get_cluster_status()

    def order_and_commit_block(self, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Simulates Raft consensus pipeline:
        1. Checks for active leader and quorum (>= 2 nodes).
        2. Leader prepares candidate block.
        3. Leader sends AppendEntries RPC to followers.
        4. When at least 1 follower confirms (total >= 2 with leader), commit is finalized.
        """
        with self._lock:
            if not self.has_quorum():
                active_count = len(self.get_active_nodes())
                raise RuntimeError(
                    f"Raft Consensus Halted: Quorum lost. Active nodes: {active_count}/{len(self.nodes)}. "
                    f"Minimum required quorum is {self.quorum_size} nodes."
                )

            leader = self.get_leader()
            if not leader:
                self.elect_new_leader_if_needed()
                leader = self.get_leader()
                if not leader:
                    raise RuntimeError("Raft Consensus Error: No active leader could be elected.")

            # Replicate to active followers
            confirmations: List[str] = [leader.node_id]
            active_followers = [n for n in self.get_active_nodes() if n.node_id != leader.node_id]

            log_entry = {
                "term": self.term,
                "timestamp": int(time.time()),
                "transactions": transactions,
                "tx_count": len(transactions)
            }

            leader.log.append(log_entry)
            leader.commit_index = len(leader.log)

            for follower in active_followers:
                follower.log.append(log_entry)
                follower.commit_index = len(follower.log)
                follower.last_heartbeat = time.time()
                confirmations.append(follower.node_id)

            return {
                "status": "COMMITTED",
                "term": self.term,
                "leader": leader.node_id,
                "confirmations": confirmations,
                "quorum_achieved": len(confirmations) >= self.quorum_size,
                "active_orderers": len(self.get_active_nodes()),
                "total_orderers": len(self.nodes)
            }

    def get_cluster_status(self) -> Dict[str, Any]:
        """Returns comprehensive telemetry for Raft cluster monitoring."""
        active = self.get_active_nodes()
        quorum_ok = len(active) >= self.quorum_size
        leader = self.get_leader()

        return {
            "cluster_type": "Crash-Fault Tolerant (CFT) Raft Ordering Service",
            "total_nodes": len(self.nodes),
            "active_nodes_count": len(active),
            "quorum_threshold": self.quorum_size,
            "quorum_available": quorum_ok,
            "current_term": self.term,
            "current_leader": leader.node_id if leader else "None (Quorum Unavailable or In Election)",
            "network_status": "ONLINE - OPERATIONAL" if quorum_ok else "HALTED - INSUFFICIENT QUORUM",
            "nodes": [node.to_dict() for node in self.nodes.values()],
            "fault_tolerance_note": "Raft tolerates 1 node failure out of 3. Requires at least 2 nodes for consensus."
        }
