import requests
import json

module_name = input()
r = requests.get(f"https://pypi.org/pypi/{module_name}/json")
data = r.json()
print(data)