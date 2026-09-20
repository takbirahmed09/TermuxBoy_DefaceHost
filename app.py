from flask import Flask, request, jsonify, Response
import os, random, string, json

app = Flask(__name__)

DATA_DIR = "data"

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

def generate_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))


@app.route("/save", methods=["POST"])
def save():
    code = request.form.get("code")

    file_id = generate_id()
    file_path = os.path.join(DATA_DIR, f"{file_id}.txt")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(code)

    return jsonify({
        "url": f"/raw/{file_id}"
    })


@app.route("/raw/<file_id>")
def raw(file_id):
    file_path = os.path.join(DATA_DIR, f"{file_id}.txt")

    if not os.path.exists(file_path):
        return Response("console.log('Not Found');", mimetype="application/javascript")

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    encoded = json.dumps(content)

    js = f"""
    document.open();
    document.write({encoded});
    document.close();
    """

    return Response(js, mimetype="application/javascript")


# 🔥 MAIN UI PAGE
@app.route("/")
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>JS Loader Generator</title>
        <style>
            body {
                background: #111;
                color: lime;
                text-align: center;
                font-family: Arial;
                padding: 20px;
            }
            textarea {
                width: 90%;
                height: 250px;
                background: black;
                color: lime;
                border: 1px solid #333;
                padding: 10px;
            }
            button {
                margin-top: 10px;
                padding: 10px 20px;
                background: lime;
                border: none;
                cursor: pointer;
            }
            #result {
                margin-top: 20px;
                background: black;
                padding: 10px;
            }
        </style>
    </head>
    <body>

    <h2>🔥 JS Loader Generator</h2>

    <textarea id="code" placeholder="Paste HTML or JS here..."></textarea>
    <br>

    <button onclick="upload()">Generate URL</button>

    <div id="result"></div>

    <button onclick="copy()">Copy</button>

    <script>
    function upload(){
        let code = document.getElementById("code").value;

        fetch("/save", {
            method: "POST",
            headers: {"Content-Type": "application/x-www-form-urlencoded"},
            body: "code=" + encodeURIComponent(code)
        })
        .then(r => r.json())
        .then(data => {
            let url = location.origin + data.url;
            let tag = '<script src="'+url+'"></'+'script>';
            document.getElementById("result").innerText = tag;
        });
    }

    function copy(){
        let text = document.getElementById("result").innerText;
        navigator.clipboard.writeText(text);
        alert("Copied!");
    }
    </script>

    </body>
    </html>
    """


if __name__ == "__main__":
    app.run()
