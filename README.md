# 🔐 EvidenceChain

## Blockchain-Based Digital Evidence Integrity & Chain-of-Custody Verification

EvidenceChain is a web-based academic prototype that uses **SHA-256 hashing** and a **custom blockchain** to verify the integrity of digital evidence and maintain a tamper-evident chain of custody.

The system generates a cryptographic hash from the contents of an uploaded evidence file and records that hash along with evidence and custody metadata in a blockchain. When the evidence is uploaded again for verification, its hash is compared with the blockchain record to determine whether the file content is unchanged or has been modified.

The blockchain data is persistently stored using **PostgreSQL on Neon**, while the Flask application is deployed on **Render**.

> **Note:** EvidenceChain is an academic prototype for demonstrating blockchain, cryptographic hashing, database persistence, and chain-of-custody concepts. It is not intended to replace certified forensic evidence-management systems or establish legal authenticity of evidence.

---

## 🎯 Objectives

- Maintain the integrity of digital evidence using SHA-256.
- Detect modifications to registered evidence files.
- Store evidence records in a tamper-evident blockchain.
- Maintain a chronological chain of custody.
- Provide evidence verification through hash comparison.
- Detect modifications to blockchain data through hash validation.
- Persist blockchain records using PostgreSQL.
- Deploy the application as a web-based system.

---

## ✨ Features

### 📁 Evidence Registration

Users can register a digital evidence file by providing:

- Evidence ID
- Actor name
- Evidence file

The application calculates the file's **SHA-256 hash** and stores it in a blockchain block.

### 🔍 Evidence Verification

Users can upload an evidence file together with its Evidence ID.

The system:

1. Calculates the SHA-256 hash of the uploaded file.
2. Finds the registered blockchain record.
3. Compares the uploaded hash with the stored hash.
4. Returns the verification result.

Possible results:

- **VALID** — file content matches the registered hash.
- **TAMPERED** — Evidence ID exists, but file content has changed.
- **NOT_FOUND** — no registered record exists for the supplied Evidence ID.

### 🔄 Chain of Custody

EvidenceChain records custody events for registered evidence:

- **REGISTERED**
- **TRANSFERRED**
- **RECEIVED**
- **VERIFIED**

Each custody event becomes a new blockchain block linked to the previous block.

### ⛓️ Blockchain Integrity Validation

Every block contains:

- Block index
- Timestamp
- Evidence ID
- Action
- Actor
- Evidence hash
- Previous block hash
- Current block hash

The application recalculates block hashes and checks the links between consecutive blocks.

If blockchain data is modified, the integrity status changes from:

**✅ VALID**

to:

**❌ COMPROMISED**

---

## 🧠 How the System Works

```text
                    EvidenceChain
                         │
                         ▼
                  Upload Evidence
                         │
                         ▼
                    SHA-256 Hash
                         │
                         ▼
                Create Blockchain Block
                         │
                         ▼
                PostgreSQL / Neon
                         │
                         ▼
                Evidence Verification
                         │
                ┌────────┼────────┐
                ▼        ▼        ▼
              VALID   TAMPERED  NOT_FOUND
```

### Chain-of-Custody Flow

```text
REGISTERED
     │
     ▼
TRANSFERRED
     │
     ▼
RECEIVED
     │
     ▼
VERIFIED
```

Each event is recorded as a separate blockchain block.

---

## 🔗 Blockchain Structure

Each block stores the hash of the previous block.

```text
┌──────────────┐
│   Block #0   │
│   GENESIS    │
│ Hash: ABC... │
└──────┬───────┘
       │ Previous Hash
       ▼
┌──────────────┐
│   Block #1   │
│ REGISTERED   │
│ Hash: DEF... │
└──────┬───────┘
       │ Previous Hash
       ▼
┌──────────────┐
│   Block #2   │
│ TRANSFERRED  │
│ Hash: GHI... │
└──────┬───────┘
       │ Previous Hash
       ▼
┌──────────────┐
│   Block #3   │
│  RECEIVED    │
│ Hash: JKL... │
└──────────────┘
```

Changing data in an earlier block changes its calculated hash. Later blocks still contain the old previous hash, allowing the application to detect the inconsistency.

---

## 🔐 SHA-256 Integrity Verification

EvidenceChain uses **SHA-256 (Secure Hash Algorithm 256-bit)** to generate a fixed-length cryptographic hash of each evidence file.

For example:

```text
Evidence File
     ↓
SHA-256
     ↓
f88da8b6c05bfb6713f56bfb782d0bbcc8772b52f7600af8bfac48417fb98872
```

The system stores the hash rather than relying on the filename.

Therefore:

- Renaming a file does **not** change its hash.
- Changing the file content produces a different hash.
- The modified hash will not match the blockchain record.

---

## 🏗️ System Architecture

```text
┌───────────────────────────────┐
│         Web Browser           │
│       HTML / CSS / JS         │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│        Flask Application      │
│            app.py             │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│       Blockchain Module       │
│        blockchain.py          │
│                               │
│  • Block Creation             │
│  • Hash Calculation           │
│  • Chain Validation            │
│  • Evidence Records            │
│  • Custody Events              │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│       PostgreSQL Database      │
│            Neon               │
└───────────────────────────────┘
```

---

## 🧩 System Modules

### 1. Evidence Registration Module

Accepts evidence details and calculates the SHA-256 hash of the uploaded file.

### 2. Evidence Verification Module

