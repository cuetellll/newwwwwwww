import os
import time

os.environ.setdefault("BOT_TOKEN", "123:TEST")
os.environ.setdefault("SECRET_KEY", "unit-test-secret-key-000000000000")
os.environ.setdefault("BASE_URL", "https://example.com")

import httpx  # noqa: E402
import pytest  # noqa: E402
from fastapi import FastAPI  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

import app.web as web  # noqa: E402
from app.telegram import TgFile  # noqa: E402
from app.tokens import FilePayload, make_token  # noqa: E402

PAYLOAD = b"x" * 2048


@pytest.fixture
def client(monkeypatch):
    async def fake_open_stream(file_id, range_header=None):
        if range_header and range_header.startswith("bytes="):
            s, _, e = range_header[6:].partition("-")
            start = int(s or 0)
            end = int(e) if e else len(PAYLOAD) - 1
            chunk = PAYLOAD[start : end + 1]
            resp = httpx.Response(
                206,
                content=chunk,
                headers={
                    "content-length": str(len(chunk)),
                    "content-range": f"bytes {start}-{end}/{len(PAYLOAD)}",
                },
            )
        else:
            resp = httpx.Response(
                200, content=PAYLOAD, headers={"content-length": str(len(PAYLOAD))}
            )
        return resp, None

    async def fake_get_file(fid, use_cache=True):
        return TgFile(file_id=fid, file_path="videos/f.mp4", file_size=len(PAYLOAD))

    monkeypatch.setattr(web, "open_stream", fake_open_stream)
    monkeypatch.setattr(web, "get_file", fake_get_file)

    application = FastAPI()
    application.include_router(web.router)
    return TestClient(application)


@pytest.fixture
def token():
    return make_token(
        FilePayload(fid="FID", name="ویدیو من.mp4", size=len(PAYLOAD), mime="video/mp4")
    )


def test_index_and_health(client):
    assert client.get("/").status_code == 200
    body = client.get("/health").json()
    assert body["ok"] is True


def test_full_download(client, token):
    r = client.get(f"/f/{token}/video.mp4")
    assert r.status_code == 200
    assert r.content == PAYLOAD
    assert r.headers["accept-ranges"] == "bytes"
    assert "filename*=UTF-8''" in r.headers["content-disposition"]


def test_range_request(client, token):
    r = client.get(f"/f/{token}", headers={"Range": "bytes=0-99"})
    assert r.status_code == 206
    assert len(r.content) == 100
    assert r.headers["Content-Range"] == f"bytes 0-99/{len(PAYLOAD)}"


def test_head_request(client, token):
    r = client.head(f"/f/{token}")
    assert r.status_code == 200
    assert r.headers["content-length"] == str(len(PAYLOAD))


def test_inline_disposition(client, token):
    r = client.get(f"/f/{token}?inline=1")
    assert r.headers["content-disposition"].startswith("inline")


def test_download_page(client, token):
    r = client.get(f"/p/{token}")
    assert r.status_code == 200
    assert "ویدیو من.mp4" in r.text
    assert "<video" in r.text


def test_invalid_and_expired_tokens(client):
    assert client.get("/f/not-a-token/x.mp4").status_code == 404
    expired = make_token(FilePayload(fid="A", exp=int(time.time()) - 60))
    assert client.get(f"/f/{expired}").status_code == 410


def test_unknown_slug(client):
    assert client.get("/d/doesnotexist").status_code == 404
