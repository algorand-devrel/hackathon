import json
import os
from pyteal import *
from pyteal.ast.bytes import Bytes
from algosdk.v2client import algod
from pyteal_helpers import program
from algosdk.future.transaction import *
from algosdk import account, encoding, mnemonic, transaction
from algosdk.v2client.models.dryrun_source import DryrunSource
from algosdk.v2client.models.dryrun_request import DryrunRequest


local_ints = 0
local_bytes = 0
global_ints = 1
global_bytes = 1
global_schema = StateSchema(global_ints, global_bytes)
local_schema = StateSchema(local_ints, local_bytes)
# define private keys
creator_mnemonic = "burst term load cactus virtual fan punch medal bulb truth sugar below fame below glow ankle scorpion miracle cupboard trophy ability tip asthma absent inhale"
user_mnemonic = "reopen demand depart jewel host smooth genius catalog alone account ancient valve industry poet swim volcano cousin dismiss toward expand agree tattoo jealous above helmet"


def get_private_key_from_mnemonic(mn):
    private_key = mnemonic.to_private_key(mn)
    return private_key


creator_private_key = get_private_key_from_mnemonic(creator_mnemonic)
user_private_key = get_private_key_from_mnemonic(user_mnemonic)


def compile_program(acl, program_source):
    response = acl.compile(program_source)
    programstr = response['result']
    t = programstr.encode("ascii")
    # program = b"hex-encoded-program"
    approval_program = base64.decodebytes(t)
    return approval_program


def write_teal(res, contents):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    path = os.path.join(dir_path, res)
    f = open(path, "w")
    f.write(str(contents))
    f.close()
    return


def read_global_state(client, addr, app_id):
    results = client.account_info(addr)
    apps_created = results['created-apps']
    for app in apps_created:
        if app['id'] == app_id:
            print(f"global_state for app_id {app_id}: ")
            print(json.dumps(app['params']['global-state'], indent=2))
            break



def main():
    algod_address = "http://hackathon.algodev.network:9100"
    algod_token = "ef920e2e7e002953f4b29a8af720efe8e4ecc75ff102b165e0472834b25832c1"
    # algod_address = "http://localhost:8080"
    # algod_token = "8024065d94521d253181cff008c44fa4ae4bdf44f028834cd4b4769a26282de1"

    # create algod clients
    acl = algod.AlgodClient(algod_token, algod_address)
    approval_program_source = compileTeal(
        approval(), Mode.Application, version=6)
    write_teal('counter_approval.teal', approval_program_source)
    print("Approval Source: ")
    print(approval_program_source)
    clear_program_source = compileTeal(clear(), Mode.Application, version=6)
    write_teal('counter_clear.teal', clear_program_source)
    print("Clear Program")
    print(clear_program_source)
    approval_program_compiled = compile_program(acl, approval_program_source)

    clear_program_compiled = compile_program(acl, clear_program_source)

    # app_id = create_app(acl, creator_private_key,
    #                     approval_program_compiled, clear_program_compiled, global_schema, local_schema)
# TXID:  UJ4G7NCZBROJNGGQKVQXX6X2KCKKKBWAERJ3EMGVDPNLMFDSYFFA
# Result confirmed in round: 23952166
# Created new Contract app-id:  108497623
# Contract Address:  6S2CYQ3UJQDHNIAXGDZFQNIKGABDH4VOGN7LW5HSEQQIBVDIB3OS2VNPLU
# Creator Account Address:  IW66YB5IV7J6PIIYCFG4ALRAVJYNZ2P3TU7EAS27FMOX4D45Q34GA2UO3Y
    app_id = 108497623

    # read global state of application
    read_global_state(acl, account.address_from_private_key(
        creator_private_key), app_id)

    # opt-in to application
    # opt_in_app(acl, user_private_key, app_id)
    # opt_in_app(acl, creator_private_key, app_id)
    # call app from user account updates global storage
   
    app_args = None
    # comment out next 2 lines to error
    arg1 = "inc"
    app_args=[arg1]
    # arg1 = "dec"
    # app_args=[arg1]
    call_app(acl, user_private_key, app_id, app_args,
                approval_program_source, 'counter_approval.teal')
    # read global state of application
    read_global_state(acl, account.address_from_private_key(
        creator_private_key), app_id)
   

