import hashlib
import json
import os
from datetime import datetime

import psycopg2


# --------------------------------------------------
# Database Connection
# --------------------------------------------------

DATABASE_URL = os.getenv("DATABASE_URL")


def get_connection():

    if not DATABASE_URL:
        return None

    return psycopg2.connect(DATABASE_URL)


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

        # ------------------------------------------
        # PostgreSQL mode
        # ------------------------------------------

        if DATABASE_URL:

            self.use_database = True

            self.setup_database()

            self.load_from_database()

            if not self.chain:

                self.chain = [
                    self.create_genesis_block()
                ]

                self.save_block_to_database(
                    self.chain[0]
                )

        # ------------------------------------------
        # JSON fallback mode
        # ------------------------------------------

        else:

            self.use_database = False

            os.makedirs(
                os.path.dirname(self.storage_file),
                exist_ok=True
            )

            if os.path.exists(self.storage_file):

                self.load_chain()

            else:

                self.chain = [
                    self.create_genesis_block()
                ]

                self.save_chain()

    # --------------------------------------------------
    # Database Setup
    # --------------------------------------------------

    def setup_database(self):

        connection = get_connection()

        try:

            cursor = connection.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS blockchain (
                    id SERIAL PRIMARY KEY,
                    block_index INTEGER UNIQUE NOT NULL,
                    timestamp TEXT NOT NULL,
                    evidence_id TEXT NOT NULL,
                    action TEXT NOT NULL,
                    actor TEXT NOT NULL,
                    evidence_hash TEXT NOT NULL,
                    previous_hash TEXT NOT NULL,
                    block_hash TEXT NOT NULL
                )
            """)

            connection.commit()

            cursor.close()

        finally:

            connection.close()

    # --------------------------------------------------
    # Load Blockchain From Database
    # --------------------------------------------------

    def load_from_database(self):

        connection = get_connection()

        try:

            cursor = connection.cursor()

            cursor.execute("""
                SELECT
                    block_index,
                    timestamp,
                    evidence_id,
                    action,
                    actor,
                    evidence_hash,
                    previous_hash,
                    block_hash
                FROM blockchain
                ORDER BY block_index
            """)

            rows = cursor.fetchall()

            self.chain = []

            for row in rows:

                block = Block(
                    index=row[0],
                    timestamp=row[1],
                    evidence_id=row[2],
                    action=row[3],
                    actor=row[4],
                    evidence_hash=row[5],
                    previous_hash=row[6],
                    block_hash=row[7]
                )

                self.chain.append(block)

            cursor.close()

        finally:

            connection.close()

    # --------------------------------------------------
    # Save Block To Database
    # --------------------------------------------------

    def save_block_to_database(self, block):

        connection = get_connection()

        try:

            cursor = connection.cursor()

            cursor.execute("""
                INSERT INTO blockchain (
                    block_index,
                    timestamp,
                    evidence_id,
                    action,
                    actor,
                    evidence_hash,
                    previous_hash,
                    block_hash
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                block.index,
                block.timestamp,
                block.evidence_id,
                block.action,
                block.actor,
                block.evidence_hash,
                block.previous_hash,
                block.hash
            ))

            connection.commit()

            cursor.close()

        finally:

            connection.close()

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
    # Latest Block
    # --------------------------------------------------

    def get_latest_block(self):

        return self.chain[-1]

    # --------------------------------------------------
    # Add Block
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

        if self.use_database:

            self.save_block_to_database(
                new_block
            )

        else:

            self.save_chain()

        return new_block

    # --------------------------------------------------
    # JSON Save
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
    # JSON Load
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

        except (
            json.JSONDecodeError,
            KeyError
        ):

            self.chain = [
                self.create_genesis_block()
            ]

            self.save_chain()

    # --------------------------------------------------
    # Blockchain Validation
    # --------------------------------------------------

    def is_valid(self):

        for i in range(
            1,
            len(self.chain)
        ):

            current = self.chain[i]

            previous = self.chain[i - 1]

            if current.hash != current.calculate_hash():

                return False

            if current.previous_hash != previous.hash:

                return False

        return True