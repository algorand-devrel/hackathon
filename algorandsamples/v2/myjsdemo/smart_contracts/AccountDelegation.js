const algosdk = require('algosdk');
// const token = "<algod-token>";
// const server = "<algod-address>";
// const port = <algod-port>;
// sandbox
const token = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa";
const server = "http://localhost";
const port = 4001;
// Import the filesystem module 
const fs = require('fs'); 
// import your private key mnemonic
// let PASSPHRASE = "<25-word-mnemonic>";
let PASSPHRASE = "awake used crawl list cruel harvest useful flag essay speed glad salmon camp sudden ride symptom test kind version together project inquiry diet abandon budget";

let  myAccount = algosdk.mnemonicToSecretKey(PASSPHRASE);
console.log("My Address: " + myAccount.addr);

// create an algod v2 client
let algodclient = new algosdk.Algodv2(token, server, port);

(async () => {

    // get suggested parameter
    let params = await algodclient.getTransactionParams().do();
    // comment out the next two lines to use suggested fee 
    params.fee = 1000;
    params.flatFee = true;
    console.log(params);
    // create logic sig
    // samplearg.teal
    // This code is meant for learning purposes only
    // It should not be used in production
    // arg_0
    // btoi
    // int 12345
    // ==
    // see more info here: https://developer.algorand.org/docs/features/asc1/sdks/#accessing-teal-program-from-sdks
    let  fs = require('fs'),
        path = require('path'),
        filePath = path.join(__dirname, 'samplearg.teal');
    // filePath = path.join(__dirname, <'fileName'>);
    let data = fs.readFileSync(filePath);
    let results = await algodclient.compile(data).do();
    console.log("Hash = " + results.hash);
    console.log("Result = " + results.result);
    // let program = new Uint8Array(Buffer.from(<"base64-encoded-program">, "base64"));
    let program = new Uint8Array(Buffer.from(results.result, "base64"));
    // Use this if no args
    // let lsig = algosdk.makeLogicSig(program);

    // String parameter
    // let args = ["<my string>"];
    // let lsig = algosdk.makeLogicSig(program, args);
    // Integer parameter

    let args = getUint8Int(12345);
    let lsig = new algosdk.LogicSigAccount(program, args);

    // sign the logic signature with an account sk
    lsig.sign(myAccount.sk);
    
    // Setup a transaction
    let sender = myAccount.addr;
    let receiver = "SOEI4UA72A7ZL5P25GNISSVWW724YABSGZ7GHW5ERV4QKK2XSXLXGXPG5Y";
    // let receiver = "<receiver-address>"";
    let amount = 10000;
    let closeToRemaninder = undefined;
    let note = undefined;
    let txn = algosdk.makePaymentTxnWithSuggestedParams(sender, 
        receiver, amount, closeToRemaninder, note, params)

    // Create the LogicSigTransaction with contract account LogicSig
    let rawSignedTxn = algosdk.signLogicSigTransactionObject(txn, lsig);
    // fs.writeFileSync("simple.stxn", rawSignedTxn.blob);
    // send raw LogicSigTransaction to network    
    let tx = (await algodclient.sendRawTransaction(rawSignedTxn.blob).do());
    console.log("Transaction : " + tx.txId);    
    await algosdk.waitForConfirmation(algodclient, tx.txId, 4);

})().catch(e => {
    console.log(e.message);
    console.log(e);
});
function getUint8Int(number) {
    const buffer = Buffer.alloc(8);
    const bigIntValue = BigInt(number);
    buffer.writeBigUInt64BE(bigIntValue);
    return  [Uint8Array.from(buffer)];
}
