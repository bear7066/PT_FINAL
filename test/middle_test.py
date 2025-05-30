import asyncio
import httpx
from dotenv import load_dotenv
import os

load_dotenv()
# BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
BASE_URL = f"http://localhost:{os.getenv("PORT")}"

# 測試帳號
test_user = {
    "username": "testuser1",
    "usermail": "testuser1@mail.com",
    "password": "testpass1",
}

PROTECTED_PATH = "/api/user/mfa"
LOGIN_PATH = "/api/user/login"


async def test_session_guard():
    async with httpx.AsyncClient() as client:
        # -------- Case 1: 不帶 cookie --------
        print("\n--- Case 1: 沒帶 session_id cookie ---")
        no_cookie_resp = await client.get(f"{BASE_URL}{PROTECTED_PATH}")
        print("No-cookie response:", no_cookie_resp.status_code, no_cookie_resp.text)
        assert no_cookie_resp.status_code in (401, 403)

        # -------- Case 2: 帶錯誤 cookie --------
        print("\n--- Case 2: 帶錯的 session_id ---")
        bad_cookie_resp = await client.get(
            f"{BASE_URL}{PROTECTED_PATH}",
            cookies={"session_id": "this-is-not-a-valid-session"},
        )
        print("Bad-cookie response:", bad_cookie_resp.status_code, bad_cookie_resp.text)
        assert bad_cookie_resp.status_code in (401, 403)

        # -------- Case 3: 登入取得合法 session，但時間間隔太近會被擋 --------
        print("\n--- Case 3: 登入取得合法 session，但時間間隔太近會被擋 ---")
        login_resp = await client.post(f"{BASE_URL}{LOGIN_PATH}", json=test_user)
        assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"

        session_id = login_resp.cookies.get("session_id")
        print("Session ID (from login):", session_id)
        assert session_id, "No session_id set after login"

        error_resp = await client.get(
            f"{BASE_URL}{PROTECTED_PATH}",
            cookies={"session_id": session_id},
        )

        print("Valid-cookie response:", error_resp.status_code, error_resp.text)
        assert error_resp.status_code in [
            404,
            500,
        ], "Expected 404 or 500 for protected route access failure"

        # -------- Case 4: 登入取得合法 session，預期回傳 200 且內容正確 --------
        import asyncio

        await asyncio.sleep(2)
        print("\n--- Case 4: 使用正確 session_id ---")
        print("Session ID (from login):", session_id)
        assert session_id, "No session_id set after login"

        ok_resp = await client.get(
            f"{BASE_URL}{PROTECTED_PATH}",
            cookies={"session_id": session_id},
        )
        print("Valid-cookie response:", ok_resp.status_code, ok_resp.text)
        assert ok_resp.status_code == 200
        assert ok_resp.json().get("msg") == "you passed session guard"


async def test_high_risk_session():
    print("\n--- Case 4: 模擬高風險請求 ---")
    async with httpx.AsyncClient() as client:
        # 登入取得 session_id
        login_resp = await client.post(f"{BASE_URL}{LOGIN_PATH}", json=test_user)
        assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"

        session_id = login_resp.cookies.get("session_id")
        assert session_id, "No session_id set after login"
        print("Session ID (for risk test):", session_id)

        # 模擬風險行為：demo 的時候可改
        headers = {
            # 現在是模擬 UA + Fingerprint
            "User-Agent": "Totally-Different-UA/1.0",  # score +40
            "x-device-fp": "fake-fingerprint-123456",  # score +40
        }

        high_risk_resp = await client.get(
            f"{BASE_URL}{PROTECTED_PATH}",
            cookies={"session_id": session_id},
            headers=headers,
        )

        print("High-risk response:", high_risk_resp.status_code, high_risk_resp.text)
        assert high_risk_resp.status_code == 403
        assert "risk too high" in high_risk_resp.text


async def test_expired_session():
    print("\n--- Case 5: Session 過期 ---")
    async with httpx.AsyncClient() as client:
        # Step 1: 登入取得 session_id
        login_resp = await client.post(f"{BASE_URL}{LOGIN_PATH}", json=test_user)
        assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
        session_id = login_resp.cookies.get("session_id")
        assert session_id, "No session_id set after login"
        print("Session ID (for expire test):", session_id)

        # Step 2: 用 Redis 將 session 的 expire_time 修改為過去
        import redis.asyncio as redis

        r = redis.from_url("redis://localhost")  # 或你 .env 裡的 Redis 連線字串
        await r.hset(
            session_id, mapping={"expire_time": "1"}
        )  # 設為遠古時間（Unix timestamp 1 秒）

        # Step 3: 再次請求受保護資源
        expired_resp = await client.get(
            f"{BASE_URL}{PROTECTED_PATH}",
            cookies={"session_id": session_id},
        )

        print("Expired-session response:", expired_resp.status_code, expired_resp.text)
        assert expired_resp.status_code == 403
        assert "risk too high" in expired_resp.text


if __name__ == "__main__":
    asyncio.run(test_session_guard())
    # asyncio.run(test_high_risk_session())
