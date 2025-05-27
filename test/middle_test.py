# test/session_guard.py
import asyncio
import httpx
from dotenv import load_dotenv
import os

load_dotenv()  # 若 .env 內有自訂 BASE_URL、測試帳密，可自動帶入
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

# 測試帳號，請確定與資料庫 / fixture 相符
test_user = {
    "username": "testuser1",
    "usermail": "testuser1@mail.com",
    "password": "testpass1",
}

PROTECTED_PATH = "/api/user/test/mfa"
LOGIN_PATH = "/api/user/login"


async def test_session_guard():
    async with httpx.AsyncClient() as client:
        # -------- Case 1: 不帶 cookie --------
        no_cookie_resp = await client.get(f"{BASE_URL}{PROTECTED_PATH}")
        print("No-cookie response:", no_cookie_resp.status_code, no_cookie_resp.text)
        assert no_cookie_resp.status_code in (401, 403)

        # -------- Case 2: 帶錯誤 cookie --------
        bad_cookie_resp = await client.get(
            f"{BASE_URL}{PROTECTED_PATH}",
            cookies={"session_id": "this-is-not-a-valid-session"},
        )
        print("Bad-cookie response:", bad_cookie_resp.status_code, bad_cookie_resp.text)
        assert bad_cookie_resp.status_code in (401, 403)

        # -------- Case 3: 先登入取得合法 session，再呼叫 --------
        login_resp = await client.post(f"{BASE_URL}{LOGIN_PATH}", json=test_user)
        assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"

        session_id = login_resp.cookies.get("session_id")
        print("Session ID (from login):", session_id)
        assert session_id, "No session_id set after login"

        ok_resp = await client.get(
            f"{BASE_URL}{PROTECTED_PATH}",
            cookies={"session_id": session_id},
        )
        print("Valid-cookie response:", ok_resp.status_code, ok_resp.text)
        assert ok_resp.status_code == 200
        assert ok_resp.json().get("msg") == "you passed session guard"


if __name__ == "__main__":
    asyncio.run(test_session_guard())
