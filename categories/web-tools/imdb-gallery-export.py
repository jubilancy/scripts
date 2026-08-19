import os
import re
import sys
import time
import mimetypes

import requests
from slugify import slugify
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "Sec-GPC": "1",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
}

if __name__ == "__main__":

    #url = sys.argv[1]
    #url = "https://www.imdb.com/title/tt32572889/"
    url = "https://www.imdb.com/title/tt30144839/"

    r = requests.get(url, headers=headers)
    assert r.status_code == 200, f"bad http status: {r.status_code}"

    soup = BeautifulSoup(r.text, "html.parser")

    try:
        ep = soup.find(lambda tag: "season-episode-numbers-section" in tag.attrs.get("data-testid", ""))
        season, episode = ep.text.strip().split(".")
        season = season[1:]
        episode = episode[1:]
        show, title = re.search('"(.*)" ([^(]+)', soup.find("title").text).groups()
        show = slugify(show)
        title = title.strip()
    except:
        season = episode = show = None
        title = soup.find("title").text
        title = slugify(title)

    media_url = url + "mediaindex/"
    page_number = 1
    total_images_downloaded = 0

    while True:
        # Append the current page parameter to the media index url
        current_page_url = f"{media_url}?page={page_number}"
        print(f"Scraping page {page_number}: {current_page_url}")
        
        r = requests.get(current_page_url, headers=headers)
        assert r.status_code == 200, str(r.status_code)
        soup = BeautifulSoup(r.text, "html.parser")
        
        image_section = soup.find(lambda tag: tag.attrs.get("data-testid") == "sub-section-images")
        
        # If the targeted block or page context container isn't present, stop loop execution
        if not image_section:
            print("No image section container located. Exiting pagination loop.")
            break
            
        images = [tag.attrs["src"] for tag in image_section.find_all("img") if "src" in tag.attrs]
        images = [re.sub(r"V1_[^.]+.", "V1_.", i) for i in images]

        # Break out of loop if the parsed array contains zero images
        if not images:
            print(f"No further items found on page {page_number}. Scraping complete.")
            break

        for n, img in enumerate(images):
            total_images_downloaded += 1
            print(n + 1, len(images), show, season, episode, title, img)

            r = requests.get(img, headers=headers)

            try:
                extension = mimetypes.guess_extension(r.headers.get('Content-Type'))
            except Exception as e:
                extension = mimetypes.guess_extension(mimetypes.guess_type(img)[0])

            assert r.status_code == 200, f"bad http status: {r.status_code}"

            if show:
                imgfile = f"{show}-season-{season}-episode-{episode}-{total_images_downloaded}{extension}"
            else:
                imgfile = f"{title}-{total_images_downloaded}{extension}"

            if os.path.exists(imgfile): 
                continue
            open(imgfile, "wb").write(r.content)
            time.sleep(1)
            
        # Increment to advance parameters to the next data segment
        page_number += 1
        time.sleep(1)