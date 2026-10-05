from flask import Flask, render_template, request, redirect, url_for
import hashlib
import os

from blockchain import Blockchain


app = Flask(__name__)


UPLOAD_FOLDER = "uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


blockchain = Blockchain()


def calculate_file_hash(file_path):

    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:

        while True:

            data = file.read(4096)

            if not data:
                break

            sha256.update(data)

    return sha256.hexdigest()


@app.route("/")
def home():

    return render_template(
        "index.html",
        chain=blockchain.chain,
        valid=blockchain.is_valid(),
        result=None
    )


# -----------------------------------------
# REGISTER EVIDENCE
# -----------------------------------------

@app.route("/register", methods=["POST"])
def register():

    evidence_id = request.form["evidence_id"].strip()

    actor = request.form["actor"].strip()

    evidence_file = request.files["evidence"]

    if evidence_file.filename == "":
        return redirect(url_for("home"))

    filename = evidence_file.filename

    filepath = os.path.join(
        app.config["UPLOAD_FOLDER"],
        filename
    )

    evidence_file.save(filepath)

    file_hash = calculate_file_hash(filepath)

    blockchain.add_block(
        evidence_id=evidence_id,
        action="REGISTERED",
        actor=actor,
        evidence_hash=file_hash
    )

    return redirect(url_for("home"))


# -----------------------------------------
# VERIFY EVIDENCE
# -----------------------------------------

@app.route("/verify", methods=["POST"])
def verify():

    evidence_id = request.form["evidence_id"].strip()

    evidence_file = request.files["evidence"]

    if evidence_file.filename == "":
        return redirect(url_for("home"))

    temp_filename = "verification_" + evidence_file.filename

    temp_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        temp_filename
    )

    evidence_file.save(temp_path)

    uploaded_hash = calculate_file_hash(temp_path)

    os.remove(temp_path)

    matched_block = None

    for block in blockchain.chain:

        if (
            block.evidence_id == evidence_id
            and block.action == "REGISTERED"
        ):

            matched_block = block

            break

    if matched_block:

        if matched_block.evidence_hash == uploaded_hash:

            result = {

                "status": "VALID",

                "message":
                "Evidence is authentic. File content matches the blockchain record.",

                "block": matched_block

            }

        else:

            result = {

                "status": "TAMPERED",

                "message":
                "Evidence ID exists, but the uploaded file has been modified.",

                "block": matched_block

            }

    else:

        result = {

            "status": "NOT_FOUND",

            "message":
            "No blockchain record was found for this Evidence ID.",

            "block": None

        }

    return render_template(

        "index.html",

        chain=blockchain.chain,

        valid=blockchain.is_valid(),

        result=result

    )


# -----------------------------------------
# CHAIN OF CUSTODY
# -----------------------------------------

@app.route("/custody", methods=["POST"])
def custody():

    evidence_id = request.form["evidence_id"].strip()

    action = request.form["action"].strip()

    actor = request.form["actor"].strip()

    allowed_actions = [
        "TRANSFERRED",
        "RECEIVED",
        "VERIFIED"
    ]

    if action not in allowed_actions:

        return redirect(url_for("home"))

    evidence_exists = False

    for block in blockchain.chain:

        if (
            block.evidence_id == evidence_id
            and block.action == "REGISTERED"
        ):

            evidence_exists = True
            break

    if not evidence_exists:

        result = {

            "status": "NOT_FOUND",

            "message":
            "No registered evidence was found for this Evidence ID.",

            "block": None

        }

        return render_template(

            "index.html",

            chain=blockchain.chain,

            valid=blockchain.is_valid(),

            result=result

        )

    latest_evidence_hash = None

    for block in blockchain.chain:

        if block.evidence_id == evidence_id:

            latest_evidence_hash = block.evidence_hash

    blockchain.add_block(

        evidence_id=evidence_id,

        action=action,

        actor=actor,

        evidence_hash=latest_evidence_hash

    )

    return redirect(url_for("home"))


# -----------------------------------------
# BLOCKCHAIN VALIDATION
# -----------------------------------------

@app.route("/validate")
def validate():

    return render_template(

        "index.html",

        chain=blockchain.chain,

        valid=blockchain.is_valid(),

        result=None

    )


# -----------------------------------------
# RUN APPLICATION
# -----------------------------------------

if __name__ == "__main__":

    import webbrowser

    from threading import Timer

    def open_browser():

        webbrowser.open_new(
            "http://127.0.0.1:5000"
        )

    Timer(
        1,
        open_browser
    ).start()

    app.run(
        debug=True,
        use_reloader=False
    )
