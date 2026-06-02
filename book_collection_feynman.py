import os
import requests
from bs4 import BeautifulSoup

urls = [
    "https://en.wikipedia.org/wiki/Richard_Feynman",
    "https://fs.blog/richard-feynman-learning-thinking/",

    "https://en.wikipedia.org/wiki/Surely_You're_Joking,_Mr._Feynman!",
    "https://en.wikipedia.org/wiki/What_Do_You_Care_What_Other_People_Think%3F",

    "https://en.wikipedia.org/wiki/The_Feynman_Lectures_on_Physics",
    "https://www.feynmanlectures.caltech.edu/",

    "https://en.wikipedia.org/wiki/Six_Easy_Pieces",
    "https://en.wikipedia.org/wiki/Six_Not-So-Easy_Pieces",

    "https://en.wikipedia.org/wiki/The_Pleasure_of_Finding_Things_Out",
    "https://en.wikipedia.org/wiki/The_Meaning_of_It_All_(book)",

    "https://en.wikipedia.org/wiki/QED:_The_Strange_Theory_of_Light_and_Matter",

    "https://en.wikipedia.org/wiki/Richard_Feynman#Books_and_lectures",
    "https://en.wikipedia.org/wiki/Feynman_diagram",

    "https://www.feynmanlectures.caltech.edu/III_toc.html",
    "https://www.feynmanlectures.caltech.edu/II_toc.html",
    "https://www.feynmanlectures.caltech.edu/I_toc.html",

    "https://en.wikipedia.org/wiki/Path_integral_formulation",
    "https://en.wikipedia.org/wiki/Quantum_electrodynamics",

    "https://en.wikipedia.org/wiki/Lectures_on_Physics",
    "https://en.wikipedia.org/wiki/Cornell_Lectures",

    "https://en.wikipedia.org/wiki/Feynman_method",
    "https://en.wikipedia.org/wiki/Scientific_method",

    "https://fs.blog/feynman-technique/",
    "https://www.feynmanlectures.caltech.edu/info/",
]

output_dir = "feynman_data/books"
os.makedirs(output_dir, exist_ok=True)

def extract_text(url):
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(r.text, "html.parser")

    paragraphs = soup.find_all("p")
    text = "\n".join([p.get_text() for p in paragraphs])

    return text

all_texts = []

for i, url in enumerate(urls):
    try:
        print("Processing:", url)
        text = extract_text(url)

        all_texts.append(text)

    except Exception as e:
        print("Failed:", url, e)

with open(f"{output_dir}/all_books.txt", "w", encoding="utf-8") as f:
    f.write("\n\n".join(all_texts))

print("Books saved.")