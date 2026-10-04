from flask import Flask, render_template, request, redirect, url_for
import hashlib
import os

from blockchain import Blockchain


app = Flask(__name__)


# ==================================================
# Configuration
# ==================================================

UPLOAD_FOLDER = "uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# ==================================================
# Create Blockchain
# ==================================================

blockchain = Blockchain()


# ==================================================
# Calculate SHA-256 File Hash
# ==================================================

def calculate_file_hash(file_path):

    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:

        while True:

            data = file.read(4096)

            if not data:
                break

            sha256.update(data)

    return sha256.hexdigest()


# ==================================================
# Home Page
# ==================================================

@app.route("/")
def home():

    return render_template(
        "index.html",
        chain=blockchain.chain,
        valid=blockchain.is_valid(),
        result=None
    )


# ==================================================
# Register Evidence
# ==================================================

@app.route("/register", methods=["POST"])
def register():

    evidence_id = request.form["evidence_id"]

    actor = request.form["actor"]

    evidence_file = request.files["evidence"]


    # Check file
    if evidence_file.filename == "":
        return redirect(url_for("home"))


    # --------------------------------------------------
    # Save Evidence File
    # --------------------------------------------------

    filename = evidence_file.filename

    filepath = os.path.join(
        app.config["UPLOAD_FOLDER"],
        filename
    )

    evidence_file.save(filepath)


    # --------------------------------------------------
    # Calculate SHA-256
    # --------------------------------------------------

    file_hash = calculate_file_hash(filepath)


    # --------------------------------------------------
    # Add Evidence to Blockchain
    # --------------------------------------------------

    blockchain.add_block(
        evidence_id=evidence_id,
        action="REGISTERED",
        actor=actor,
        evidence_hash=file_hash
    )


    return redirect(url_for("home"))


# ==================================================
# Verify Evidence
# ==================================================

@app.route("/verify", methods=["POST"])
def verify():

    evidence_file = request.files["evidence"]


    # Check file
    if evidence_file.filename == "":
        return redirect(url_for("home"))


    # --------------------------------------------------
    # Save Temporary File
    # --------------------------------------------------

    temp_filename = "verification_" + evidence_file.filename

    temp_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        temp_filename
    )

    evidence_file.save(temp_path)


    # --------------------------------------------------
    # Calculate Uploaded File Hash
    # --------------------------------------------------

    uploaded_hash = calculate_file_hash(temp_path)


    # Delete temporary file
    os.remove(temp_path)


    # --------------------------------------------------
    # Search Blockchain
    # --------------------------------------------------

    matched_block = None

    for block in blockchain.chain:

        if block.evidence_hash == uploaded_hash:

            matched_block = block

            break


    # --------------------------------------------------
    # Verification Result
    # --------------------------------------------------

    if matched_block:

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
            "Evidence does not match any registered blockchain record.",

            "block": None

        }


    return render_template(

        "index.html",

        chain=blockchain.chain,

        valid=blockchain.is_valid(),

        result=result

    )


# ==================================================
# Validate Blockchain
# ==================================================

@app.route("/validate")
def validate():

    return render_template(

        "index.html",

        chain=blockchain.chain,

        valid=blockchain.is_valid(),

        result=None

    )


# ==================================================
# Start Application
# ==================================================

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