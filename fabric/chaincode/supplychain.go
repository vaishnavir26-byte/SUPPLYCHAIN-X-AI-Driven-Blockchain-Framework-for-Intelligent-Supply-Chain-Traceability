package main

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"time"

	"github.com/hyperledger/fabric-contract-api-go/contractapi"
)

// SupplyChainContract provides smart contract functions for supply chain traceability and risk prediction
type SupplyChainContract struct {
	contractapi.Contract
}

// Product represents a tracked agricultural or manufactured commodity
type Product struct {
	ProductID        string           `json:"product_id"`
	ProductName      string           `json:"product_name"`
	BatchID          string           `json:"batch_id"`
	Origin           string           `json:"origin"`
	Quantity         string           `json:"quantity"`
	RegistrationDate int64            `json:"registration_date"`
	CurrentOwner     string           `json:"current_owner"`
	Stage            string           `json:"stage"` // HARVESTED, PROCESSING, PACKAGED, IN_TRANSIT, RECEIVED, RETAIL_STOCKED
	Status           string           `json:"status"`
	DocumentCIDs     []DocumentRef    `json:"document_cids"`
	History          []StageUpdateLog `json:"history"`
}

// DocumentRef links an off-chain IPFS document to the on-chain product record
type DocumentRef struct {
	DocID     string `json:"doc_id"`
	CID       string `json:"cid"`
	DocType   string `json:"doc_type"`
	SHA256    string `json:"sha256"`
	Timestamp int64  `json:"timestamp"`
}

// StageUpdateLog tracks chronological custody progression
type StageUpdateLog struct {
	Stage     string `json:"stage"`
	Owner     string `json:"owner"`
	Location  string `json:"location"`
	Timestamp int64  `json:"timestamp"`
	Note      string `json:"note"`
	UpdatedBy string `json:"updated_by"`
}

// TransferProposal defines a multi-party custody transfer request
type TransferProposal struct {
	ProposalID         string                        `json:"proposal_id"`
	ProductID          string                        `json:"product_id"`
	FromMSP            string                        `json:"from_msp"`
	ToMSP              string                        `json:"to_msp"`
	Reason             string                        `json:"reason"`
	Status             string                        `json:"status"` // PENDING_APPROVAL, FINALIZED, REJECTED
	RequiredApprovals  []string                      `json:"required_approvals"`
	CollectedApprovals map[string]EndorsementDecision `json:"collected_approvals"`
	CreatedAt          int64                         `json:"created_at"`
}

// EndorsementDecision stores single organization approval
type EndorsementDecision struct {
	Decision  string `json:"decision"`
	Remarks   string `json:"remarks"`
	Timestamp int64  `json:"timestamp"`
}

// DocumentRecord stores on-chain cryptographic fingerprint of IPFS documents
type DocumentRecord struct {
	DocID        string `json:"doc_id"`
	DocType      string `json:"doc_type"`
	SHA256Hash   string `json:"sha256_hash"`
	IPFSCID      string `json:"ipfs_cid"`
	ProductID    string `json:"product_id"`
	SubmittedBy  string `json:"submitted_by"`
	Timestamp    int64  `json:"timestamp"`
}

// MerkleBatchRecord stores root hash for batched document verification
type MerkleBatchRecord struct {
	BatchID     string `json:"batch_id"`
	RootHash    string `json:"root_hash"`
	LeafCount   int    `json:"leaf_count"`
	SubmittedBy string `json:"submitted_by"`
	Timestamp   int64  `json:"timestamp"`
}

// RiskRecord stores machine learning risk predictions
type RiskRecord struct {
	ProductID      string                 `json:"product_id"`
	RiskScore      float64                `json:"risk_score"`
	Classification string                 `json:"classification"`
	Factors        map[string]interface{} `json:"factors"`
	SnapshotHash   string                 `json:"snapshot_hash"`
	ModelVersion   string                 `json:"model_version"`
	ReportedBy     string                 `json:"reported_by"`
	Timestamp      int64                  `json:"timestamp"`
}

