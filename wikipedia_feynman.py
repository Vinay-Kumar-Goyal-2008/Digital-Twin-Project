import requests
import os
from bs4 import BeautifulSoup

title = "Richard_Feynman"

url = "https://en.wikipedia.org/w/api.php"

params = {
    "action": "parse",
    "page": title,
    "format": "json",
    "prop": "text",
    "redirects": 1
}

response = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"})
data = response.json()

html_content = data["parse"]["text"]["*"]

soup = BeautifulSoup(html_content, "html.parser")
text = soup.get_text(separator="\n")

os.makedirs("feynman_data/wiki", exist_ok=True)

with open("feynman_data/wiki/feynman_full.txt", "w", encoding="utf-8") as f:
    f.write(text)

print("Clean Wikipedia text saved successfully")