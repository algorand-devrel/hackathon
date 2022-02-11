#!/usr/bin/env python3
import datetime
from pyteal import *

import base64
import os
from algosdk import account, algod, encoding, mnemonic, transaction
from algosdk.v2client import algod

from algosdk.future.transaction import StateSchema, ApplicationCreateTxn
from algosdk.v2client.models.dryrun_source import DryrunSource
from algosdk.v2client.models.dryrun_request import DryrunRequest
import json
from algosdk.future.transaction import *

def write_drr(res, contents):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    path = os.path.join(dir_path, res)
    data = encoding.msgpack_encode(contents)
    data = base64.b64decode(data)
    with open(path, "wb") as fout:
        fout.write(data)
    return


def write_teal(res, contents):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    path = os.path.join(dir_path, res)
    f = open(path, "w")
    f.write(str(contents))
    f.close()
    return


# return dry run request (needed for debugging)


def dryrun_drr(signed_txn, mysource, creator, user):
    sources = []
    if (mysource != None):
        # source
        sources = [DryrunSource(
            field_name="approv", source=mysource, txn_index=0)]
    drr = DryrunRequest(txns=[signed_txn],
                        sources=sources, accounts=[creator, user])
    return drr


# declare application state storage (immutable)
local_ints = 1
local_bytes = 0
global_ints = 1
global_bytes = 0
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


def approval_program_initial():
    get_counter = App.globalGet(Bytes("counter"))
    counter_logic = Seq([
        # read global state, increment the value,
        # and put the updated value back into global state
        App.globalPut(Bytes("counter"), get_counter + Int(1)),
        Return(get_counter)
    ])
    return counter_logic


def approval_program_refactored():
    get_localcounter = App.localGet(Int(0), Bytes("localcounter"))
    # user_account = mnemonic.to_public_key(user_mnemonic)
    get_counter = App.globalGet(Bytes("counter"))
    counter_logic = Seq([
        # read global state, increment the value, and put the updated value back into global state
        App.globalPut(Bytes("counter"), get_counter + Int(1)),
        App.localPut(Int(0), Bytes("localcounter"),
                     get_localcounter + Int(1)),
        # read from global state and return
        Return(get_localcounter)
    ])
    return counter_logic


def clear_state_program():
    return Int(1)
# create new application

# def compile_program(client, source_code):
#     compile_response = client.compile(source_code.decode('utf-8'))
#     return base64.b64decode(compile_response['result'])


def compile_program(acl, program_source):
    response = acl.compile(program_source)
    programstr = response['result']
    t = programstr.encode("ascii")
    # program = b"hex-encoded-program"
    approval_program = base64.decodebytes(t)
    return approval_program


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
        print("Result confirmed in round: {}".format(transaction_response['confirmed-round']))
       
    except Exception as err:
        print(err)
        return

    # display results
    app_id = transaction_response['application-index']
    print("Created new app-id: ", app_id)

    return app_id

# opt-in to application


def opt_in_app(client, private_key, index):
    # declare sender
    sender = account.address_from_private_key(private_key)
    print("OptIn from account: ", sender)

    # get node suggested parameters
    params = client.suggested_params()
    # comment out the next two (2) lines to use suggested fees
    # params.flat_fee = True
    # params.fee = 1000

    # create unsigned transaction
    txn = ApplicationOptInTxn(sender, params, index)

    # sign transaction
    signed_txn = txn.sign(private_key)
    tx_id = signed_txn.transaction.get_txid()

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

    print("OptIn to app-id: ")
    print(json.dumps(transaction_response['txn']['txn']['apid'], indent=2))

# call application


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
    # `tealdbg debug program.teal --dryrun-req mydrr.dr`
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


def read_local_state(client, addr, app_id):
    results = client.account_info(addr)
    for local_state in results['apps-local-state']:
        for index in local_state:
            if local_state[index] == app_id:
                print(f"local_state of account {addr} for app_id {app_id}: ")
                print(json.dumps(local_state['key-value'], indent=2))
                break

# read app global state


def read_global_state(client, addr, app_id):
    results = client.account_info(addr)
    apps_created = results['created-apps']
    for app in apps_created:
        if app['id'] == app_id:
            print(f"global_state for app_id {app_id}: ")
            print(json.dumps(app['params']['global-state'], indent=2))
            break


def update_app(client, private_key, app_id, approval_program, clear_program):
    # declare sender
    sender = account.address_from_private_key(private_key)

    # define initial value for key "timestamp"
    # app_args = [b'initial value']

    # get node suggested parameters
    params = client.suggested_params()
    # comment out the next two (2) lines to use suggested fees
    # params.flat_fee = True
    # params.fee = 1000

    # create unsigned transaction
    txn = ApplicationUpdateTxn(sender, params, app_id,
                                           approval_program, clear_program, None)

    # sign transaction
    signed_txn = txn.sign(private_key)
    tx_id = signed_txn.transaction.get_txid()

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
    app_id = transaction_response['txn']['txn']['apid']
    print("Updated existing app-id: ", app_id)

