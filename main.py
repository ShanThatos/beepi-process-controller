from subprocess import Popen
from flask import Flask, render_template
from waitress import serve

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    # cloudflared tunnel run --url localhost:8000 beepi.shanthatos.dev
    Popen(["cloudflared", "tunnel", "run", "--url", "localhost:8000", "beepi.shanthatos.dev"])

    # app.run("0.0.0.0", 8000, debug=True)
    serve(app, listen="localhost:8000")
