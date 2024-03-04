import http.server
import urllib.parse
import requests

class PwnedPasswordsHandler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            # Extract the first 5 characters of the hash from the URL
            path = urllib.parse.urlparse(self.path).path
            hash_prefix = path.split('/')[-1]

            # Make a request to the Pwned Passwords API
            response = requests.get(f"https://api.pwnedpasswords.com/range/{hash_prefix}")

            if response.status_code == 200:
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(response.text.encode())
            else:
                self.send_error(500, "Internal Server Error")

        except Exception as e:
            self.send_error(500, str(e))

def run(server_class=http.server.HTTPServer, handler_class=PwnedPasswordsHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting server on port {port}...")
    httpd.serve_forever()

if __name__ == "__main__":
    run()
