import requests

response = requests.get("http://localhost:5009/nav_feedback/list?page=1")
print(response.json())