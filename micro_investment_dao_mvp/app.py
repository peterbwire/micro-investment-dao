# micro_investment_dao_mvp/app.py

from flask import Flask, request, jsonify
from web3 import Web3
import json

app = Flask(__name__)

# Connect to local Ganache or Polygon Mumbai Testnet
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))  # Replace with Infura/Alchemy for testnet

# Load compiled smart contract
with open("contracts/DAOContract.json") as f:
    contract_json = json.load(f)
    contract_abi = contract_json['abi']
    contract_address = Web3.to_checksum_address("0xYourContractAddressHere")
    contract = w3.eth.contract(address=contract_address, abi=contract_abi)

# Replace with your deployed wallet
admin_address = w3.to_checksum_address("0xYourWalletAddressHere")

@app.route("/create_group", methods=["POST"])
def create_group():
    data = request.get_json()
    name = data['name']
    tx_hash = contract.functions.createGroup(name).transact({'from': admin_address})
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    return jsonify({"status": "Group created", "tx": tx_hash.hex()})

@app.route("/contribute", methods=["POST"])
def contribute():
    data = request.get_json()
    group_id = int(data['group_id'])
    amount = int(data['amount'])
    contributor = data['from']
    tx_hash = contract.functions.contribute(group_id).transact({
        'from': contributor,
        'value': w3.to_wei(amount, 'ether')
    })
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    return jsonify({"status": "Contribution successful", "tx": tx_hash.hex()})

@app.route("/propose", methods=["POST"])
def propose():
    data = request.get_json()
    group_id = int(data['group_id'])
    description = data['description']
    amount = int(data['amount'])
    proposer = data['from']
    tx_hash = contract.functions.proposeInvestment(group_id, description, w3.to_wei(amount, 'ether')).transact({
        'from': proposer
    })
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    return jsonify({"status": "Proposal created", "tx": tx_hash.hex()})

@app.route("/vote", methods=["POST"])
def vote():
    data = request.get_json()
    proposal_id = int(data['proposal_id'])
    voter = data['from']
    support = bool(data['support'])
    tx_hash = contract.functions.vote(proposal_id, support).transact({'from': voter})
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    return jsonify({"status": "Vote submitted", "tx": tx_hash.hex()})

@app.route("/execute", methods=["POST"])
def execute():
    data = request.get_json()
    proposal_id = int(data['proposal_id'])
    tx_hash = contract.functions.executeProposal(proposal_id).transact({'from': admin_address})
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    return jsonify({"status": "Proposal executed", "tx": tx_hash.hex()})

if __name__ == "__main__":
    app.run(debug=True)
