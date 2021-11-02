from algosdk import *
from algosdk.v2client import algod
from algosdk.v2client.models import DryrunSource, DryrunRequest
from algosdk.future.transaction import *
from sandbox import get_accounts
import base64
import os


token = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
url = "http://localhost:4001"

_verify = b"A"*64 # 64 bytes since thats the length of a valid signature

client = algod.AlgodClient(token, url)

def demo():
    # Create acct
    addr, pk = get_accounts("Testnet")[0]
    print("Using {}".format(addr))

    # Create app
    app_id =   41057222
    # app_id = create_app(addr, pk)
    print("Created App with id: {}".format(app_id))

    # App call with 1 txn - this will fail
    try:
        sp = client.suggested_params()
        single = [
            get_app_call(addr, sp, app_id, [_verify, _verify])
        ]
        signed_group = [txn.sign(pk) for txn in single]
        # write_dryrun(signed_group, "expect-fail", app_id, [addr])

        txid = client.send_transactions(signed_group)
        print("Sending single transaction: {}".format(txid))

        result = wait_for_confirmation(client, txid, 4)
        print("Result from single: {}".format(result))
    except Exception as e:
        print("Failed to call single app call: {}".format(e))
        

    # App call with 3 txns
    # Only the first transaction passes the verify args, 
    # the others are used increase pooled opcode budget 
    # from 700 for one to 2100 for the three
    try :
        sp = client.suggested_params()
        actual = logic.get_application_address(app_id)
        print ("Address of Smart Contract: {}".format(actual))
        pooled_group = assign_group_id([
            get_app_call(addr, sp, app_id, [_verify, _verify]), 
            get_app_call(addr, sp, app_id, []),
            get_app_call(addr, sp, app_id, [])
        ])

        signed_group = [txn.sign(pk) for txn in pooled_group]
        write_dryrun(signed_group, "expect-succeed", app_id, [addr])


        txid = client.send_transactions(signed_group)
        print("Sending grouped transaction: {}".format(txid))

        result = wait_for_confirmation(client, txid, 4)
        print("Success! Confirmed in round: {}".format(result['confirmed-round']))
    except Exception as e:
        print("Failed to call grouped app call: {}".format(e))


def write_dryrun(signed_txn, name, app_id, addrs):
    path = os.path.dirname(os.path.abspath(__file__))
    # Read in approval teal source
    app_src = open(os.path.join(path,'approval.teal')).read()

    # Add source
    sources = [
        DryrunSource(
            app_index=app_id, 
            field_name="approv", 
            source=app_src
        ), 
    ]

    # Get account info
    accounts = [client.account_info(a) for a in addrs]
    # Get app info
    app = client.application_info(app_id)

    # Create request
    drr = DryrunRequest(
        txns=signed_txn, 
        sources=sources, 
        apps=[app], 
        accounts=accounts
    )

    file_path = os.path.join(path, "{}.msgp".format(name))
    data = encoding.msgpack_encode(drr)
    with open(file_path, "wb") as f:
        f.write(base64.b64decode(data))

    print("Created Dryrun file at {}".format(file_path))

    path = os.path.dirname(os.path.abspath(__file__))
    # Read in approval teal source
    app_src = open(os.path.join(path,'approval.teal')).read()

    # Add source
    sources = [
        DryrunSource(
            app_index=app_id, 
            field_name="approv", 
            source=app_src
        ), 
    ]

    # Get account info
    accounts = [client.account_info(a) for a in addrs]
    # Get app info
    app = client.application_info(app_id)

    # Create request
    drr = DryrunRequest(
        txns=signed_txn, 
        sources=sources, 
        apps=[app], 
        accounts=accounts
    )

    file_path = os.path.join(path, "{}.msgp".format(name))
    data = encoding.msgpack_encode(drr)
    with open(file_path, "wb") as f:
        f.write(base64.b64decode(data))
    
    print("Created Dryrun file at {}".format(file_path))

def get_app_call(addr, sp, app_id, args):
    return ApplicationCallTxn(
            addr, sp, app_id, 
            OnComplete.NoOpOC, 
            app_args=args,
            note=os.urandom(4) #Add random note field to prevent dupe transaction ids
    )

def create_app(addr, pk):

    # Get suggested params from network 
    sp = client.suggested_params()

    path = os.path.dirname(os.path.abspath(__file__))

    # Read in approval teal source && compile
    approval = open(os.path.join(path,'approval.teal')).read()
    app_result = client.compile(approval)
    app_bytes = base64.b64decode(app_result['result'])
    
    # Read in clear teal source && compile 
    clear = open(os.path.join(path,'clear.teal')).read()
    clear_result = client.compile(clear)
    clear_bytes = base64.b64decode(clear_result['result'])

    # We dont need no stinkin storage
    schema = StateSchema(0, 0)

    # Create the transaction
    create_txn = ApplicationCreateTxn(addr, sp, 0, app_bytes, clear_bytes, schema, schema)

    # Sign it
    signed_txn = create_txn.sign(pk)

    # Ship it
    txid = client.send_transaction(signed_txn)
    
    # Wait for the result so we can return the app id
    result = wait_for_confirmation(client, txid, 4)

    return result['application-index']

if __name__ == "__main__":
    demo()
