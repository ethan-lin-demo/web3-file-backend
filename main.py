"""basic services"""
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qsl
import os
import json
from requests_toolbelt.multipart import decoder
from ifps_file import add_file

port = int(os.environ.get("PORT", 3030))


def get_query_params(query, need_key, default=None):
    """get query parameters"""
    query_params = parse_qsl(query)
    for key, value in query_params:
        if need_key == key:
            return value
    return default


def auth(func):
    """auth user"""

    def warp(query, *args, **kwargs):
        password = get_query_params(query, "password", default="")
        if password != "test":
            return b""
        return func(query, *args, **kwargs)

    return warp


@auth
def login(_query):
    """login"""
    return b"test"


routes = {
    "login": login,
}


class MyHandler(BaseHTTPRequestHandler):
    """basic http server"""

    def do_OPTIONS(self):  # pylint: disable=invalid-name
        """rewrite do options"""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.end_headers()
        self.wfile.write(b"ok~")

    def do_POST(self):  # pylint: disable=invalid-name
        """rewrite do post"""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        parsed = urlparse(self.path)
        handler = routes.get(parsed.path[1:])
        if (
            handler != "upload"
            and get_query_params(parsed.query, "password", default="") != "test"
        ):
            self.wfile.write(b"404")
            return

        content_len = int(self.headers.get("Content-Length"))
        post_body = self.rfile.read(content_len)

        content_type = self.headers.get("Content-Type")
        multipart_data = decoder.MultipartDecoder(post_body, content_type).parts
        file = multipart_data[0]
        file_name = (
            file.headers[b"Content-Disposition"].decode().split("filename=")[-1][1:-1]
        )
        file_data = file.content
        file_url = add_file(file_data)

        self.wfile.write(
            json.dumps(
                {
                    "name": file_name,
                    "url": file_url,
                }
            ).encode()
        )

    def do_GET(self):  # pylint: disable=invalid-name
        """rewrite do get"""
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        parsed = urlparse(self.path)
        handler = routes.get(parsed.path[1:])
        if handler:
            self.wfile.write(handler(parsed.query))
        else:
            self.wfile.write(b"404")

    def log_message(self, *_args, **_kws):
        pass


server = HTTPServer(("", port), MyHandler)
print("Starting server, use <Ctrl-C> to stop")
server.serve_forever()
