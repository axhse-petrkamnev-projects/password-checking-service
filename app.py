import requests
from flask import Flask, render_template
from storage.pwned_storage import PwnedStorage

storage = PwnedStorage("/tmp/pwned-storage")
app = Flask(__name__, template_folder="templates")

@app.route('/')
def home():
    return render_template('client-page.html')

@app.route("/range/<prefix>")
def prefix_search(prefix):
    try:
        response = storage.get_range(prefix)
        return response, 200, {"Content-Type": "text/plain"}
    except:
        return "Bad prefix", 400, {"Content-Type": "text/plain"}

if __name__ == "__main__":
    app.run()
