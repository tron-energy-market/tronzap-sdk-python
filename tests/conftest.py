import json
import ssl
import threading
import time
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Callable, Dict, Iterator, List, Optional, Tuple

import pytest
import trustme

from tronzap_sdk import Client

API_TOKEN = "test-token"
API_SECRET = "test-secret"


@dataclass
class ReceivedRequest:
    method: str
    path: str
    headers: Dict[str, str]
    body: bytes

    @property
    def json(self) -> Any:
        return json.loads(self.body)


Responder = Callable[[ReceivedRequest], Tuple[int, str]]


@dataclass
class ApiServer:
    url: str
    requests: List[ReceivedRequest] = field(default_factory=list)
    status: int = 200
    body: str = '{"code": 0, "result": {}}'
    delay: float = 0.0
    responder: Optional[Responder] = None
    lock: threading.Lock = field(default_factory=threading.Lock)

    def respond(self, status: int, body: Any) -> None:
        self.status = status
        self.body = body if isinstance(body, str) else json.dumps(body)

    def ok(self, result: Any) -> None:
        self.respond(200, {"code": 0, "result": result})

    @property
    def last(self) -> ReceivedRequest:
        assert self.requests, "the server received no request"
        return self.requests[-1]


def _start(server_state: ApiServer, ssl_context: Optional[ssl.SSLContext]) -> ThreadingHTTPServer:
    class Handler(BaseHTTPRequestHandler):
        def do_POST(self) -> None:
            length = int(self.headers.get("Content-Length", 0))
            received = ReceivedRequest(
                method="POST",
                path=self.path,
                headers={k.lower(): v for k, v in self.headers.items()},
                body=self.rfile.read(length),
            )
            with server_state.lock:
                server_state.requests.append(received)
            if server_state.delay:
                time.sleep(server_state.delay)
            if server_state.responder is not None:
                status, body = server_state.responder(received)
            else:
                status, body = server_state.status, server_state.body
            payload = body.encode()
            try:
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
            except (BrokenPipeError, ConnectionResetError):
                pass

        def log_message(self, format: str, *args: Any) -> None:
            pass

    class Server(ThreadingHTTPServer):
        # The default backlog of 5 makes Linux reset connections under the concurrency test.
        request_queue_size = 128

    httpd = Server(("127.0.0.1", 0), Handler)
    httpd.daemon_threads = True
    if ssl_context is not None:
        httpd.socket = ssl_context.wrap_socket(httpd.socket, server_side=True)
    threading.Thread(target=httpd.serve_forever, args=(0.01,), daemon=True).start()
    return httpd


@pytest.fixture
def server() -> Iterator[ApiServer]:
    state = ApiServer(url="")
    httpd = _start(state, None)
    state.url = f"http://127.0.0.1:{httpd.server_address[1]}"
    yield state
    httpd.shutdown()
    httpd.server_close()


@pytest.fixture(scope="session")
def tls_ca() -> trustme.CA:
    return trustme.CA()


@pytest.fixture
def tls_server(tls_ca: trustme.CA) -> Iterator[ApiServer]:
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    tls_ca.issue_cert("127.0.0.1", "localhost").configure_cert(context)
    state = ApiServer(url="")
    httpd = _start(state, context)
    state.url = f"https://localhost:{httpd.server_address[1]}"
    yield state
    httpd.shutdown()
    httpd.server_close()


@pytest.fixture
def client(server: ApiServer) -> Client:
    return Client(API_TOKEN, API_SECRET, base_url=server.url)
