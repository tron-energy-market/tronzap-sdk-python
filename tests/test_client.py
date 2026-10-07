import hashlib
import json
from concurrent.futures import ThreadPoolExecutor
from typing import Tuple

from conftest import API_SECRET, ApiServer, ReceivedRequest

import tronzap_sdk
from tronzap_sdk import Client


def test_version() -> None:
    assert tronzap_sdk.__version__.count(".") == 2


def test_concurrent_calls_share_one_client(client: Client, server: ApiServer) -> None:
    def echo(request: ReceivedRequest) -> Tuple[int, str]:
        signature_ok = (
            request.headers["x-signature"]
            == hashlib.sha256(request.body + API_SECRET.encode()).hexdigest()
        )
        result = {"echo": request.json.get("id"), "signature_ok": signature_ok}
        return 200, json.dumps({"code": 0, "result": result})

    server.responder = echo
    ids = [f"tx-{i}" for i in range(64)]

    with ThreadPoolExecutor(max_workers=16) as pool:
        results = list(pool.map(lambda tx_id: client.check_transaction(id=tx_id), ids))

    assert [r["echo"] for r in results] == ids
    assert all(r["signature_ok"] for r in results)
    assert len(server.requests) == len(ids)
