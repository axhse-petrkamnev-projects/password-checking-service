import os
import traceback

from flask import Flask, render_template

from storage.implementations.pwned_storage import PwnedStorage


def create_app():
    app = Flask(__name__, template_folder="templates")

    storage_path = os.getenv("RESOURCE_DIR", "/tmp/pwned-storage")
    storage = PwnedStorage(storage_path)

    @app.route("/")
    def home():
        return render_template("client-page.html")

    @app.route("/range/<prefix>")
    async def prefix_search(prefix):
        try:
            response = await storage.get_range(prefix)
            return response, 200, {"Content-Type": "text/plain"}
        except Exception:
            traceback.print_exc()
            return "Bad prefix", 400, {"Content-Type": "text/plain"}

    return app


if __name__ == "__main__":
    app = create_app()
    app.run()
