import asyncio
import httpx
from dotenv import load_dotenv
import os

load_dotenv()

BASE_URL = f"http://localhost:8000"
test_user = {
    "username": "testuser1",
    "usermail": "testuser1@mail.com",
    "password": "testpass1"
}

async def test_login():
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/api/user/login", json=test_user)
        print("Login Response:", response.status_code, response.json())

        cookies = response.cookies
        session_id = cookies.get("session_id")
        print("Session ID:", session_id)

        # profile_resp = await client.get(f"{BASE_URL}/api/profile", cookies={"session_id": session_id})
        # print("Profile response:", profile_resp.status_code, profile_resp.json())


if __name__ == "__main__":
    asyncio.run(test_login())
