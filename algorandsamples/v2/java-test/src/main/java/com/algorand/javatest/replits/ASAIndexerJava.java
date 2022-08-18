
package com.algorand.javatest.replits;

import com.algorand.algosdk.v2.client.common.IndexerClient;
import com.algorand.algosdk.v2.client.common.Response;
import com.algorand.algosdk.v2.client.common.Client;
import com.algorand.algosdk.crypto.Address;

import com.algorand.algosdk.v2.client.model.AssetBalancesResponse;
import com.algorand.algosdk.v2.client.model.AssetsResponse;
import com.algorand.algosdk.v2.client.model.TransactionsResponse;
import org.json.JSONObject;

// class Main on replit
public class ASAIndexerJava {
    public Client indexerInstance = null;

    // utility function to connect to a node
    private Client connectToNetwork() {
        final String INDEXER_API_ADDR = "https://algoindexer.testnet.algoexplorerapi.io/";


        
        final int INDEXER_API_PORT = 443;
        IndexerClient indexerClient = new IndexerClient(INDEXER_API_ADDR, INDEXER_API_PORT);
        return indexerClient;
    }

    public static void main(String args[]) throws Exception {
        ASAIndexerJava ex = new ASAIndexerJava();
        IndexerClient indexerClientInstance = (IndexerClient) ex.connectToNetwork();
        assetBalances(indexerClientInstance);
        searchAssetName(indexerClientInstance);
        searchTxAddressAsset(indexerClientInstance);
        searchAssets(indexerClientInstance);
    }

    public static void searchAssets(IndexerClient indexerClientInstance) throws Exception {
        System.out.println("");
        System.out.println("==> SEARCH ACCOUNTS FOR ASSET");
        Long asset_id = Long.valueOf(29340683);
        Response<AssetsResponse> response = indexerClientInstance.searchForAssets()
            .assetId(asset_id)
            .execute();
        if (!response.isSuccessful()) {
            throw new Exception(response.message());
        }
        JSONObject jsonObj = new JSONObject(response.body().toString());
        System.out.println("Account Information for Asset: " + jsonObj.toString(2)); // pretty print json
    }

    public static void searchTxAddressAsset(IndexerClient indexerClientInstance) throws Exception {
        System.out.println("");
        System.out.println("==> SEARCH TRANSACTIONS FOR ASSET AND MIN AMOUNT ");
        Address account = new Address("BHF5U3LAR5Z7R272Q4VK6JLWFSYWKBS7PLA44FFBK2YW2WZLQM7FXOJXQM");
        Long asset_id = Long.valueOf(29340683);
        Long min_amount = Long.valueOf(99);
        Response<TransactionsResponse> response = indexerClientInstance.searchForTransactions()
            .address(account)
            .currencyGreaterThan(min_amount)
            .assetId(asset_id).execute();
        if (!response.isSuccessful()) {
            throw new Exception(response.message());
        }
        JSONObject jsonObj = new JSONObject(response.body().toString());
        System.out.println("Transaction Info: " + jsonObj.toString(2)); // pretty print json
    }

    public static void assetBalances(IndexerClient indexerClientInstance) throws Exception {
        System.out.println("");
        System.out.println("==> LOOKUP ASSET BALANCES");

        Long asset_id = Long.valueOf(29340683);


        // searhes for asset greater than currencyGreaterThan
        Response<AssetBalancesResponse> response = indexerClientInstance.lookupAssetBalances(asset_id)
            .execute();
        if (!response.isSuccessful()) {
            throw new Exception(response.message());
        }
        JSONObject jsonObj = new JSONObject(response.body().toString());
        System.out.println("Balance Information for Asset: " + jsonObj.toString(2)); // pretty print json
    }

    public static void searchAssetName(IndexerClient indexerClientInstance) throws Exception {
        System.out.println("");
        System.out.println("==> SEARCH ASSETS FOR NAME AND CREATOR");
        String name = "Alice's Artwork";
        String creator = "BHF5U3LAR5Z7R272Q4VK6JLWFSYWKBS7PLA44FFBK2YW2WZLQM7FXOJXQM";
        Response<AssetsResponse> response = indexerClientInstance.searchForAssets()
            .creator(creator)
            .name(name)
            .execute();
        if (!response.isSuccessful()) {
            throw new Exception(response.message());
        }
        JSONObject jsonObj = new JSONObject(response.body().toString());
        System.out.println("Creator Information for Asset Name: : " + jsonObj.toString(2)); // pretty print json
    }
}