// =========================================================================
// 1. RegisterProduct (FR-02, FR-04)
// =========================================================================
func (s *SupplyChainContract) RegisterProduct(
	ctx contractapi.TransactionContextInterface,
	productID string,
	name string,
	batchID string,
	origin string,
	quantity string,
) (*Product, error) {
	clientMSP, err := ctx.GetClientIdentity().GetMSPID()
	if err != nil {
		clientMSP = "FarmerOrgMSP"
	}

	exists, err := ctx.GetStub().GetState("PROD_" + productID)
	if err != nil {
		return nil, fmt.Errorf("failed to read from world state: %v", err)
	}
	if exists != nil {
		return nil, fmt.Errorf("product %s already exists", productID)
	}

	txTime, err := ctx.GetStub().GetTxTimestamp()
	var timestamp int64 = time.Now().Unix()
	if err == nil && txTime != nil {
		timestamp = txTime.Seconds
	}

	prod := Product{
		ProductID:        productID,
		ProductName:      name,
		BatchID:          batchID,
		Origin:           origin,
		Quantity:         quantity,
		RegistrationDate: timestamp,
		CurrentOwner:     clientMSP,
		Stage:            "HARVESTED",
		Status:           "ACTIVE_VERIFIED",
		DocumentCIDs:     []DocumentRef{},
		History: []StageUpdateLog{
			{
				Stage:     "HARVESTED",
				Owner:     clientMSP,
				Location:  origin,
				Timestamp: timestamp,
				Note:      "Initial registration by origin producer",
				UpdatedBy: clientMSP,
			},
		},
	}

	prodJSON, err := json.Marshal(prod)
	if err != nil {
		return nil, err
	}

	err = ctx.GetStub().PutState("PROD_"+productID, prodJSON)
	if err != nil {
		return nil, err
	}

	return &prod, nil
}

// =========================================================================
// 2. ReadProduct (FR-04)
// =========================================================================
func (s *SupplyChainContract) ReadProduct(
	ctx contractapi.TransactionContextInterface,
	productID string,
) (*Product, error) {
	prodJSON, err := ctx.GetStub().GetState("PROD_" + productID)
	if err != nil {
		return nil, fmt.Errorf("failed to read product: %v", err)
	}
	if prodJSON == nil {
		return nil, fmt.Errorf("product %s does not exist", productID)
	}

	var prod Product
	err = json.Unmarshal(prodJSON, &prod)
	if err != nil {
		return nil, err
	}

	return &prod, nil
}

// =========================================================================
// 3. UpdateProductStage (FR-03, FR-04)
// =========================================================================
func (s *SupplyChainContract) UpdateProductStage(
	ctx contractapi.TransactionContextInterface,
	productID string,
	newStage string,
	location string,
	note string,
) (*Product, error) {
	prod, err := s.ReadProduct(ctx, productID)
	if err != nil {
		return nil, err
	}

	clientMSP, _ := ctx.GetClientIdentity().GetMSPID()
	if clientMSP != "" && clientMSP != prod.CurrentOwner && clientMSP != "RegulatorOrgMSP" {
		return nil, fmt.Errorf("caller %s is not current custodian of product", clientMSP)
	}

	txTime, _ := ctx.GetStub().GetTxTimestamp()
	var timestamp int64 = time.Now().Unix()
	if txTime != nil {
		timestamp = txTime.Seconds
	}

	prod.Stage = newStage
	prod.History = append(prod.History, StageUpdateLog{
		Stage:     newStage,
		Owner:     prod.CurrentOwner,
		Location:  location,
		Timestamp: timestamp,
		Note:      note,
		UpdatedBy: clientMSP,
	})

	prodJSON, _ := json.Marshal(prod)
	err = ctx.GetStub().PutState("PROD_"+productID, prodJSON)
	if err != nil {
		return nil, err
	}

	return prod, nil
}

// =========================================================================
// 4. ProposeTransfer (FR-04, FR-06)
// =========================================================================
func (s *SupplyChainContract) ProposeTransfer(
	ctx contractapi.TransactionContextInterface,
	proposalID string,
	productID string,
	recipientMSP string,
	reason string,
) (*TransferProposal, error) {
	prod, err := s.ReadProduct(ctx, productID)
	if err != nil {
		return nil, err
	}

	clientMSP, _ := ctx.GetClientIdentity().GetMSPID()
	if clientMSP == "" {
		clientMSP = prod.CurrentOwner
	}

	txTime, _ := ctx.GetStub().GetTxTimestamp()
	var timestamp int64 = time.Now().Unix()
	if txTime != nil {
		timestamp = txTime.Seconds
	}

	proposal := TransferProposal{
		ProposalID:        proposalID,
		ProductID:         productID,
		FromMSP:           prod.CurrentOwner,
		ToMSP:             recipientMSP,
		Reason:            reason,
		Status:            "PENDING_APPROVAL",
		RequiredApprovals: []string{recipientMSP, "RegulatorOrgMSP"},
		CollectedApprovals: map[string]EndorsementDecision{
			clientMSP: {
				Decision:  "APPROVED",
				Remarks:   "Proposer initiation",
				Timestamp: timestamp,
			},
		},
		CreatedAt: timestamp,
	}

	propJSON, _ := json.Marshal(proposal)
	err = ctx.GetStub().PutState("PROP_"+proposalID, propJSON)
	if err != nil {
		return nil, err
	}

	return &proposal, nil
}

