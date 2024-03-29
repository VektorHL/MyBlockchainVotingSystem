import hashlib
import json
import random
from time import time
from urllib.parse import urlparse
from uuid import uuid4

import requests
from flask import Flask, jsonify, request


class Blockchain:
    def __init__(self, question):
        #self.current_transactions = []
        self.chain = []
        self.nodes = set()
        #self.data = ["Голосуем за внесение поправок в конституцию. Да или нет?"]

        # Create the genesis block
        genesis = self.new_block(previous_hash='1', proof=100, my_vote=question)
        self.chain = [genesis]

    def register_node(self, address):
        parsed_url = urlparse(address)
        if parsed_url.netloc:
            self.nodes.add(parsed_url.netloc)
        elif parsed_url.path:
            # Accepts an URL without scheme like '192.168.0.5:5000'.
            self.nodes.add(parsed_url.path)
        else:
            raise ValueError('Invalid URL')

    def valid_chain(self, chain):
        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            print(f'{last_block}')
            print(f'{block}')
            print("\n-----------\n")
            # Check that the hash of the block is correct
            if block['previous_hash'] != self.hash(last_block):
                return False

            # Check that the Proof of Work is correct
            if not self.valid_proof(block):
                return False

            last_block = block
            current_index += 1

        return True

    def resolve_conflicts(self):
        neighbours = self.nodes
        new_chain = None

        # We're only looking for chains longer than ours
        max_length = len(self.chain)

        # Grab and verify the chains from all the nodes in our network
        for node in neighbours:
            response = requests.get(f'http://{node}/chain')

            print(response)
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                # Check if the length is longer and the chain is valid
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        # Replace our chain if we discovered a new, valid chain longer than ours
        if new_chain:
            self.chain = new_chain
            return True

        return False

    def new_block(self, proof, previous_hash, my_vote):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            #'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
            'vote': my_vote,
        }

        # Reset the current list of transactions
        #self.current_transactions = []
        return block

    # def new_transaction(self, sender, recipient, amount):
    #     self.current_transactions.append({
    #         'sender': sender,
    #         'recipient': recipient,
    #         'amount': amount,
    #     })
    #
    #     return self.last_block['index'] + 1

    # def new_vote(self, sender, recipient, amount, my_vote):
    #     self.current_transactions.append({
    #         'sender': sender,
    #         'recipient': recipient,
    #         'amount': amount,
    #         'vote': my_vote,
    #     })
    #
    #     return self.last_block['index'] + 1

    @property
    def last_block(self):
        return self.chain[-1]

    @staticmethod
    def hash(block):
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def proof_of_work(self, current_block):
        while self.valid_proof(current_block) is False:
            current_block["proof"] += 1
        return current_block

    def valid_proof(self, block):
        guess = self.hash(block)
        return guess[:4] == "0000"


app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

node_identifier = str(uuid4()).replace('-', '')

vote_question = "Голосуем за внесение поправок в конституцию. Да или нет?"

blockchain = Blockchain(vote_question)
print(blockchain.chain[0])


@app.route('/')
def index():
    return blockchain.chain[0]['vote']

@app.route('/mine', methods=['GET'])
def mine():
    last_block = blockchain.last_block

    # blockchain.new_transaction(
    #     sender="0",
    #     recipient=node_identifier,
    #     amount=1,
    # )

    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(0, previous_hash, "yes?")

    proofed = blockchain.proof_of_work(block)
    blockchain.chain.append(proofed)

    response = {
        'message': "New Block Forged",
        'index': proofed['index'],
        #'transactions': proofed['transactions'],
        'proof': proofed['proof'],
        'previous_hash': proofed['previous_hash'],
        'vote': proofed['vote'],
    }
    return jsonify(response), 200


@app.route('/vote', methods=['GET'])
def vote():
    last_block = blockchain.last_block

    # blockchain.new_vote(
    #     sender="0",
    #     recipient=node_identifier,
    #     amount=1,
    #     vote="yes",
    # )
    #test_vote = "yes"

    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(0, previous_hash, "test_vote")

    proofed = blockchain.proof_of_work(block)
    blockchain.chain.append(proofed)

    response = {
        'message': "New Block Forged",
        'index': proofed['index'],
        #'transactions': proofed['transactions'],
        'proof': proofed['proof'],
        'previous_hash': proofed['previous_hash'],
        'vote': proofed['vote'],
    }
    return jsonify(response), 200


@app.route('/vote/yes', methods=['GET'])
def vote_yes():
    last_block = blockchain.last_block

    vote = "yes"

    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(0, previous_hash, vote)

    proofed = blockchain.proof_of_work(block)
    blockchain.chain.append(proofed)

    response = {
        #'message': "New Block Forged",
        'index': proofed['index'],
        'proof': proofed['proof'],
        'previous_hash': proofed['previous_hash'],
        'vote': proofed['vote'],
    }
    return jsonify(response), 200


@app.route('/vote/no', methods=['GET'])
def vote_no():
    last_block = blockchain.last_block

    vote = "no"

    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(0, previous_hash, vote)

    proofed = blockchain.proof_of_work(block)
    blockchain.chain.append(proofed)

    response = {
        #'message': "New Block Forged",
        'index': proofed['index'],
        'proof': proofed['proof'],
        'previous_hash': proofed['previous_hash'],
        'vote': proofed['vote'],
    }
    return jsonify(response), 200


@app.route('/vote/randomize', methods=['GET'])
def vote_rand():
    yes = random.randrange(5)
    no = random.randrange(5)
    for _ in range(no):
        vote_no()
    for _ in range(yes):
        vote_yes()
    response = f'Added {yes} positive and {no} negative votes'
    return response, 200


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200


@app.route('/results', methods=['GET'])
def show_results():
    yes_count = no_count = 0
    for i in range(len(blockchain.chain)):
        if blockchain.chain[i]['vote'] == "yes":
            yes_count += 1
        elif blockchain.chain[i]['vote'] == "no":
            no_count += 1
    browser_new_line = "<br>"
    votes = f"Voted for: {yes_count}{browser_new_line}Voted against: {no_count}"
    # votes_no = f"Voted for: {yes_count} Voted against: {no_count}"

    return votes, 200


@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json(force=True, silent=True, cache=False)
    print(values)

    nodes = values.get("nodes")
    print(nodes)
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 201


@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain
        }

    return jsonify(response), 200


@app.route('/nodes', methods=['GET'])
def consensusasd():
    print(blockchain.nodes)


    return jsonify(list(blockchain.nodes)), 200


@app.route('/ping', methods=['GET'])
def ping():
    return "", 200


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='0.0.0.0', port=port)
