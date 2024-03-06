import requests
from flask import Flask
from storage.pwned_storage import PwnedStorage

storage = PwnedStorage("/tmp/pwned-storage")
app = Flask(__name__)


@app.route("/range/<prefix>")
def prefix_search(prefix):
    try:
        response = storage.get_range(prefix)
        return response, 200, {"Content-Type": "text/plain"}
    except:
        return "Bad prefix", 400, {"Content-Type": "text/plain"}

if __name__ == "__main__":
    app.run()
