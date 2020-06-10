import json
# requires Python SDK version 1.3 or higher
from algosdk.v2client import indexer

data = {
    "indexer_token": "",
    "indexer_address": "http://localhost:8980"
}

# instantiate indexer client
myindexer = indexer.IndexerClient(**data)
# gets accounts with a min balance of 100 that have a particular AssetID
data = {
    "min_balance": 100,
    "asset_id": 312769
}
response = myindexer.accounts(**data)
print(json.dumps(response, indent=2, sort_keys=True))