def approval():
    # globals
    global_owner = Bytes("owner")  # byteslice
    global_counter = Bytes("counter")  # uint64

    op_increment = Bytes("inc")
    op_decrement = Bytes("dec")

    increment = Seq(
        [
            App.globalPut(global_counter, App.globalGet(
                global_counter) + Int(1)),
            Approve(),
        ]
    )

    decrement = Seq(
        [
            App.globalPut(global_counter, App.globalGet(
                global_counter) - Int(1)),
            Approve(),
        ]
    )

    return program.event(
        init=Seq(
            [
                App.globalPut(global_owner, Txn.sender()),
                App.globalPut(global_counter, Int(0)),
                Approve(),
            ]
        ),
        no_op=Cond(
            [Txn.application_args[0] == op_increment, increment],
            [Txn.application_args[0] == op_decrement, decrement],
        ),
    )


def clear():
    return Approve()

def write_drr(res, contents):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    path = os.path.join(dir_path, res)
    data = encoding.msgpack_encode(contents)
    data = base64.b64decode(data)
    with open(path, "wb") as fout:
        fout.write(data)
    return
    
def dryrun_drr(signed_txn, mysource, creator, user):
    sources = []
    if (mysource != None):
        # source
        sources = [DryrunSource(
            field_name="approv", source=mysource, txn_index=0)]
    drr = DryrunRequest(txns=[signed_txn],
                        sources=sources, accounts=[creator, user])
    return drr


def create_app(client, private_key, approval_program_compiled, clear_program, global_schema, local_schema):
    # define sender as creator
    sender = account.address_from_private_key(private_key)
    # declare on_complete as NoOp
    on_complete = OnComplete.NoOpOC.real
    # get node suggested parameters
    params = client.suggested_params()
    # comment out the next two (2) lines to use suggested fees
    # params.flat_fee = True
    # params.fee = 1000
    # create unsigned transaction - Create App
    txn = ApplicationCreateTxn(sender,
                               params, on_complete,
                               approval_program_compiled, clear_program,
                               global_schema, local_schema)
    # sign transaction
    signed_txn = txn.sign(private_key)
    tx_id = signed_txn.transaction.get_txid()
    # send transaction
    client.send_transactions([signed_txn])
    # wait for confirmation
    try:
        transaction_response = wait_for_confirmation(client, tx_id, 4)
        print("TXID: ", tx_id)
        print("Result confirmed in round: {}".format(
            transaction_response['confirmed-round']))
    except Exception as err:
        print(err)
        return
    # display results
    app_id = transaction_response['application-index']
    print("Created new Contract app-id: ", app_id)
    actual = logic.get_application_address(app_id)
    print("Contract Address: ", actual)
    print("Creator Account Address: ", sender)

    return app_id

def call_app(client, private_key_user, index, app_args, approval_program_source, teal_file_name):
    # declare sender
    creator = account.address_from_private_key(creator_private_key)
    creatoraccount = client.account_info(creator)
    user = account.address_from_private_key(private_key_user)
    useraccount = client.account_info(user)
    print("Creator account: ", creator)
    print("User account: ", user)
    # get node suggested parameters
    params = client.suggested_params()
    # comment out the next two (2) lines to use suggested fees
    # params.flat_fee = True
    # params.fee = 1000

    # create unsigned transaction

    txn = ApplicationNoOpTxn(user, params, index, app_args)

    # sign transaction
    signed_txn = txn.sign(private_key_user)
    tx_id = signed_txn.transaction.get_txid()
    # get dryrun request

    mydrr = dryrun_drr(signed_txn, approval_program_source,
                       creatoraccount, useraccount)
    # write drr
    drr_file_name = "mydrr.dr"
    write_drr(drr_file_name, mydrr)
    print("drr file created ... debugger starting - goto chrome://inspect")

    #  START debugging session
    #  either use from terminal in this folder
    # `tealdbg debug counter_approval.teal --dryrun-req mydrr.dr`
    #
    # or use this line to invoke debugger
    # and switch to chrome://inspect to inspect and debug
    # (program execution will continue after debuigging session completes)

    dir_path = os.path.dirname(os.path.realpath(__file__))
    drrpath = os.path.join(dir_path, drr_file_name)
    programpath = os.path.join(dir_path, teal_file_name)
    
    # stdout, stderr = execute(["tealdbg", "debug", programpath, "--dryrun-req", drrpath])

    # send transaction
    client.send_transactions([signed_txn])

    # wait for confirmation
    try:
        transaction_response = wait_for_confirmation(client, tx_id, 4)
        print("TXID: ", tx_id)
        print("Result confirmed in round: {}".format(transaction_response['confirmed-round']))
    except Exception as err:
        print(err)
        return

    # display results

    print("Called app-id: ", transaction_response['txn']['txn']['apid'])
    if "global-state-delta" in transaction_response:
        print("Global State updated :\n")
        print(json.dumps(transaction_response['global-state-delta'], indent=2))
    if "local-state-delta" in transaction_response:
        print("Local State updated :\n")
        print(json.dumps(transaction_response['local-state-delta'], indent=2))


main()
