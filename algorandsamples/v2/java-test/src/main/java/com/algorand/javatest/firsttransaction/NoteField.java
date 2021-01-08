package com.algorand.javatest.firsttransaction;

import com.algorand.algosdk.account.Account;
import com.algorand.algosdk.crypto.Address;
import com.algorand.algosdk.transaction.SignedTransaction;
import com.algorand.algosdk.transaction.Transaction;
import com.algorand.algosdk.util.Encoder;
import com.algorand.algosdk.v2.client.common.AlgodClient;
import com.algorand.algosdk.v2.client.common.Response;
import com.algorand.algosdk.v2.client.model.NodeStatusResponse;
import com.algorand.algosdk.v2.client.model.PendingTransactionResponse;
import com.algorand.algosdk.v2.client.model.PostTransactionsResponse;
import com.algorand.algosdk.v2.client.model.TransactionParametersResponse;
import org.json.JSONObject;

public class NoteField {
    public AlgodClient client = null;
    // String[] headers = { "X-API-Key" };
    // String[] values = { "B3SU4KcVKi94Jap2VXkK83xx38bsv95K5UZm2lab" };

    // utility function to connect to a node
    private AlgodClient connectToNetwork() {

        // Initialize an algod client
        final String ALGOD_API_ADDR = "localhost";
        final Integer ALGOD_PORT = 4001;
        final String ALGOD_API_TOKEN = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa";
        AlgodClient client = new AlgodClient(ALGOD_API_ADDR, ALGOD_PORT, ALGOD_API_TOKEN);
        return client;
    }

    // utility function to wait on a transaction to be confirmed
    public PendingTransactionResponse waitForConfirmation(AlgodClient myclient, String txID, Integer timeout)
            throws Exception {
        PendingTransactionResponse pendingInfo = null;
        if (myclient == null || txID == null || timeout < 0) {
            throw new IllegalArgumentException("Bad arguments for waitForConfirmation.");
        }
        Response<NodeStatusResponse> resp = myclient.GetStatus().execute();
        if (!resp.isSuccessful()) {
            throw new Exception(resp.message());
        }
        NodeStatusResponse nodeStatusResponse = resp.body();
        Long startRound = nodeStatusResponse.lastRound;
        Long currentRound = startRound;
        while (currentRound < (startRound + timeout)) { 
                // Check the pending transactions                 
                Response<PendingTransactionResponse> resp2 = myclient.PendingTransactionInformation(txID).execute();
                if (resp2.isSuccessful()) {
                    pendingInfo = resp2.body();               
                    if (pendingInfo != null) {
                        if (pendingInfo.confirmedRound != null && pendingInfo.confirmedRound > 0) {
                            // Got the completed Transaction
                            return pendingInfo;                     
                        }
                        if (pendingInfo.poolError != null && pendingInfo.poolError.length() > 0) {
                            // If there was a pool error, then the transaction has been rejected!
                            throw new Exception("There was a pool error, then the transaction has been rejected!");
                        }
                    }
                }
                currentRound++;            
                Response<NodeStatusResponse> resp3 = myclient.WaitForBlock(currentRound).execute();
                if (!resp3.isSuccessful()) {
                    throw new Exception(resp3.message());
                }       
        }
        throw new Exception("Could not find transaction!");
    }

    public void gettingStartedNoteFieldExample() throws Exception {

        if (client == null)
            this.client = connectToNetwork();

        // Import your private key mnemonic and address
        final String PASSPHRASE = "patrol target joy dial ethics flip usual fatigue bulb security prosper brand coast arch casino burger inch cricket scissors shoe evolve eternal calm absorb school";
        com.algorand.algosdk.account.Account myAccount = new Account(PASSPHRASE);
        System.out.println("My Address: " + myAccount.getAddress());

        String myAddress = printBalance(myAccount);

        // Construct the transaction
        final String RECEIVER = "L5EUPCF4ROKNZMAE37R5FY2T5DF2M3NVYLPKSGWTUKVJRUGIW4RKVPNPD4";
        // add some notes to the transaction
        String note = "showing prefix and more";


        Transaction txn = Transaction.PaymentTransactionBuilder()
                .sender(myAddress)
                .note(note.getBytes())
                .amount(100000)
                .receiver(RECEIVER)
                .lookupParams(client)
                .build();

        // Sign the transaction
        SignedTransaction signedTxn = myAccount.signTransaction(txn);
        System.out.println("Signed transaction with txid: " + signedTxn.transactionID);

        // Submit the transaction to the network
        byte[] encodedTxBytes = Encoder.encodeToMsgPack(signedTxn);
        Response<PostTransactionsResponse> resp = client.RawTransaction().rawtxn(encodedTxBytes).execute();
        if (!resp.isSuccessful()) {
            throw new Exception(resp.message());
        }
        String id = resp.body().txId;

        // Wait for transaction confirmation
        PendingTransactionResponse pTrx = waitForConfirmation(client, id, 4);

        System.out.println("Transaction " + id + " confirmed in round " + pTrx.confirmedRound);
        // Read the transaction
        JSONObject jsonObj = new JSONObject(pTrx.toString());
        System.out.println("Transaction information (with notes): " + jsonObj.toString(2));
        System.out.println("Decoded note: " + new String(pTrx.txn.tx.note));
        myAddress = printBalance(myAccount);
    }

    private String printBalance(com.algorand.algosdk.account.Account myAccount) throws Exception {
        String myAddress = myAccount.getAddress().toString();

        Response<com.algorand.algosdk.v2.client.model.Account> resp = client.AccountInformation(myAccount.getAddress())
                .execute();
        if (!resp.isSuccessful()) {
            throw new Exception(resp.message());
        }
        com.algorand.algosdk.v2.client.model.Account accountInfo = resp.body();
        System.out.println(String.format("Account Balance: %d microAlgos", accountInfo.amount));
        return myAddress;
    }

    public static void main(String args[]) throws Exception {
        NoteField t = new NoteField();
        t.gettingStartedNoteFieldExample();
    }
}