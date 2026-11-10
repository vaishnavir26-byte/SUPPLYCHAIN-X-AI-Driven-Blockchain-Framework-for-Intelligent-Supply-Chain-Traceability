"""
Persistent Database & State Management Module.
Implements relational tables and audit stores for:
Users, Organizations, Products, Transactions, Approvals, Documents,
Merkle Records, Risk Records, Network Nodes (PRD Section 11).
"""

import sqlite3
import json
import os
import time
from typing import Dict, Any, List, Optional


class SupplyChainDatabase:
    """
    SQLite persistent database matching the 9 core entities from PRD Section 11.
    """
    def __init__(self, db_path: str = "supply_chain.db"):
        self.db_path = db_path
        self._init_schema()
        self._seed_default_users_and_orgs()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # 1. Organizations
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS organizations (
                    msp_id TEXT PRIMARY KEY,
                    org_name TEXT NOT NULL,
                    role TEXT NOT NULL,
                    certificate_id TEXT NOT NULL,
                    domain TEXT NOT NULL,
                    created_at INTEGER NOT NULL
                )
            """)

            # 2. Users
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    full_name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    role TEXT NOT NULL,
                    msp_id TEXT NOT NULL,
                    created_at INTEGER NOT NULL,
                    FOREIGN KEY (msp_id) REFERENCES organizations(msp_id)
                )
            """)

            # 3. Products
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    product_id TEXT PRIMARY KEY,
                    product_name TEXT NOT NULL,
                    batch_id TEXT NOT NULL,
                    origin TEXT NOT NULL,
                    quantity TEXT NOT NULL,
                    current_owner TEXT NOT NULL,
                    stage TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at INTEGER NOT NULL
                )
            """)

            # 4. Transactions
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    tx_id TEXT PRIMARY KEY,
                    tx_type TEXT NOT NULL,
                    sender_msp TEXT NOT NULL,
                    block_number INTEGER NOT NULL,
                    block_hash TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    signature TEXT NOT NULL,
                    timestamp INTEGER NOT NULL
                )
            """)

            # 5. Approvals (Multi-party transfer requests)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS approvals (
                    proposal_id TEXT PRIMARY KEY,
                    product_id TEXT NOT NULL,
                    from_msp TEXT NOT NULL,
                    to_msp TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    status TEXT NOT NULL,
                    required_approvals_json TEXT NOT NULL,
                    collected_approvals_json TEXT NOT NULL,
                    created_at INTEGER NOT NULL
                )
            """)

            # 6. Documents (IPFS & Cryptographic Hashes)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    doc_id TEXT PRIMARY KEY,
                    cid TEXT NOT NULL,
                    sha256_hash TEXT NOT NULL,
                    file_name TEXT NOT NULL,
                    doc_type TEXT NOT NULL,
                    product_id TEXT,
                    uploaded_by TEXT NOT NULL,
                    is_encrypted INTEGER NOT NULL,
                    created_at INTEGER NOT NULL
                )
            """)

            # 7. Merkle Records
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS merkle_records (
                    batch_id TEXT PRIMARY KEY,
                    root_hash TEXT NOT NULL,
                    leaf_count INTEGER NOT NULL,
                    submitted_by TEXT NOT NULL,
                    timestamp INTEGER NOT NULL
                )
            """)

            # 8. Risk Records
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS risk_records (
                    record_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id TEXT NOT NULL,
                    risk_score REAL NOT NULL,
                    classification TEXT NOT NULL,
                    snapshot_hash TEXT NOT NULL,
                    model_version TEXT NOT NULL,
                    factors_json TEXT NOT NULL,
                    timestamp INTEGER NOT NULL
                )
            """)

            # 9. Network Nodes (Raft cluster)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS network_nodes (
                    node_id TEXT PRIMARY KEY,
                    address TEXT NOT NULL,
                    role TEXT NOT NULL,
                    is_active INTEGER NOT NULL,
                    last_heartbeat INTEGER NOT NULL
                )
            """)

            conn.commit()

    def _seed_default_users_and_orgs(self):
        """Populates initial consortium organizations and user accounts."""
        orgs = [
            ("FarmerOrgMSP", "GreenValley Organic Farmers Co-op", "FARMER", "CERT-FARMER-9901-X509", "farmer.supplychain.org"),
            ("ManufacturerOrgMSP", "Apex Food Processing & Packaging Ltd.", "MANUFACTURER", "CERT-MFR-4421-X509", "mfr.supplychain.org"),
            ("DistributorOrgMSP", "TransGlobal Cold-Chain Logistics", "DISTRIBUTOR", "CERT-DIST-7789-X509", "logistics.supplychain.org"),
            ("RetailerOrgMSP", "MetroFresh Hypermarkets Corp.", "RETAILER", "CERT-RETAIL-1123-X509", "retail.supplychain.org"),
            ("RegulatorOrgMSP", "National Agricultural & Food Safety Authority", "REGULATOR", "CERT-REGULATOR-0001-X509", "safety.regulator.gov"),
            ("OrdererMSP", "Consortium Raft Ordering Service", "ADMIN", "CERT-ORDERER-ROOT-X509", "orderers.supplychain.net")
        ]

        users = [
            ("usr-farmer-01", "Ramesh Kumar (Master Grower)", "ramesh@farmer.supplychain.org", "FARMER", "FarmerOrgMSP"),
            ("usr-mfr-01", "Dr. Elena Rostova (Plant Director)", "elena@mfr.supplychain.org", "MANUFACTURER", "ManufacturerOrgMSP"),
            ("usr-dist-01", "Marcus Vance (Fleet Manager)", "marcus@logistics.supplychain.org", "DISTRIBUTOR", "DistributorOrgMSP"),
            ("usr-ret-01", "Sarah Chen (Inventory Lead)", "sarah@retail.supplychain.org", "RETAILER", "RetailerOrgMSP"),
            ("usr-reg-01", "Inspector Donald Blake", "blake@safety.regulator.gov", "REGULATOR", "RegulatorOrgMSP"),
            ("usr-admin-01", "SysAdmin Root Authority", "admin@supplychain.net", "ADMIN", "OrdererMSP")
        ]

        now = int(time.time())
        with self._get_connection() as conn:
            cursor = conn.cursor()
            for org in orgs:
                cursor.execute("""
                    INSERT OR IGNORE INTO organizations (msp_id, org_name, role, certificate_id, domain, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (*org, now))

            for user in users:
                cursor.execute("""
                    INSERT OR IGNORE INTO users (user_id, full_name, email, role, msp_id, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (*user, now))

            conn.commit()

    def get_all_users(self) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            rows = conn.execute("SELECT * FROM users").fetchall()
            return [dict(r) for r in rows]

    def get_all_organizations(self) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            rows = conn.execute("SELECT * FROM organizations").fetchall()
            return [dict(r) for r in rows]
