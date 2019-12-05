import hashlib
import requests
from datetime import datetime

import sys
import json

DIFFICULTY = 6
coins_mined = 0

def proof_of_work(block):
    """
    Simple Proof of Work Algorithm
    Stringify the block and look for a proof.
    Loop through possibilities, checking each one against `valid_proof`
    in an effort to find a number that is a valid proof
    :return: A valid proof for the provided block
    """
    # print("START PROOF OF WORK")
    block_string = json.dumps(block, sort_keys=True)
    proof = 0
    start_time = datetime.today()
    # print(f"\n\nlast block: {block_string}\n\n")
    while valid_proof(block_string, proof) is False:
        proof += 1
    end_time = datetime.today()
    print(f"TIME TAKEN: {end_time - start_time}")
    return proof

def valid_proof(block_string, proof):
    """
    Validates the Proof:  Does hash(block_string, proof) contain 6
    leading zeroes?  Return true if the proof is valid
    :param block_string: <string> The stringified block to use to
    check in combination with `proof`
    :param proof: <int?> The value that when combined with the
    stringified previous block results in a hash that has the
    correct number of leading zeroes.
    :return: True if the resulting hash is a valid proof, False otherwise
    """
    guess = f'{block_string}{proof}'.encode()
    guess_hash = hashlib.sha256(guess).hexdigest()
    # if guess_hash[:DIFFICULTY] == "0" * DIFFICULTY:
    #     print(f"DIFFICULTY: {DIFFICULTY} | GUESS_HASH: {guess_hash} | IS_VALID: {guess_hash[:DIFFICULTY] == '0' * DIFFICULTY}")

    return guess_hash[:DIFFICULTY] == "0" * DIFFICULTY


if __name__ == '__main__':
    # What is the server address? IE `python3 miner.py https://server.com/api/`
    if len(sys.argv) > 1:
        node = sys.argv[1]
    else:
        node = "http://localhost:5000"

    # Load ID
    f = open("my_id.txt", "r")
    id = f.read()
    print("ID is", id)
    f.close()

    # Run forever until interrupted
    while True:
        r = requests.get(url=node + "/last_block")
        # Handle non-json response
        try:
            data = r.json()
        except ValueError:
            print("Error:  Non-json response")
            print("Response returned:")
            print(r)
            break

        # TODO: Get the block from `data` and use it to look for a new proof
        # breakpoint() # opens python debugger
        DIFFICULTY = data["difficulty"]
        new_proof = proof_of_work(data["last_block"])

        # When found, POST it to the server {"proof": new_proof, "id": id}
        block_id = data["last_block"]["index"] + 1
        # post_data = {"proof":new_proof}
        # post_data = {"id":id}
        # post_data = {}
        # print(f'NEW BLOCK ID: {id}')
        post_data = {"proof":new_proof, "id":block_id, "user_id": id}

        r = requests.post(url=node + "/mine", json=post_data)
        # data = r.json()
        # """
        try:
            data = r.json()
        except ValueError:
            print("Error: Non-json response")
            print("Response returned:")
            print(data)
            break
        #"""

        # TODO: If the server responds with a 'message' 'New Block Forged'
        # add 1 to the number of coins mined and print it.  Otherwise,
        # print the message from the server.
        if "message" in data:
            if data["message"] == "New Block Forged":
                coins_mined += 1
                print(f"COINS MINED: {coins_mined} | Difficulty: {DIFFICULTY} | block: {data['block']}")
        else:
            print(f"Error: {data['error']}")
