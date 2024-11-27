import requests
from bs4 import BeautifulSoup


st_accept = "text/html"
st_useragent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_3_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.4 Safari/605.1.15"
headers = {
    "Accept": st_accept,
    "User-Agent": st_useragent
}


def site_parser(url):
    try:
        req = requests.get(url, headers)
        req.raise_for_status()
        src = req.content

        soup = BeautifulSoup(src, "html.parser")

        text_divs = soup.find_all(
            'div', class_='notion-page-content')
        extracted_text = ""
        for div in text_divs:
            extracted_text += div.get_text(strip=True, separator="\n")

        print(extracted_text)

        title = soup.title.string
        print(title)

    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