# delete application


def delete_app(client, private_key, index):
    # declare sender
    sender = account.address_from_private_key(private_key)

    # get node suggested parameters
    params = client.suggested_params()
    # comment out the next two (2) lines to use suggested fees
    # params.flat_fee = True
    # params.fee = 1000

    # create unsigned transaction
    txn = ApplicationDeleteTxn(sender, params, index)

    # sign transaction
    signed_txn = txn.sign(private_key)
    tx_id = signed_txn.transaction.get_txid()

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

    print("Deleted app-id: ", transaction_response['txn']['txn']['apid'])

# close out from application


def close_out_app(client, private_key, index):
    # declare sender
    sender = account.address_from_private_key(private_key)

    # get node suggested parameters
    params = client.suggested_params()
    # comment out the next two (2) lines to use suggested fees
    # params.flat_fee = True
    # params.fee = 1000

    # create unsigned transaction
    txn = ApplicationCloseOutTxn(sender, params, index)

    # sign transaction
    signed_txn = txn.sign(private_key)
    tx_id = signed_txn.transaction.get_txid()

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
    # transaction_response = client.pending_transaction_info(tx_id)
    print("Closed out from app-id: ")
    print(json.dumps(transaction_response['txn']['txn']['apid'], indent=2))

# clear application


def clear_app(client, private_key, index):
    # declare sender
    sender = account.address_from_private_key(private_key)

    # get node suggested parameters
    params = client.suggested_params()
    # comment out the next two (2) lines to use suggested fees
    params.flat_fee = True
    params.fee = 1000

    # create unsigned transaction
    txn = ApplicationClearStateTxn(sender, params, index)

    # sign transaction
    signed_txn = txn.sign(private_key)
    tx_id = signed_txn.transaction.get_txid()

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

    print("Cleared app-id: ")
    print(json.dumps(transaction_response['txn']['txn']['apid'], indent=2))


def main():

    # program_file_name = "program.teal"

    # --------- compile, debug ,  & send transaction using Python SDK ----------

    # read TEAL program
    # data = load_resource(myprogram)
    algod_address = "http://localhost:4001"
    algod_token = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    # algod_address = "http://localhost:8080"
    # algod_token = "8024065d94521d253181cff008c44fa4ae4bdf44f028834cd4b4769a26282de1"

    # create algod clients
    acl = algod.AlgodClient(algod_token, algod_address)

    # compile programs approval_program_source
    # and approval_program_source_refactored
    approval_program_source = compileTeal(
        approval_program_initial(), Mode.Application, version=5)
    write_teal('hello_world.teal', approval_program_source)

    approval_program_refactored_source = compileTeal(
        approval_program_refactored(), Mode.Application, version=5)
    write_teal('hello_world_updated.teal',
               approval_program_refactored_source)

    clear_program_source = compileTeal(clear_state_program(), Mode.Application, version=5)
    write_teal('hello_world_clear.teal', clear_program_source)

    approval_program_compiled = compile_program(acl, approval_program_source)

    clear_program_compiled = compile_program(acl, clear_program_source)

    approval_program_refactored_compiled = compile_program(
        acl, approval_program_refactored_source)

    try:

        app_id = create_app(acl, creator_private_key,
                            approval_program_compiled, clear_program_compiled, global_schema, local_schema)

        # opt-in to application
        opt_in_app(acl, user_private_key, app_id)
        opt_in_app(acl, creator_private_key, app_id)
        # call app from user account updates global storage

        call_app(acl, user_private_key, app_id, None,
                 approval_program_source, 'hello_world.teal')

        # read global state of application
        read_global_state(acl, account.address_from_private_key(
            creator_private_key), app_id)

        # update application

        update_app(acl, creator_private_key,
                   app_id, approval_program_refactored_compiled, clear_program_compiled)

        # call application with updated app which updates local storage counter
        call_app(acl, user_private_key, app_id,
                 None, approval_program_refactored_source, 'hello_world_updated.teal')

        # read local state of application from user account
        read_local_state(acl, account.address_from_private_key(
            user_private_key), app_id)

        # close-out from application - removes application from balance record
        close_out_app(acl, user_private_key, app_id)

        # # opt-in again to application
        # opt_in_app(acl, user_private_key, app_id)

        # # call application with arguments
        # call_app(acl, user_private_key, app_id,
        #          None, approval_program_refactored_source, 'hello_world_updated.teal')

        # delete application
        # clears global storage only
        # user must clear local
        delete_app(acl, creator_private_key, app_id)

        # clear application from user account
        # clears local storage
        # clear_app(acl, user_private_key, app_id)

    except Exception as e:
        print(e)


main()
