package com.algorand.javatest;

import java.math.BigInteger;

import com.algorand.algosdk.account.Account;
import com.algorand.algosdk.algod.client.AlgodClient;
import com.algorand.algosdk.algod.client.ApiException;
import com.algorand.algosdk.algod.client.api.AlgodApi;
import com.algorand.algosdk.algod.client.auth.ApiKeyAuth;
import com.algorand.algosdk.algod.client.model.AssetHolding;
import com.algorand.algosdk.algod.client.model.AssetParams;
import com.algorand.algosdk.algod.client.model.TransactionID;
import com.algorand.algosdk.algod.client.model.TransactionParams;
import com.algorand.algosdk.crypto.Address;
import com.algorand.algosdk.crypto.Digest;
import com.algorand.algosdk.transaction.SignedTransaction;
import com.algorand.algosdk.transaction.Transaction;
import com.algorand.algosdk.util.Encoder;

/**
 * Show Creating, modifying, sending and listing assets
 */
public class TutorialAssetExample {

    public AlgodApi algodApiInstance = null;

    // utility function to connect to a node
    private AlgodApi connectToNetwork(){

        // hackathon / workshop
        // final String ALGOD_API_ADDR = "http://hackathon.algodev.network:9100";
        // final String ALGOD_API_TOKEN = "ef920e2e7e002953f4b29a8af720efe8e4ecc75ff102b165e0472834b25832c1";
  
        // your own node
        // final String ALGOD_API_ADDR = "http://127.0.0.1:8080";
        // final String ALGOD_API_TOKEN = "your token in your node/data/algod.token file";

        //sandbox
        final String ALGOD_API_ADDR = "http://localhost:4001";
        final String ALGOD_API_TOKEN = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa";

        // Purestake
        // final String ALGOD_API_ADDR =
        // "https://testnet-algorand.api.purestake.io/ps1";
        // final String ALGOD_API_TOKEN = "B3SU4KcVKi94Jap2VXkK83xx38bsv95K5UZm2lab";

        AlgodClient client = (AlgodClient) new AlgodClient().setBasePath(ALGOD_API_ADDR);
        ApiKeyAuth api_key = (ApiKeyAuth) client.getAuthentication("api_key");
        api_key.setApiKey(ALGOD_API_TOKEN);
        algodApiInstance = new AlgodApi(client);   
        return algodApiInstance;
    }

    // Inline class to handle changing block parameters
    // Throughout the example
    public class ChangingBlockParms {
        public BigInteger fee;
        public BigInteger firstRound;
        public BigInteger lastRound;
        public String genID;
        public Digest genHash;

        public ChangingBlockParms() {
            this.fee = BigInteger.valueOf(0);
            this.firstRound = BigInteger.valueOf(0);
            this.lastRound = BigInteger.valueOf(0);
            this.genID = "";
            this.genHash = null;
        }
    };

    // Utility function to wait on a transaction to be confirmed
    public void waitForConfirmation(String txID) throws Exception {
        if (algodApiInstance == null)
            connectToNetwork();
        while (true) {
            try {
                // Check the pending tranactions
                com.algorand.algosdk.algod.client.model.Transaction pendingInfo = algodApiInstance
                        .pendingTransactionInformation(txID);
                if (pendingInfo.getRound() != null && pendingInfo.getRound().longValue() > 0) {
                    // Got the completed Transaction
                    System.out.println("Transaction " + pendingInfo.getTx() + " confirmed in round "
                            + pendingInfo.getRound().longValue());
                    break;
                }
                algodApiInstance
                        .waitForBlock(BigInteger.valueOf(algodApiInstance.getStatus().getLastRound().longValue() + 1));
            } catch (Exception e) {
                throw (e);
            }
        }

    }

