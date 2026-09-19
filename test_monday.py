import os
import requests
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("MONDAY_API_TOKEN")

if not token:
    print("❌ MONDAY_API_TOKEN not found")
    exit()

query = """
query {
    me {
        id
        name
        email
    }
}
"""

headers = {
    "Authorization": token,
    "Content-Type": "application/json"
}

response = requests.post(
    "https://api.monday.com/v2",
    json={"query": query},
    headers=headers
)

print("Status:", response.status_code)
print("Response:", response.json())