import hashlib
import json
from time import time
from uuid import uuid4

from flask import Flask, jsonify, request

DIFFICULTY = 6

class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []

        # Create the genesis block
        self.new_block(previous_hash='=============', proof=100)

    def new_block(self, proof, previous_hash=None):
        """
        Create a new Block in the Blockchain

        A block should have:
        * Index
        * Timestamp
        * List of current transactions
        * The proof used to mine this block
        * The hash of the previous block

        :param proof: <int> The proof given by the Proof of Work algorithm
        :param previous_hash: (Optional) <str> Hash of previous Block
        :return: <dict> New Block
        """
        # print("NEW BLOCK")
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1])
        }

        # Reset the current list of transactions
        self.current_transactions = []
        # Append the chain to the block
        self.chain.append(block)
        # print(f"CHAIN: {self.chain}")
        # Return the new block
        return block

    def hash(self, block):
        """
        Creates a SHA-256 hash of a Block

        :param block": <dict> Block
        "return": <str>
        """

        # Use json.dumps to convert json into a string
        # Use hashlib.sha256 to create a hash
        # It requires a `bytes-like` object, which is what
        # .encode() does.
        # It convertes the string to bytes.
        # We must make sure that the Dictionary is Ordered,
        # or we'll have inconsistent hashes

        # TODO: Create the block_string
        # .dumps() = python version of JSON.stringify
        # .encode() strips out metadata and creates a byte string
        block_string = json.dumps(block, sort_keys=True).encode()

        # TODO: Hash this string using sha256
        hash = hashlib.sha256(block_string).hexdigest()

        # By itself, the sha256 function returns the hash in a raw string
        # that will likely include escaped characters.
        # This can be hard to read, but .hexdigest() converts the
        # hash to a string of hexadecimal characters, which is
        # easier to work with and understand

        # TODO: Return the hashed block string in hexadecimal format
        return hash

    @property
    def last_block(self):
        return self.chain[-1]


    # def proof_of_work(self, block): # remove mining on server
    #     """
    #     Simple Proof of Work Algorithm
    #     Stringify the block and look for a proof.
    #     Loop through possibilities, checking each one against `valid_proof`
    #     in an effort to find a number that is a valid proof
    #     :return: A valid proof for the provided block
    #     """
    #     # TODO
    #     # return proof
    #     block_string = json.dumps(self.last_block, sort_keys=True)
    #     proof = 0
    #     while self.valid_proof(block_string, proof) is False:
    #         proof += 1
        
    #     return proof

    @staticmethod
    def valid_proof(block_string, proof):
        """
        Validates the Proof:  Does hash(block_string, proof) contain 3
        leading zeroes?  Return true if the proof is valid
        :param block_string: <string> The stringified block to use to
        check in combination with `proof`
        :param proof: <int?> The value that when combined with the
        stringified previous block results in a hash that has the
        correct number of leading zeroes.
        :return: True if the resulting hash is a valid proof, False otherwise
        """
        # TODO
        # return True or False
        # print(f"\n\nSTART VALID PROOF | LAST BLOCK: {blockchain.last_block}\n\n")
        guess = f'{block_string}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        # print(f'GUESS_HASH: {guess_hash} | {guess_hash[:DIFFICULTY] == "0" * DIFFICULTY}')

        return guess_hash[:DIFFICULTY] == "0" * DIFFICULTY


# Instantiate our Node
app = Flask(__name__)

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

# Instantiate the Blockchain
blockchain = Blockchain()


@app.route('/mine', methods=['POST'])
def mine():
    """ old code for mining on server
    # Run the proof of work algorithm to get the next proof
    proof = blockchain.proof_of_work(blockchain.last_block)

    # Forge the new Block by adding it to the chain with the proof
    previous_hash = blockchain.hash(blockchain.last_block)
    new_block = blockchain.new_block(proof, previous_hash)

    response = {
        'block': new_block
    }

    return jsonify(response), 200
    # """
    """ # Lecture Version
    try:
        values = r.get_json()
    except ValueError:
        print("Error: Non-json response")
        print("Response returned:")
        print(r)
        return "Error" # TODO Handle error

    required = ['proof', 'id']
    if not all(k values for k in required):
        response = { 'message': "Missing Values"}
        return jsonify(response), 400

    submitted_proof = values['proof']

    # Determine if proof is valid
    last_block = blockchain.last_block
    last_block_string = json.dumps(last_block, sort_keys=True)
    if blockchain.valid_proof(last_block_string, submitted_proof):
        # Forge new Block by adding it to the chain with the proof
        previous_hash = blockchain.hash(blockchain.last_block)
        new_block = blockchain.new_block(submitted_proof, previous_hash)

        response = {
            'message': "New Block Forged",
            'block': new_block
        }
        return jsonify(response), 200
    else:
        response = {
            'message': "Proof invalid or already submitted"
        }
        return jsonify(response), 200
    #"""

    #""" Mine own code
    data = request.get_json()
    if "proof" not in data or "id" not in data:
        response = {"error": ""}
        if "proof" not in data and "id" not in data:
            response["error"] = 'POST request must include proof and id'
        elif "proof" not in data:
            response["error"] = 'POST request must include proof'
        else:
            response["error"] = 'POST request must include id'
        return jsonify(response), 400     
    else:
        # print(f"\n\nblockchain length: {len(blockchain.chain)} | id: {data['id']}\n\n")
        if data["id"] <= len(blockchain.chain):
            # print("\n\ndata id is less than blockchain\n\n")
            return jsonify({ 'error': 'Block already claimed' }), 200
        proof = data["proof"]
        block_string = json.dumps(blockchain.last_block, sort_keys=True)
        is_valid = blockchain.valid_proof(block_string, proof)
        # print(f"IS_VALID: {is_valid}")
        if is_valid:
            # print('IS VALID')
            previous_hash = blockchain.hash(blockchain.last_block)
            new_block = blockchain.new_block(proof, previous_hash)
            return jsonify({ "message": "New Block Forged" }), 200
        else:
            # print("IS NOT VALID")
            return jsonify({ "message": "No New Block"}), 400
    # """      


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'length': len(blockchain.chain),
        'block': blockchain.chain
    }
    return jsonify(response), 200

@app.route('/last_block', methods=['GET'])
def last_block():
    response = {
        'last_block': blockchain.last_block,
        'difficulty': DIFFICULTY
    }

    return jsonify(response), 200


# Run the program on port 5000
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
