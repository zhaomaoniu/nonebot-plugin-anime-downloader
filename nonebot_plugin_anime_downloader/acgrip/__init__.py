import re
import aiohttp
import asyncio
import urllib.parse
from typing import List, Dict


headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "Cache-Control": "max-age=0",
    "Sec-Ch-Ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Microsoft Edge";v="122"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0",
}


async def make_request(arg: str = "", base_url: str = "https://acgrip.art") -> str:
    url = f"{base_url}/{arg}"
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url) as response:
            response_text = await response.text()
            return response_text


async def fetch_torrent_data(url: str) -> bytes:
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url) as response:
            torrent_data = await response.read()
            return torrent_data


def extract_data(html_content: str) -> List[Dict[str, str]]:
    """Extracts title, URL, ID, and size from ACG.RIP HTML content.

    Args:
      html_content: The HTML content as a string.

    Returns:
      A list of dictionaries, where each dictionary contains information
      about a torrent entry:
      {
        "title": "[桜都字幕组] ... [简繁内封]",
        "url": "/t/302390",
        "id": "302390",
        "size": "99.8 MB"
      }
    """

    # Regular expression to match torrent entries
    pattern = r'<tr>.*?<a href="(https://[^\s]*/t/\d+|/t/\d+)".*?>(.*?)</a>.*?<td class="action"><a href=".*?\.torrent".*?>.*?</td>.*?<td class="size">(.*?)</td>.*?</tr>'

    # Find all matches in the HTML content
    matches = re.findall(pattern, html_content, re.DOTALL)

    # Extract data and create a list of dictionaries
    data = []
    for match in matches:
        url, title, size = match
        id_ = url.split("/")[-1]  # Extract ID from URL
        data.append(
            {"title": title.strip(), "url": url, "id": id_, "size": size.strip()}
        )

    return data


def replace_html_entities(text: str) -> str:
    """Replaces HTML entities in the given text.

    Args:
      text: The text to process.

    Returns:
      The text with HTML entities replaced.
    """
    # Define a dictionary of HTML entities and their replacements
    html_entities = {
        "&amp;": "&",
        "&lt;": "<",
        "&gt;": ">",
        "&quot;": '"',
        "&apos;": "'",
        "&#39;": "'",
        "&#34;": '"',
        "&#60;": "<",
        "&#62;": ">",
    }

    # Replace HTML entities in the text
    for entity, replacement in html_entities.items():
        text = text.replace(entity, replacement)

    return text


def url_encode(text: str) -> str:
    """Encode the given text as a URL.

    Args:
        text: The text to encode.

    Returns:
        The URL-encoded text.
    """
    encoded_text = urllib.parse.quote(text)
    return encoded_text


def convert_tags_to_query(tags: List[str]) -> str:
    """Converts a list of tags to a query string.

    Args:
      tags: A list of tags.

    Returns:
      A query string with tags separated by '+'.
    """
    for tag in tags:
        tag.replace(" ", "+")

    query = "+".join(tags)
    return query


def get_anime_data(tags: List[str]) -> List[Dict[str, str]]:
    """Fetches anime data from ACG.RIP.

    Args:
      tags: A list of tags to search for.

    Returns:
      A list of dictionaries, where each dictionary contains information
      about a torrent entry:
      {
        "title": "[桜都字幕组] ... [简繁内封]",
        "url": "/t/302390",
        "id": "302390",
        "size": "99.8 MB"
      }
    """
    query = convert_tags_to_query(tags)
    html = make_request(f"?term={query}")
    html = replace_html_entities(html)
    data = extract_data(html)
    return data


async def main() -> None:
    tag = ["北宇治字幕组", "GIRLS BAND CRY", "简体内嵌"]
    html = await make_request(f"?term={convert_tags_to_query(tag)}")

    html = replace_html_entities(html)
    data = extract_data(html)
    print(data)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())


__all__ = ["get_anime_data", "fetch_torrent_data"]
