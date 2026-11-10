"""
Cryptographic Identity and Digital Signature Verification Module.
Simulates Membership Service Provider (MSP) and X.509 digital certificates
for Hyperledger Fabric permissioned networks.
"""

import hashlib
import hmac
import json
import base64
from typing import Dict, Any, Tuple, Optional

# Organization Registry with simulated X.509 public-private keypairs
ORGANIZATIONS: Dict[str, Dict[str, Any]] = {
    "FarmerOrgMSP": {
        "org_name": "GreenValley Organic Farmers Co-op",
        "role": "FARMER",
        "msp_id": "FarmerOrgMSP",
        "secret_key": "farmer_priv_key_secure_supplychain_seed_987123",
        "public_key": "farmer_pub_key_greenvalley_x509_cert_v1",
        "certificate_id": "CERT-FARMER-9901-X509",
        "domain": "farmer.supplychain.org"
    },
    "ManufacturerOrgMSP": {
        "org_name": "Apex Food Processing & Packaging Ltd.",
        "role": "MANUFACTURER",
        "msp_id": "ManufacturerOrgMSP",
        "secret_key": "mfr_priv_key_secure_supplychain_seed_847291",
        "public_key": "mfr_pub_key_apex_processing_x509_cert_v1",
        "certificate_id": "CERT-MFR-4421-X509",
        "domain": "mfr.supplychain.org"
    },
    "DistributorOrgMSP": {
        "org_name": "TransGlobal Cold-Chain Logistics",
        "role": "DISTRIBUTOR",
        "msp_id": "DistributorOrgMSP",
        "secret_key": "dist_priv_key_secure_supplychain_seed_391054",
        "public_key": "dist_pub_key_transglobal_x509_cert_v1",
        "certificate_id": "CERT-DIST-7789-X509",
        "domain": "logistics.supplychain.org"
    },
    "RetailerOrgMSP": {
        "org_name": "MetroFresh Hypermarkets Corp.",
        "role": "RETAILER",
        "msp_id": "RetailerOrgMSP",
        "secret_key": "retail_priv_key_secure_supplychain_seed_602941",
        "public_key": "retail_pub_key_metrofresh_x509_cert_v1",
        "certificate_id": "CERT-RETAIL-1123-X509",
        "domain": "retail.supplychain.org"
    },
    "RegulatorOrgMSP": {
        "org_name": "National Agricultural & Food Safety Authority",
        "role": "REGULATOR",
        "msp_id": "RegulatorOrgMSP",
        "secret_key": "reg_priv_key_secure_supplychain_seed_104829",
        "public_key": "reg_pub_key_nafs_regulator_x509_cert_v1",
        "certificate_id": "CERT-REGULATOR-0001-X509",
        "domain": "safety.regulator.gov"
    },
    "OrdererMSP": {
        "org_name": "Consortium Raft Ordering Service",
        "role": "ADMIN",
        "msp_id": "OrdererMSP",
        "secret_key": "orderer_priv_key_secure_supplychain_seed_002914",
        "public_key": "orderer_pub_key_consortium_x509_cert_v1",
        "certificate_id": "CERT-ORDERER-ROOT-X509",
        "domain": "orderers.supplychain.net"
    }
}


def canonical_json_bytes(data: Any) -> bytes:
    """Produces deterministic serialized byte representation for cryptographic signing."""
    return json.dumps(data, sort_keys=True, separators=(',', ':')).encode('utf-8')


def sha256_hex(data: bytes) -> str:
    """Returns SHA-256 hash in hexadecimal format."""
    return hashlib.sha256(data).hexdigest()


def sign_payload(msp_id: str, payload: Any) -> str:
    """
    Signs canonical JSON payload using the organization's private cryptographic key.
    Generates a secure HMAC-SHA256 signature simulating an X.509 ECDSA certificate signature.
    """
    org = ORGANIZATIONS.get(msp_id)
    if not org:
        raise ValueError(f"Unknown MSP identity: {msp_id}")
    
    secret = org["secret_key"].encode('utf-8')
    data_bytes = canonical_json_bytes(payload)
    sig_bytes = hmac.new(secret, data_bytes, hashlib.sha256).digest()
    return base64.b64encode(sig_bytes).decode('utf-8')


def verify_signature(msp_id: str, payload: Any, signature_b64: str) -> bool:
    """
    Verifies that a transaction payload was signed by the holder of the MSP identity's key.
    """
    org = ORGANIZATIONS.get(msp_id)
    if not org:
        return False
    try:
        expected_sig = sign_payload(msp_id, payload)
        return hmac.compare_digest(expected_sig, signature_b64)
    except Exception:
        return False


def get_msp_info(msp_id: str) -> Optional[Dict[str, Any]]:
    """Returns public certificate and organization metadata for a given MSP."""
    org = ORGANIZATIONS.get(msp_id)
    if not org:
        return None
    return {
        "msp_id": org["msp_id"],
        "org_name": org["org_name"],
        "role": org["role"],
        "public_key": org["public_key"],
        "certificate_id": org["certificate_id"],
        "domain": org["domain"]
    }


def list_organizations() -> Dict[str, Dict[str, Any]]:
    """Returns all registered consortium organizations with public identities."""
    return {
        msp: {
            "msp_id": data["msp_id"],
            "org_name": data["org_name"],
            "role": data["role"],
            "certificate_id": data["certificate_id"],
            "domain": data["domain"]
        }
        for msp, data in ORGANIZATIONS.items()
    }
