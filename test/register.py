import asyncio
import httpx
from dotenv import load_dotenv
import os

load_dotenv()

# BASE_URL = f"http://localhost:8000"
BASE_URL = f"http://localhost:{os.getenv("PORT")}"

test_user = {
    "username": "testuser1",
    "usermail": "testuser1@mail.com",
    "password": "testpass1"
}

async def test_register():
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/api/user/register", json=test_user)
        print("Register Response:", response.status_code, response.json())


if __name__ == "__main__":
    asyncio.run(test_register())
