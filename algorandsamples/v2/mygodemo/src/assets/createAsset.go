package main

import (
	"context"
	"crypto/ed25519"
//	"encoding/base64"
	json "encoding/json"
	"fmt"

	"github.com/algorand/go-algorand-sdk/client/v2/algod"
	"github.com/algorand/go-algorand-sdk/crypto"
	"github.com/algorand/go-algorand-sdk/mnemonic"
	"github.com/algorand/go-algorand-sdk/types"
)
import transaction "github.com/algorand/go-algorand-sdk/future"

// UPDATE THESE VALUES
// const algodAddress = "Your ADDRESS"
// const algodToken = "Your TOKEN"

// sandbox
const algodAddress = "http://localhost:4001"
const algodToken = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"

// Accounts to be used through examples
func loadAccounts() (map[int][]byte, map[int]string) {
	// Shown for demonstration purposes. NEVER reveal secret mnemonics in practice.
	// Change these values to use the accounts created previously.

	// Paste in mnemonic phrases for all three accounts
	// mnemonic1 := "PASTE your phrase for account 1"
	// mnemonic2 := "PASTE your phrase for account 2"
	// mnemonic3 := "PASTE your phrase for account 3"

	mnemonic1 := "portion never forward pill lunch organ biology weird catch curve isolate plug innocent skin grunt bounce clown mercy hole eagle soul chunk type absorb trim"
	mnemonic2 := "place blouse sad pigeon wing warrior wild script problem team blouse camp soldier breeze twist mother vanish public glass code arrow execute convince ability there"
	mnemonic3 := "image travel claw climb bottom spot path roast century also task cherry address curious save item clean theme amateur loyal apart hybrid steak about blanket"

	mnemonics := []string{mnemonic1, mnemonic2, mnemonic3}
	pks := map[int]string{1: "", 2: "", 3: ""}
	var sks = make(map[int][]byte)

	for i, m := range mnemonics {
		var err error
		sk, err := mnemonic.ToPrivateKey(m)
		sks[i+1] = sk
		if err != nil {
			fmt.Printf("Issue with account %d private key conversion.", i+1)
		}
		// derive public address from Secret Key.
		pk := sk.Public()
		var a types.Address
		cpk := pk.(ed25519.PublicKey)
		copy(a[:], cpk[:])
		pks[i+1] = a.String()
		fmt.Printf("Loaded Key %d: %s\n", i+1, pks[i+1])
	}
	return sks, pks
}

func waitForConfirmation(txID string, client *algod.Client) {
	status, err := client.Status().Do(context.Background())
	if err != nil {
		fmt.Printf("error getting algod status: %s\n", err)
		return
	}
	lastRound := status.LastRound
	for {
		pt, _, err := client.PendingTransactionInformation(txID).Do(context.Background())
		if err != nil {
			fmt.Printf("error getting pending transaction: %s\n", err)
			return
		}
		if pt.ConfirmedRound > 0 {
			fmt.Printf("Transaction "+txID+" confirmed in round %d\n", pt.ConfirmedRound)
			break
		}
		fmt.Printf("waiting for confirmation\n")
		lastRound++
		status, err = client.StatusAfterBlock(lastRound).Do(context.Background())
	}
}

// prettyPrint prints Go structs
func prettyPrint(data interface{}) {
	var p []byte
	//    var err := error
	p, err := json.MarshalIndent(data, "", "\t")
	if err != nil {
		fmt.Println(err)
		return
	}
	fmt.Printf("%s \n", p)
}

// printAssetHolding utility to print asset holding for account
func printAssetHolding(assetID uint64, account string, client *algod.Client) {

	act, err := client.AccountInformation(account).Do(context.Background())
	if err != nil {
		fmt.Printf("failed to get account information: %s\n", err)
		return
	}
	for _, assetholding := range act.Assets {
		if assetID == assetholding.AssetId {
			prettyPrint(assetholding)
			break
		}
	}
}

