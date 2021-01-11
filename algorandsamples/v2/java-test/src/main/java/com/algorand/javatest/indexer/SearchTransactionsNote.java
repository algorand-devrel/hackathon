package com.algorand.javatest.indexer;

import com.algorand.algosdk.v2.client.common.Client;
import com.algorand.algosdk.v2.client.common.IndexerClient;
import com.algorand.algosdk.v2.client.common.Response;
import com.algorand.algosdk.v2.client.model.TransactionsResponse;

import org.json.JSONObject;

public class SearchTransactionsNote {
    /**
     * Initialize connection to indexer.
     */
    private static IndexerClient connectToNetwork() {
        final String INDEXER_API_ADDR = "localhost";
        final int INDEXER_API_PORT = 8981;
        return new IndexerClient(INDEXER_API_ADDR, INDEXER_API_PORT);
    }

    /**
     * Indexer search transaction notes example.
     */
    public static void main(String args[]) throws Exception {
        IndexerClient indexerClientInstance = connectToNetwork();
        Response<TransactionsResponse> resp = indexerClientInstance.searchForTransactions()
                .notePrefix("showing prefix".getBytes())
                .minRound(11551185L)
                .execute();
        if (!resp.isSuccessful()) {
            throw new Exception(resp.message());
        }

        // pretty print json
        JSONObject jsonObj = new JSONObject(resp.toString());
        System.out.println("Transaction Info: " + jsonObj.toString(2));

        int i = 0;
        for (Transaction tx : resp.body().transactions) {
            i++;
            System.out.println("Transaction " + i);
            System.out.println("  Note Info: " + new String(tx.note));
        }
    }
}
