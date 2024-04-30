import hashlib  # For hashing functions
import time  # For handling timestamps
import json  # For JSON serialization/deserialization
from typing import List  # For type hints
import requests  # For making HTTP requests
from flask import Flask, jsonify, request  # For creating a web application
from uuid import uuid4  # For generating unique identifiers
from urllib.parse import urlparse  # For parsing URLs

# Define a class to represent transactions in the blockchain.
class Transaction:
    def __init__(self, sender, recipient, amount):
        # Initialize transaction details.
        self.sender = sender
        self.recipient = recipient
        self.amount = amount

    def to_dict(self):
        # Convert transaction details to a dictionary.
        return {
            'sender': self.sender,
            'recipient': self.recipient,
            'amount': self.amount
        }

# Define a class to represent individual blocks in the blockchain.
class Block:
    def __init__(self, index, previous_hash, timestamp, transactions, proof, hash):
        # Initialize block attributes.
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.transactions = transactions
        self.proof = proof
        self.hash = hash

    def to_dict(self):
        # Convert block information to a dictionary.
        return {
            'index': self.index,
            'previous_hash': self.previous_hash,
            'timestamp': self.timestamp,
            'transactions': [transaction.to_dict() for transaction in self.transactions],
            'proof': self.proof,
            'hash': self.hash
        }

# Define a class to manage the blockchain.
class Blockchain:
    def __init__(self):
        # Initialize blockchain attributes.
        self.chain = []
        self.current_transactions = []  # Transactions in the current block being mined
        self.nodes = set()  # Set of nodes in the network
        self.create_genesis_block()  # Create the initial block (genesis block)

    def create_genesis_block(self):
        # Generate the initial block in the blockchain (genesis block).
        self.add_block(previous_hash='1', proof=100)

    def add_block(self, proof, previous_hash=None):
        # Add a new block to the blockchain.
        block_data = {
            'index': len(self.chain) + 1,
            'timestamp': time.time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]) if self.chain else '1',
        }
        block_hash = self.hash(block_data)  # Generate hash based on block data
        block = Block(
            index=block_data['index'],
            timestamp=block_data['timestamp'],
            transactions=self.current_transactions,
            proof=proof,
            previous_hash=block_data['previous_hash'],
            hash=block_hash
        )
        self.current_transactions = []  # Clear transactions after adding them to a block
        self.chain.append(block)
        return block

    @staticmethod
    def hash(block_data):
        # Hash block data using SHA-256.
        block_string = json.dumps(block_data, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    # Rest of the Blockchain class...

# Create a new Flask web application.
app = Flask(__name__)

# Generate a unique identifier for this node.
node_identifier = str(uuid4()).replace('-', '')

# Instantiate the Blockchain class.
blockchain = Blockchain()

# Define endpoints for interacting with the blockchain through HTTP requests.

@app.route('/mine', methods=['GET'])
def mine():
    # This endpoint is used for "mining" a new block.
    last_block = blockchain.last_block  # Get the last block in the chain
    last_proof = last_block['proof']  # Get the proof of work from the last block
    proof = blockchain.proof_of_work(last_proof)  # Perform proof of work to find a new valid proof

    # Reward the miner by adding a transaction to the current block.
    blockchain.new_transaction(
        sender="0",  # Indicates that this is a reward transaction
        recipient=node_identifier,  # The recipient is the miner (this node)
        amount=1,  # Reward amount
    )

    # Create the new block and add it to the blockchain.
    previous_hash = blockchain.hash(last_block)  # Calculate the hash of the last block
    block = blockchain.add_block(proof, previous_hash)

    # Prepare the response with details of the new block.
    response = {
        'message': "New Block Forged",
        'index': block.index,
        'transactions': block.transactions,
        'proof': block.proof,
        'previous_hash': block.previous_hash,
    }
    return jsonify(response), 200

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    # This endpoint allows a new transaction to be posted to the blockchain.
    values = request.get_json()
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # Add the new transaction to the current list of transactions.
    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])

    # Prepare the response indicating that the transaction will be added to a block.
    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 201

@app.route('/chain', methods=['GET'])
def full_chain():
    # This endpoint returns the full blockchain.
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200

# Parse command line arguments for running the Flask app.
if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='0.0.0.0', port=port)
