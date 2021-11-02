# accounts_assetid.py
import json
# requires Python SDK version 1.3 or higher
from algosdk.v2client import indexer

# instantiate indexer client
myindexer = indexer.IndexerClient(indexer_token="", indexer_address="http://localhost:8981")

response = myindexer.accounts(
    asset_id=12270668)
print("Account Info: " + json.dumps(response, indent=2, sort_keys=True))

