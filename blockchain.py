import hashlib
import json
import os
from datetime import datetime


# --------------------------------------------------
# Block
# --------------------------------------------------

class Block:

    def __init__(
        self,
        index,
        evidence_id,
        action,
        actor,
        evidence_hash,
        previous_hash,
        timestamp=None,
        block_hash=None
    ):

        self.index = index

        self.timestamp = (
            timestamp
            if timestamp
            else datetime.now().isoformat()
        )

        self.evidence_id = evidence_id
        self.action = action
        self.actor = actor
        self.evidence_hash = evidence_hash
        self.previous_hash = previous_hash

        self.hash = (
            block_hash
            if block_hash
            else self.calculate_hash()
        )

    # --------------------------------------------------
    # Calculate Block Hash
    # --------------------------------------------------

    def calculate_hash(self):

        block_data = {
            "index": self.index,
            "timestamp": self.timestamp,
            "evidence_id": self.evidence_id,
            "action": self.action,
            "actor": self.actor,
            "evidence_hash": self.evidence_hash,
            "previous_hash": self.previous_hash
        }

        encoded_data = json.dumps(
            block_data,
            sort_keys=True
        ).encode()

        return hashlib.sha256(encoded_data).hexdigest()

    # --------------------------------------------------
    # Convert Block to Dictionary
    # --------------------------------------------------

    def to_dict(self):

        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "evidence_id": self.evidence_id,
            "action": self.action,
            "actor": self.actor,
            "evidence_hash": self.evidence_hash,
            "previous_hash": self.previous_hash,
            "hash": self.hash
        }

    # --------------------------------------------------
    # Create Block from Dictionary
    # --------------------------------------------------

    @staticmethod
    def from_dict(data):

        return Block(
            index=data["index"],
            evidence_id=data["evidence_id"],
            action=data["action"],
            actor=data["actor"],
            evidence_hash=data["evidence_hash"],
            previous_hash=data["previous_hash"],
            timestamp=data["timestamp"],
            block_hash=data["hash"]
        )


# ==================================================
# Blockchain
# ==================================================

class Blockchain:

    def __init__(self, storage_file="data/blockchain.json"):

        self.storage_file = storage_file

        # Create data folder if it doesn't exist
        os.makedirs(
            os.path.dirname(self.storage_file),
            exist_ok=True
        )

        # Load existing blockchain
        if os.path.exists(self.storage_file):

            self.load_chain()

        else:

            self.chain = [
                self.create_genesis_block()
            ]

            self.save_chain()

    # --------------------------------------------------
    # Genesis Block
    # --------------------------------------------------

    def create_genesis_block(self):

        return Block(
            0,
            "GENESIS",
            "BLOCKCHAIN_CREATED",
            "SYSTEM",
            "GENESIS_HASH",
            "0"
        )

    # --------------------------------------------------
    # Get Latest Block
    # --------------------------------------------------

    def get_latest_block(self):

        return self.chain[-1]

    # --------------------------------------------------
    # Add New Block
    # --------------------------------------------------

    def add_block(
        self,
        evidence_id,
        action,
        actor,
        evidence_hash
    ):

        previous_block = self.get_latest_block()

        new_block = Block(
            index=len(self.chain),
            evidence_id=evidence_id,
            action=action,
            actor=actor,
            evidence_hash=evidence_hash,
            previous_hash=previous_block.hash
        )

        self.chain.append(new_block)

        # Save blockchain immediately
        self.save_chain()

        return new_block

    # --------------------------------------------------
    # Save Blockchain
    # --------------------------------------------------

    def save_chain(self):

        data = [
            block.to_dict()
            for block in self.chain
        ]

        with open(
            self.storage_file,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                data,
                file,
                indent=4
            )

    # --------------------------------------------------
    # Load Blockchain
    # --------------------------------------------------

    def load_chain(self):

        try:

            with open(
                self.storage_file,
                "r",
                encoding="utf-8"
            ) as file:

                data = json.load(file)

            self.chain = [
                Block.from_dict(block)
                for block in data
            ]

        except (json.JSONDecodeError, KeyError):

            # If file is corrupted,
            # create a fresh blockchain

            self.chain = [
                self.create_genesis_block()
            ]

            self.save_chain()

    # --------------------------------------------------
    # Validate Blockchain
    # --------------------------------------------------

    def is_valid(self):

        for i in range(1, len(self.chain)):

            current = self.chain[i]

            previous = self.chain[i - 1]

            # Check current block hash
            if current.hash != current.calculate_hash():

                return False

            # Check connection with previous block
            if current.previous_hash != previous.hash:

                return False

        return True