// printCreatedAsset utility to print created assert for account
func printCreatedAsset(assetID uint64, account string, client *algod.Client) {

	act, err := client.AccountInformation(account).Do(context.Background())
	if err != nil {
		fmt.Printf("failed to get account information: %s\n", err)
		return
	}
	for _, asset := range act.CreatedAssets {
		if assetID == asset.Index {
			prettyPrint(asset)
			break
		}
	}
}

// Main function to demonstrate ASA examples
func main() {

	// Initialize an algodClient
	algodClient, err := algod.MakeClient(algodAddress, algodToken)
	if err != nil {
		return
	}

	// Get network-related transaction parameters and assign
	txParams, err := algodClient.SuggestedParams().Do(context.Background())
	if err != nil {
		fmt.Printf("Error getting suggested tx params: %s\n", err)
		return
	}
	// comment out the next two (2) lines to use suggested fees
	txParams.FlatFee = true
	txParams.Fee = 1000

	// Get pre-defined set of keys for example
	sks, pks := loadAccounts()

	// Print asset info for newly created asset.
	prettyPrint(txParams)
	prettyPrint(sks)
	prettyPrint(pks)
	// note: you would not normally show secret keys for security reasons,
	// they are shown here for tutorial clarity

	// Debug console should look similar to this...

	// Loaded Key 1: THQHGD4HEESOPSJJYYF34MWKOI57HXBX4XR63EPBKCWPOJG5KUPDJ7QJCM
	// Loaded Key 2: AJNNFQN7DSR7QEY766V7JDG35OPM53ZSNF7CU264AWOOUGSZBMLMSKCRIU
	// Loaded Key 3: 3ZQ3SHCYIKSGK7MTZ7PE7S6EDOFWLKDQ6RYYVMT7OHNQ4UJ774LE52AQCU
	// {
	// 	"Fee": 1000,
	// 	"GenesisID": "betanet-v1.0",
	// 	"GenesisHash": "mFgazF+2uRS1tMiL9dsj01hJGySEmPN28B/TjjvpVW0=",
	// 	"FirstRoundValid": 4072061,
	// 	"LastRoundValid": 4073061,
	// 	"ConsensusVersion": "https://github.com/algorandfoundation/specs/tree/e5f565421d720c6f75cdd186f7098495caf9101f",
	// 	"FlatFee": true
	// }
	// {
	// 	"1": "QkWlt0yawnHOIvkgkQ3tbEo6KudsGmDRYtlQ1OeieN2Z4HMPhyEk58kpxgu+MspyO/PcN+Xj7ZHhUKz3JN1VHg==",
	// 	"2": "Lg1Ge0vafd1jv8FbrXcwDEJnbnA9kIpH68XQUoY88SUCWtLBvxyj+BMf96v0jNvrns7vMml+KmvcBZzqGlkLFg==",
	// 	"3": "iuM5VLAiDUsfFLsr0QG8d7KB1/jXdlIBeA9IKAXAoXreYbkcWEKkZX2Tz95Py8Qbi2WocPRxirJ/cdsOUT//Fg=="
	// }
	// {
	// 	"1": "THQHGD4HEESOPSJJYYF34MWKOI57HXBX4XR63EPBKCWPOJG5KUPDJ7QJCM",
	// 	"2": "AJNNFQN7DSR7QEY766V7JDG35OPM53ZSNF7CU264AWOOUGSZBMLMSKCRIU",
	// 	"3": "3ZQ3SHCYIKSGK7MTZ7PE7S6EDOFWLKDQ6RYYVMT7OHNQ4UJ774LE52AQCU"
	// }


	// CREATE ASSET

	// Construct the transaction
	// Set parameters for asset creation 
	creator := pks[1]
	assetName := "latinum"
	unitName := "latinum"
	assetURL := "https://path/to/my/asset/details"
	assetMetadataHash := "thisIsSomeLength32HashCommitment"
	defaultFrozen := false
	decimals := uint32(0)
	totalIssuance := uint64(1000)
	manager := pks[2]
	reserve := pks[2]
	freeze := pks[2]
	clawback := pks[2]
	note := []byte(nil)
	txn, err := transaction.MakeAssetCreateTxn(creator,
		note,
		txParams, totalIssuance, decimals,
		defaultFrozen, manager, reserve, freeze, clawback,
		unitName, assetName, assetURL, assetMetadataHash)

	if err != nil {
		fmt.Printf("Failed to make asset: %s\n", err)
		return
	}
	fmt.Printf("Asset created AssetName: %s\n", txn.AssetConfigTxnFields.AssetParams.AssetName)
	// sign the transaction
	txid, stx, err := crypto.SignTransaction(sks[1], txn)
	if err != nil {
		fmt.Printf("Failed to sign transaction: %s\n", err)
		return
	}
	fmt.Printf("Transaction ID: %s\n", txid)
	// Broadcast the transaction to the network
	sendResponse, err := algodClient.SendRawTransaction(stx).Do(context.Background())
	if err != nil {
		fmt.Printf("failed to send transaction: %s\n", err)
		return
	}
	fmt.Printf("Submitted transaction %s\n", sendResponse)
	// Wait for transaction to be confirmed
	waitForConfirmation(txid, algodClient)
	//    response := algodClient.PendingTransactionInformation(txid)
	//    prettyPrint(response)
	// Retrieve asset ID by grabbing the max asset ID
	// from the creator account's holdings.
	act, err := algodClient.AccountInformation(pks[1]).Do(context.Background())
	if err != nil {
		fmt.Printf("failed to get account information: %s\n", err)
		return
	}

	assetID := uint64(0)
	//	find newest (highest) asset for this account
	for _, asset := range act.CreatedAssets {
		if asset.Index > assetID {
			assetID = asset.Index
		}
	}

	// print created asset and asset holding info for this asset
	fmt.Printf("Asset ID: %d\n", assetID)
	printCreatedAsset(assetID, pks[1], algodClient)
	printAssetHolding(assetID, pks[1], algodClient)
	
	// Your output should look similar to this...
	// Transaction YNRBKLFS2TDQDGENVWJ2SCK4EX5EG7HJ6NGJFOFGCLSTCMMXHDJA confirmed in round 4072064
	// Asset ID: 2654024
	// {
	// 	"index": 2654024,
	// 	"params": {
	// 		"clawback": "AJNNFQN7DSR7QEY766V7JDG35OPM53ZSNF7CU264AWOOUGSZBMLMSKCRIU",
	// 		"creator": "THQHGD4HEESOPSJJYYF34MWKOI57HXBX4XR63EPBKCWPOJG5KUPDJ7QJCM",
	// 		"decimals": 0,
	// 		"freeze": "AJNNFQN7DSR7QEY766V7JDG35OPM53ZSNF7CU264AWOOUGSZBMLMSKCRIU",
	// 		"manager": "AJNNFQN7DSR7QEY766V7JDG35OPM53ZSNF7CU264AWOOUGSZBMLMSKCRIU",
	// 		"metadata-hash": "dGhpc0lzU29tZUxlbmd0aDMySGFzaENvbW1pdG1lbnQ=",
	// 		"name": "latinum",
	// 		"reserve": "AJNNFQN7DSR7QEY766V7JDG35OPM53ZSNF7CU264AWOOUGSZBMLMSKCRIU",
	// 		"total": 1000,
	// 		"unit-name": "latinum",
	// 		"url": "https://path/to/my/asset/details"
	// 	}
	// }
	// {
	// 	"amount": 1000,
	// 	"asset-id": 2654024,
	// 	"creator": "THQHGD4HEESOPSJJYYF34MWKOI57HXBX4XR63EPBKCWPOJG5KUPDJ7QJCM"
	// }
}