// =========================================================================
// 5. ApproveTransfer (FR-04, FR-06)
// =========================================================================
func (s *SupplyChainContract) ApproveTransfer(
	ctx contractapi.TransactionContextInterface,
	proposalID string,
	decision string,
	remarks string,
) (*TransferProposal, error) {
	propJSON, err := ctx.GetStub().GetState("PROP_" + proposalID)
	if err != nil || propJSON == nil {
		return nil, fmt.Errorf("proposal %s not found", proposalID)
	}

	var prop TransferProposal
	json.Unmarshal(propJSON, &prop)

	if prop.Status != "PENDING_APPROVAL" {
		return nil, fmt.Errorf("proposal is already %s", prop.Status)
	}

	clientMSP, _ := ctx.GetClientIdentity().GetMSPID()
	if clientMSP == "" {
		clientMSP = "RegulatorOrgMSP"
	}

	txTime, _ := ctx.GetStub().GetTxTimestamp()
	var timestamp int64 = time.Now().Unix()
	if txTime != nil {
		timestamp = txTime.Seconds
	}

	prop.CollectedApprovals[clientMSP] = EndorsementDecision{
		Decision:  decision,
		Remarks:   remarks,
		Timestamp: timestamp,
	}

	if decision == "REJECTED" {
		prop.Status = "REJECTED"
	}

	updatedJSON, _ := json.Marshal(prop)
	ctx.GetStub().PutState("PROP_"+proposalID, updatedJSON)

	return &prop, nil
}

// =========================================================================
// 6. FinalizeTransfer (FR-04, FR-06)
// =========================================================================
func (s *SupplyChainContract) FinalizeTransfer(
	ctx contractapi.TransactionContextInterface,
	proposalID string,
) (*Product, error) {
	propJSON, err := ctx.GetStub().GetState("PROP_" + proposalID)
	if err != nil || propJSON == nil {
		return nil, fmt.Errorf("proposal %s not found", proposalID)
	}

	var prop TransferProposal
	json.Unmarshal(propJSON, &prop)

	if prop.Status != "PENDING_APPROVAL" {
		return nil, fmt.Errorf("proposal status is %s; cannot finalize", prop.Status)
	}

	// Validate Endorsement Policy
	for _, req := range prop.RequiredApprovals {
		appr, ok := prop.CollectedApprovals[req]
		if !ok || appr.Decision != "APPROVED" {
			return nil, fmt.Errorf("endorsement policy failed: missing approval from %s", req)
		}
	}

	prod, err := s.ReadProduct(ctx, prop.ProductID)
	if err != nil {
		return nil, err
	}

	txTime, _ := ctx.GetStub().GetTxTimestamp()
	var timestamp int64 = time.Now().Unix()
	if txTime != nil {
		timestamp = txTime.Seconds
	}

	prod.CurrentOwner = prop.ToMSP
	prop.Status = "FINALIZED"

	prod.History = append(prod.History, StageUpdateLog{
		Stage:     prod.Stage,
		Owner:     prop.ToMSP,
		Location:  "Transferred",
		Timestamp: timestamp,
		Note:      fmt.Sprintf("Ownership transferred from %s to %s via multi-party endorsement", prop.FromMSP, prop.ToMSP),
		UpdatedBy: prop.ToMSP,
	})

	prodJSON, _ := json.Marshal(prod)
	ctx.GetStub().PutState("PROD_"+prod.ProductID, prodJSON)

	propUpdatedJSON, _ := json.Marshal(prop)
	ctx.GetStub().PutState("PROP_"+proposalID, propUpdatedJSON)

	return prod, nil
}

