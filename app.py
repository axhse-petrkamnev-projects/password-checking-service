from flask import Flask
import requests

app = Flask(__name__)


@app.route('/range/<prefix>')
def prefix_search(prefix):  # put application's code here
    response = requests.get(f"https://api.pwnedpasswords.com/range/{prefix}")

    if response.status_code == 200:
        return response.text, 200, {'Content-Type': 'text/plain'}
    else:
        return "Internal Server Error", 500


if __name__ == '__main__':
    app.run()
