from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


# with open("./ouch.txt", "w") as f:
#     f.write("hoooo")


app.run("0.0.0.0", 8000, debug=True)