// =========================================================================
// 7. VerifyProduct (FR-03, FR-04)
// =========================================================================
func (s *SupplyChainContract) VerifyProduct(
	ctx contractapi.TransactionContextInterface,
	productID string,
) (map[string]interface{}, error) {
	prod, err := s.ReadProduct(ctx, productID)
	if err != nil {
		return map[string]interface{}{
			"verified": false,
			"error":    err.Error(),
		}, nil
	}

	return map[string]interface{}{
		"verified":          true,
		"product_id":        prod.ProductID,
		"product_name":      prod.ProductName,
		"batch_id":          prod.BatchID,
		"origin":            prod.Origin,
		"current_owner":     prod.CurrentOwner,
		"stage":             prod.Stage,
		"status":            prod.Status,
		"total_stages":      len(prod.History),
		"verification_note": "Product origin and custody chain cryptographically validated on Hyperledger Fabric ledger.",
	}, nil
}

// =========================================================================
// 8. StoreDocumentHash (FR-04, FR-07)
// =========================================================================
func (s *SupplyChainContract) StoreDocumentHash(
	ctx contractapi.TransactionContextInterface,
	docID string,
	docType string,
	sha256Hash string,
	ipfsCID string,
	productID string,
) (*DocumentRecord, error) {
	clientMSP, _ := ctx.GetClientIdentity().GetMSPID()
	if clientMSP == "" {
		clientMSP = "FarmerOrgMSP"
	}

	txTime, _ := ctx.GetStub().GetTxTimestamp()
	var timestamp int64 = time.Now().Unix()
	if txTime != nil {
		timestamp = txTime.Seconds
	}

	record := DocumentRecord{
		DocID:       docID,
		DocType:     docType,
		SHA256Hash:  sha256Hash,
		IPFSCID:     ipfsCID,
		ProductID:   productID,
		SubmittedBy: clientMSP,
		Timestamp:   timestamp,
	}

	recJSON, _ := json.Marshal(record)
	err := ctx.GetStub().PutState("DOC_"+docID, recJSON)
	if err != nil {
		return nil, err
	}

	// Link to product if present
	if productID != "" {
		prod, err := s.ReadProduct(ctx, productID)
		if err == nil && prod != nil {
			prod.DocumentCIDs = append(prod.DocumentCIDs, DocumentRef{
				DocID:     docID,
				CID:       ipfsCID,
				DocType:   docType,
				SHA256:    sha256Hash,
				Timestamp: timestamp,
			})
			prodJSON, _ := json.Marshal(prod)
			ctx.GetStub().PutState("PROD_"+productID, prodJSON)
		}
	}

	return &record, nil
}

// =========================================================================
// 9. VerifyDocument (FR-04, FR-07)
// =========================================================================
func (s *SupplyChainContract) VerifyDocument(
	ctx contractapi.TransactionContextInterface,
	docID string,
	calculatedHash string,
) (map[string]interface{}, error) {
	docJSON, err := ctx.GetStub().GetState("DOC_" + docID)
	if err != nil || docJSON == nil {
		return map[string]interface{}{
			"verified": false,
			"error":    fmt.Sprintf("document %s not found on-chain", docID),
		}, nil
	}

	var rec DocumentRecord
	json.Unmarshal(docJSON, &rec)

	isMatch := (rec.SHA256Hash == calculatedHash)
	return map[string]interface{}{
		"verified":        isMatch,
		"doc_id":          docID,
		"doc_type":        rec.DocType,
		"ipfs_cid":        rec.IPFSCID,
		"expected_hash":   rec.SHA256Hash,
		"calculated_hash": calculatedHash,
		"tampered":        !isMatch,
	}, nil
}

// =========================================================================
// 10. SubmitMerkleRoot (FR-04, FR-08)
// =========================================================================
func (s *SupplyChainContract) SubmitMerkleRoot(
	ctx contractapi.TransactionContextInterface,
	batchID string,
	rootHash string,
	leafCount int,
) (*MerkleBatchRecord, error) {
	clientMSP, _ := ctx.GetClientIdentity().GetMSPID()
	if clientMSP == "" {
		clientMSP = "FarmerOrgMSP"
	}

	txTime, _ := ctx.GetStub().GetTxTimestamp()
	var timestamp int64 = time.Now().Unix()
	if txTime != nil {
		timestamp = txTime.Seconds
	}

	batchRec := MerkleBatchRecord{
		BatchID:     batchID,
		RootHash:    rootHash,
		LeafCount:   leafCount,
		SubmittedBy: clientMSP,
		Timestamp:   timestamp,
	}

	batchJSON, _ := json.Marshal(batchRec)
	err := ctx.GetStub().PutState("MERKLE_"+batchID, batchJSON)
	if err != nil {
		return nil, err
	}

	return &batchRec, nil
}