    // Utility function to update changing block parameters
    public ChangingBlockParms getChangingParms(AlgodApi algodApiInstance) throws Exception {
        ChangingBlockParms cp = new TutorialAssetExample.ChangingBlockParms();
        try {
            TransactionParams params = algodApiInstance.transactionParams();
            cp.fee = params.getFee();
            cp.firstRound = params.getLastRound();
            cp.lastRound = cp.firstRound.add(BigInteger.valueOf(1000));
            cp.genID = params.getGenesisID();
            cp.genHash = new Digest(params.getGenesishashb64());

        } catch (ApiException e) {
            throw (e);
        }
        return (cp);
    }

    // Utility function for sending a raw signed transaction to the network
    public TransactionID submitTransaction(SignedTransaction signedTx) throws Exception {
        try {
            // Msgpack encode the signed transaction
            byte[] encodedTxBytes = Encoder.encodeToMsgPack(signedTx);
            TransactionID id = algodApiInstance.rawTransaction(encodedTxBytes);
            return (id);
        } catch (ApiException e) {
            throw (e);
        }
    }

    public static void main(String args[]) throws Exception {

        TutorialAssetExample ex = new TutorialAssetExample();
        AlgodApi algodApiInstance= ex.connectToNetwork();

        // recover example accounts

        // final String account1_mnemonic = "<your-25-word-mnemonic>";             
        // final String account2_mnemonic = "<your-25-word-mnemonic>";             
        // final String account3_mnemonic = "<your-25-word-mnemonic>";  

        final String account1_mnemonic = "buzz genre work meat fame favorite rookie stay tennis demand panic busy hedgehog snow morning acquire ball grain grape member blur armor foil ability seminar";             
        final String account2_mnemonic = "design country rebuild myth square resemble flock file whisper grunt hybrid floor letter pet pull hurry choice erase heart spare seven idea multiply absent seven";             
        final String account3_mnemonic = "news slide thing empower naive same belt evolve lawn ski chapter melody weasel supreme abuse main olive sudden local chat candy daughter hand able drip";  

        Account acct1  = new Account(account1_mnemonic); 
        Account acct2  = new Account(account2_mnemonic);
        Account acct3  = new Account(account3_mnemonic);                           
        System.out.println("Account1: " + acct1.getAddress());
        System.out.println("Account2: " + acct2.getAddress());
        System.out.println("Account3: " + acct3.getAddress());

        // get changing network parameters
        ChangingBlockParms cp = null;
        try {
            cp = ex.getChangingParms(algodApiInstance);
        } catch (ApiException e) {
            e.printStackTrace();
            return;
        }
        // Create the Asset:
        BigInteger assetTotal = BigInteger.valueOf(10000);
        boolean defaultFrozen = false;
        String unitName = "myunit";
        String  assetName = "my longer asset name";
        String url = "http://this.test.com";
        String assetMetadataHash = "16efaa3924a6fd9d3a4824799a4ac65d";
        Address manager  = acct2.getAddress();
        Address reserve = acct2.getAddress();
        Address freeze = acct2.getAddress();
        Address clawback = acct2.getAddress();
        Integer decimals = 0;
        Transaction tx = Transaction.createAssetCreateTransaction(acct1.getAddress(), 
            BigInteger.valueOf( 1000 ), cp.firstRound, cp.lastRound, null, cp.genID, 
            cp.genHash, assetTotal, decimals, defaultFrozen, unitName, assetName, url, 
            assetMetadataHash.getBytes(), manager, reserve, freeze, clawback);
        // Update the fee as per what the BlockChain is suggesting
        Account.setFeeByFeePerByte(tx, cp.fee);

        // Sign the Transaction with creator account
        SignedTransaction signedTx = acct1.signTransaction(tx);
        BigInteger assetID = null;
        try{
            TransactionID id = ex.submitTransaction( signedTx );
            System.out.println( "Transaction ID: " + id );
            ex.waitForConfirmation( signedTx.transactionID);
            // Now that the transaction is confirmed we can get the assetID
            com.algorand.algosdk.algod.client.model.Transaction ptx = 
                algodApiInstance.pendingTransactionInformation(id.getTxId());
            assetID = ptx.getTxresults().getCreatedasset();

        } catch (Exception e){
            e.printStackTrace();
            return;
        }
        System.out.println( "AssetID = " +  assetID);

        // Change Asset Configuration:
        // Get changing network parameters
        try {
            cp = ex.getChangingParms(algodApiInstance);
        } catch (ApiException e) {
            e.printStackTrace();
            return;
        }
        // configuration changes must be done by
        // the manager account - changing manager of the asset
        tx = Transaction.createAssetConfigureTransaction(acct2.getAddress(), 
                BigInteger.valueOf( 1000 ),cp.firstRound, cp.lastRound, null, 
                cp.genID, cp.genHash, assetID, acct1.getAddress(), reserve, 
                freeze, clawback, false);
        // update the fee as per what the BlockChain is suggesting
        Account.setFeeByFeePerByte(tx, cp.fee);
        // the transaction must be signed by the current manager account   
        signedTx = acct2.signTransaction(tx);
        // send the transaction to the network
        try{
            TransactionID id = ex.submitTransaction( signedTx );
            System.out.println( "Transaction ID: " + id );
            ex.waitForConfirmation( signedTx.transactionID);
        } catch (Exception e){
            e.printStackTrace();
            return;
        }  
        // list the asset
        AssetParams assetInfo = algodApiInstance.assetInformation(assetID);
        // the manager should now be the same as the creator
        System.out.println(assetInfo);

        // Opt in to Receiving the Asset
        try {
            cp = ex.getChangingParms(algodApiInstance);
        } catch (ApiException e) {
            e.printStackTrace();
            return;
        }
        tx = Transaction.createAssetAcceptTransaction(acct3.getAddress(), 
            BigInteger.valueOf( 1000 ), cp.firstRound, 
            cp.lastRound, null, cp.genID, cp.genHash, assetID);
        // Update the fee based on the network suggested fee
        Account.setFeeByFeePerByte(tx, cp.fee);
        // The transaction must be signed by the current manager account  
        signedTx = acct3.signTransaction(tx);
        com.algorand.algosdk.algod.client.model.Account act;
        // send the transaction to the network and
        try{
            TransactionID id = ex.submitTransaction( signedTx );
            System.out.println( "Transaction ID: " + id );
            ex.waitForConfirmation( signedTx.transactionID);
            // We can now list the account information for acct3 
            // and see that it can accept the new asseet
            act = algodApiInstance.accountInformation(acct3.getAddress().toString());
            AssetHolding ah = act.getHolding(assetID);
            System.out.println( "Asset Holding: " + ah.getAmount() );

        } catch (Exception e){
            e.printStackTrace();
            return;
        }  

        // Transfer the Asset:
        // get changing network parameters
        try {
            cp = ex.getChangingParms(algodApiInstance);
        } catch (ApiException e) {
            e.printStackTrace();
            return;
        }
        // set asset xfer specific parameters
        // We set the assetCloseTo to null so we do not close the asset out
        Address assetCloseTo = new Address();
        BigInteger assetAmount = BigInteger.valueOf(10);
        tx = Transaction.createAssetTransferTransaction(acct1.getAddress(), 
            acct3.getAddress(), assetCloseTo, assetAmount, BigInteger.valueOf( 1000 ), 
            cp.firstRound, cp.lastRound, null, cp.genID, cp.genHash, assetID);        
        // Update the fee based on the network suggested fee
        Account.setFeeByFeePerByte(tx, cp.fee);
        // The transaction must be signed by the sender account  
        signedTx = acct1.signTransaction(tx);
        // send the transaction to the network 
        try{
            TransactionID id = ex.submitTransaction( signedTx );
            System.out.println( "Transaction ID: " + id );
            ex.waitForConfirmation( signedTx.transactionID);
            // list the account information for acct3 
            // and see that it now has 5 of the new asset
            act = algodApiInstance.accountInformation(acct3.getAddress().toString());
            System.out.println( act.getHolding(assetID).getAmount() );
        } catch (Exception e){
            e.printStackTrace();
            return;
        }

        // Freeze the Asset:
        // The asset was created and configured to allow freezing an account
        try {
            cp = ex.getChangingParms(algodApiInstance);
        } catch (ApiException e) {
            e.printStackTrace();
            return;
        }
        // set asset specific parameters
        boolean freezeState = true;
        // The sender should be freeze account
        tx = Transaction.createAssetFreezeTransaction(acct2.getAddress(), 
            acct3.getAddress(), freezeState, BigInteger.valueOf( 1000 ), 
            cp.firstRound, cp.lastRound, null, cp.genHash, assetID);
        // Update the fee based on the network suggested fee
        Account.setFeeByFeePerByte(tx, cp.fee);
        // The transaction must be signed by the freeze account   
        signedTx = acct2.signTransaction(tx);
        // send the transaction to the network
        try{
            TransactionID id = ex.submitTransaction( signedTx );
            System.out.println( "Transaction ID: " + id );
            ex.waitForConfirmation(signedTx.transactionID);
        } catch (Exception e){
            e.printStackTrace();
            return;
        }

        // Revoke the asset:
        // The asset was also created with the ability for it to be revoked by 
        // clawbackaddress. 
        try {
            cp = ex.getChangingParms(algodApiInstance);
        } catch (ApiException e) {
            e.printStackTrace();
            return;
        }
        // set asset specific parameters
        assetAmount = BigInteger.valueOf( 10 );
        tx = Transaction.createAssetRevokeTransaction(acct2.getAddress(), 
            acct3.getAddress(), acct1.getAddress(), assetAmount, 
            BigInteger.valueOf( 1000 ), cp.firstRound, 
        cp.lastRound, null, cp.genID, cp.genHash, assetID);
        // Update the fee based on the network suggested fee
        Account.setFeeByFeePerByte(tx, cp.fee);
        // The transaction must be signed by the clawback account  
        signedTx = acct2.signTransaction(tx);
        // send the transaction to the network and
        // wait for the transaction to be confirmed
        try{
            TransactionID id = ex.submitTransaction( signedTx );
            System.out.println( "Transaction ID: " + id );
            ex.waitForConfirmation( signedTx.transactionID);
            // list the account information 
            act = algodApiInstance.accountInformation(acct3.getAddress().toString());
            System.out.println( act.getHolding(assetID).getAmount() );
        } catch (Exception e){
            e.printStackTrace();
            return;
        }  

        // Destroy the Asset:
        // All assets should now be back in
        // creators account
        try {
            cp = ex.getChangingParms(algodApiInstance);
        } catch (ApiException e) {
            e.printStackTrace();
            return;
        }
        // set asset specific parameters
        // The manager must sign and submit the transaction
        tx = Transaction.createAssetDestroyTransaction(acct1.getAddress(), 
                BigInteger.valueOf( 1000 ), cp.firstRound, cp.lastRound, 
                null, cp.genHash, assetID);
        // Update the fee based on the network suggested fee
        Account.setFeeByFeePerByte(tx, cp.fee);
        // The transaction must be signed by the manager account  
        signedTx = acct1.signTransaction(tx);
        // send the transaction to the network 
        try{
            TransactionID id = ex.submitTransaction( signedTx );
            System.out.println( "Transaction ID: " + id );
            ex.waitForConfirmation( signedTx.transactionID);
            // We list the account information for acct1 
            // and check that the asset is no longer exist
            
            act = algodApiInstance.accountInformation(acct1.getAddress().toString());
            // expected to be null and will cause error.
            System.out.println( "Does AssetID: " + assetID + " exist? " + 
                act.getThisassettotal().containsKey(assetID) );
        } catch (Exception e){
            e.printStackTrace();
            return;
        }  
    }
}

// resource https://developer.algorand.org/docs/features/asa/
