from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os

PORT = 8000


class PackCheckServer(BaseHTTPRequestHandler):

    def send_json(self, data, status=200):
        body = json.dumps(data).encode("utf-8")

        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header(
            "Access-Control-Allow-Methods",
            "POST, GET, OPTIONS"
        )
        self.send_header(
            "Access-Control-Allow-Headers",
            "Content-Type"
        )
        self.end_headers()

        self.wfile.write(body)

    # ==========================================
    # GET /packcheck_result.json
    # ==========================================

    def do_GET(self):

        if self.path == "/packcheck_result.json":

            try:
                BASE_DIR = os.path.dirname(
                    os.path.abspath(__file__)
                )

                file_path = os.path.join(
                    BASE_DIR,
                    "packcheck_result.json"
                )

                with open(
                    file_path,
                    "r",
                    encoding="utf-8"
                ) as f:

                    data = json.load(f)

                self.send_json(data)

            except Exception as e:

                self.send_json(
                    {
                        "success": False,
                        "error": str(e)
                    },
                    500
                )

        else:

            self.send_json(
                {
                    "success": False,
                    "error": "Unknown endpoint"
                },
                404
            )

    # ==========================================
    # OPTIONS
    # ==========================================

    def do_OPTIONS(self):

        self.send_response(200)

        self.send_header(
            "Access-Control-Allow-Origin",
            "*"
        )

        self.send_header(
            "Access-Control-Allow-Methods",
            "POST, GET, OPTIONS"
        )

        self.send_header(
            "Access-Control-Allow-Headers",
            "Content-Type"
        )

        self.end_headers()

    # ==========================================
    # POST /save-verification
    # ==========================================

    def do_POST(self):

        if self.path != "/save-verification":

            self.send_json(
                {
                    "success": False,
                    "error": "Unknown endpoint"
                },
                404
            )

            return

        try:

            content_length = int(
                self.headers.get(
                    "Content-Length",
                    0
                )
            )

            body = self.rfile.read(
                content_length
            )

            data = json.loads(
                body.decode("utf-8")
            )

            BASE_DIR = os.path.dirname(
                os.path.abspath(__file__)
            )

            verification_path = os.path.join(
                BASE_DIR,
                "verification_result.json"
            )

            with open(
                verification_path,
                "w",
                encoding="utf-8"
            ) as f:

                json.dump(
                    data,
                    f,
                    indent=2,
                    ensure_ascii=False
                )

            print(
                f"✅ Verification result saved: "
                f"{verification_path}"
            )

            self.send_json(
                {
                    "success": True,
                    "message": "Verification saved"
                }
            )

        except Exception as e:

            print(
                "❌ Error:",
                e
            )

            self.send_json(
                {
                    "success": False,
                    "error": str(e)
                },
                500
            )


# ==========================================
# START SERVER
# ==========================================

if __name__ == "__main__":

    server = HTTPServer(
        ("localhost", PORT),
        PackCheckServer
    )

    print("==============================================")
    print("🚀 PACKCHECK REPORT SERVER")
    print("==============================================")
    print(
        f"Server running at http://localhost:{PORT}"
    )
    print(
        "Waiting for FoSCoS verification..."
    )
    print(
        "Press CTRL+C to stop."
    )
    print("==============================================")

    server.serve_forever()