Compares the hash of an uploaded file with the registered blockchain hash.

### 3. Chain-of-Custody Module

Records evidence movement and verification through custody events.

### 4. Blockchain Integrity Module

Validates block hashes and previous-hash relationships.

### 5. Database Persistence Module

Stores blockchain blocks in PostgreSQL using Neon.

### 6. Web Interface Module

Provides the user interface for registration, verification, custody recording, and blockchain exploration.

---

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Flask | Web application framework |
| SHA-256 | Evidence integrity verification |
| Custom Blockchain | Tamper-evident record structure |
| PostgreSQL | Persistent database |
| Neon | Cloud PostgreSQL database |
| HTML | Web page structure |
| CSS | User interface styling |
| JavaScript | Client-side functionality |
| Git | Version control |
| GitHub | Source code repository |
| Render | Web application deployment |

---

## 📁 Project Structure

```text
EvidenceChain/
│
├── app.py
├── blockchain.py
├── requirements.txt
├── render.yaml
│
├── templates/
│   └── index.html
│
├── static/
│   └── style.css
│
├── uploads/
│   └── .gitkeep
│
└── data/
    ├── blockchain.json
    └── blockchain_backup.json
```

### Important

The JSON files are used as a local fallback when a PostgreSQL `DATABASE_URL` is not configured.

In the deployed application, blockchain persistence uses PostgreSQL through Neon.

Uploaded evidence files and database credentials are not committed to the GitHub repository.

---

## ⚙️ Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/RNKIEE/EvidenceChain.git
cd EvidenceChain
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the virtual environment

Windows PowerShell:

```powershell
venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure PostgreSQL

Set the `DATABASE_URL` environment variable to your PostgreSQL connection string.

Windows PowerShell example:

```powershell
$env:DATABASE_URL="YOUR_DATABASE_CONNECTION_STRING"
```

> Never commit or publicly share the database connection string.

### 6. Run the application

```bash
python app.py
```

The application will be available locally at:

```text
http://127.0.0.1:5000
```

---

## 🌐 Deployment

The application is deployed using:

- **GitHub** — source code
- **Render** — Flask web application
- **Neon** — PostgreSQL database

The deployed application uses the `DATABASE_URL` environment variable configured on the hosting platform.

---

## 🧪 Testing

The following functional tests were performed:

| Test | Expected Result | Status |
|---|---|---|
| Register new evidence | Blockchain block created | ✅ Pass |
| Verify original file | VALID | ✅ Pass |
| Verify modified file | TAMPERED | ✅ Pass |
| Verify unknown Evidence ID | NOT_FOUND | ✅ Pass |
| Transfer evidence | TRANSFERRED block created | ✅ Pass |
| Receive evidence | RECEIVED block created | ✅ Pass |
| Verify custody | VERIFIED block created | ✅ Pass |
| Validate blockchain | VALID | ✅ Pass |
| Store blocks in Neon | Records persist | ✅ Pass |
| Load records after deployment | Existing blocks displayed | ✅ Pass |

---

## 📊 Example Blockchain Record

A successful test produced the following chain:

```text
Block #0
Evidence ID: GENESIS
Action: BLOCKCHAIN_CREATED
Actor: SYSTEM

        ↓

Block #1
Evidence ID: NEON001
Action: REGISTERED
Actor: Laksh

        ↓

Block #2
Evidence ID: NEON001
Action: TRANSFERRED
Actor: Officer A

        ↓

Block #3
Evidence ID: NEON001
Action: RECEIVED
Actor: Officer B

        ↓

Block #4
Evidence ID: NEON001
Action: VERIFIED
Actor: Forensic Lab
```

All blocks maintained valid hash relationships and the application reported:

```text
Blockchain Integrity: VALID
```

---

## ⚠️ Limitations

- This is an academic prototype rather than a production forensic system.
- The custom blockchain is implemented within the application and is not a decentralized public blockchain network.
- The system does not provide legal certification of evidence.
- Evidence authenticity before registration cannot be independently established by the system.
- Authentication and role-based access control are not currently implemented.
- Uploaded evidence files are not stored permanently as part of the blockchain.
- The blockchain database is centralized through PostgreSQL/Neon.
- Production forensic deployments would require stronger security, access control, audit policies, backup mechanisms, and compliance requirements.

---

## 🚀 Future Scope

Possible future improvements include:

- User authentication and role-based access control.
- Digital signatures for evidence and custody events.
- Multi-user or multi-organization blockchain architecture.
- Decentralized blockchain or distributed ledger integration.
- Secure object storage for evidence files.
- Advanced audit logs.
- Evidence metadata management.
- QR-code-based evidence tracking.
- Notifications for custody transfers.
- Automated forensic workflow integration.
- Stronger security and compliance controls.

---

## 🎓 Academic Use

EvidenceChain demonstrates the practical application of:

- Blockchain concepts
- Cryptographic hashing
- SHA-256
- Data integrity
- Chain of custody
- PostgreSQL database persistence
- Flask web development
- Cloud deployment

It can be used as an academic demonstration of how blockchain-style hash chaining can support **digital evidence integrity and traceability**.

---

## 👩‍💻 Project

**EvidenceChain**

**Blockchain-Based Digital Evidence Integrity & Chain-of-Custody Verification**

Built as an academic project using Python, Flask, custom blockchain logic, SHA-256, PostgreSQL, Neon, GitHub, and Render.