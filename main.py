from subprocess import Popen
from flask import Flask, render_template, request
from waitress import serve

app = Flask(__name__)

@app.before_request
def before_request():
    print(f"[{request.method} REQUEST] from {request.remote_addr}\n\t{request.url}")


@app.route("/")
def index():
    return render_template("index.html")



if __name__ == "__main__":
    # cloudflared tunnel run --url 0.0.0.0:8000 beepi.shanthatos.dev
    Popen(["cloudflared", "tunnel", "run", "--url", "0.0.0.0:8000", "beepi.shanthatos.dev"])

    # app.run("0.0.0.0", 8000, debug=True)
    serve(app, listen="0.0.0.0:8000", threads=1)