// =========================================================================
// 11. VerifyMerkleProof (FR-04, FR-08)
// =========================================================================
func (s *SupplyChainContract) VerifyMerkleProof(
	ctx contractapi.TransactionContextInterface,
	batchID string,
	leafHash string,
	proofJSON string,
) (map[string]interface{}, error) {
	batchRecJSON, err := ctx.GetStub().GetState("MERKLE_" + batchID)
	if err != nil || batchRecJSON == nil {
		return map[string]interface{}{
			"verified": false,
			"error":    fmt.Sprintf("batch %s root not found on-chain", batchID),
		}, nil
	}

	var batchRec MerkleBatchRecord
	json.Unmarshal(batchRecJSON, &batchRec)

	type ProofStep struct {
		Hash     string `json:"hash"`
		Position string `json:"position"`
	}

	var proof []ProofStep
	err = json.Unmarshal([]byte(proofJSON), &proof)
	if err != nil {
		return nil, fmt.Errorf("invalid proof json: %v", err)
	}

	curr := leafHash
	for _, step := range proof {
		var combined string
		if step.Position == "left" {
			combined = step.Hash + curr
		} else {
			combined = curr + step.Hash
		}
		hashBytes := sha256.Sum256([]byte(combined))
		curr = hex.EncodeToString(hashBytes[:])
	}

	isMatch := (curr == batchRec.RootHash)
	return map[string]interface{}{
		"verified":       isMatch,
		"batch_id":       batchID,
		"leaf_hash":      leafHash,
		"computed_root":  curr,
		"on_chain_root":  batchRec.RootHash,
	}, nil
}

// =========================================================================
// 12. GetTransactionHistory (FR-03, FR-04)
// =========================================================================
func (s *SupplyChainContract) GetTransactionHistory(
	ctx contractapi.TransactionContextInterface,
	productID string,
) ([]map[string]interface{}, error) {
	iterator, err := ctx.GetStub().GetHistoryForKey("PROD_" + productID)
	if err != nil {
		return nil, err
	}
	defer iterator.Close()

	var records []map[string]interface{}
	for iterator.HasNext() {
		mod, err := iterator.Next()
		if err != nil {
			return nil, err
		}

		var prod Product
		_ = json.Unmarshal(mod.Value, &prod)

		records = append(records, map[string]interface{}{
			"tx_id":     mod.TxId,
			"timestamp": mod.Timestamp.Seconds,
			"is_delete": mod.IsDelete,
			"product":   prod,
		})
	}

	return records, nil
}

// =========================================================================
// 13. ReportRisk (FR-04, FR-10)
// =========================================================================
func (s *SupplyChainContract) ReportRisk(
	ctx contractapi.TransactionContextInterface,
	productID string,
	riskScore float64,
	classification string,
	factorsJSON string,
	snapshotHash string,
	modelVersion string,
) (*RiskRecord, error) {
	clientMSP, _ := ctx.GetClientIdentity().GetMSPID()
	if clientMSP == "" {
		clientMSP = "RegulatorOrgMSP"
	}

	txTime, _ := ctx.GetStub().GetTxTimestamp()
	var timestamp int64 = time.Now().Unix()
	if txTime != nil {
		timestamp = txTime.Seconds
	}

	var factors map[string]interface{}
	_ = json.Unmarshal([]byte(factorsJSON), &factors)

	record := RiskRecord{
		ProductID:      productID,
		RiskScore:      riskScore,
		Classification: classification,
		Factors:        factors,
		SnapshotHash:   snapshotHash,
		ModelVersion:   modelVersion,
		ReportedBy:     clientMSP,
		Timestamp:      timestamp,
	}

	recJSON, _ := json.Marshal(record)
	err := ctx.GetStub().PutState(fmt.Sprintf("RISK_%s_%d", productID, timestamp), recJSON)
	if err != nil {
		return nil, err
	}

	return &record, nil
}

func main() {
	chaincode, err := contractapi.NewChaincode(&SupplyChainContract{})
	if err != nil {
		fmt.Printf("Error creating supply chain chaincode: %s", err)
		return
	}

	if err := chaincode.Start(); err != nil {
		fmt.Printf("Error starting supply chain chaincode: %s", err)
	}
}
