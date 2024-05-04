import re
import opencc
from typing import List


def traditional_to_simplified(traditional_text: str) -> str:
    """Convert traditional Chinese text to simplified Chinese text.

    Args:
        traditional_text: The traditional Chinese text to convert.

    Returns:
        The simplified Chinese text.
    """
    converter = opencc.OpenCC("t2s.json")
    simplified_text = converter.convert(traditional_text)
    return simplified_text


def is_tag_match_title(tags: List[str], title: str) -> bool:
    """Check if any of the tags match the title.
    Example:
        is_tag_match_title(["夜晚的水母不会游泳"], "[喵萌奶茶屋&LoliHouse] 夜晚的水母不会游泳 / Yoru no Kurage wa Oyogenai - 04 [WebRip 1080p HEVC-10bit AAC][简繁日内封字幕]") -> True
        is_tag_match_title(["夜晚的水母不会游泳"], "[ANi] Yoru no Kurage wa Oyogenai / 夜晚的水母不會游泳 - 04 [1080P][Baha][WEB-DL][AAC AVC][CHT][MP4]") -> True
        is_tag_match_title(["GIRLS", "BAND", "CRY"], "[北宇治字幕组] GIRLS BAND CRY [04][WebRip][HEVC_AAC][简体内嵌]") -> True

    Args:
      tags: A list of tags.
      title: The title to check.

    Returns:
      True if any of the tags match the title, False otherwise.
    """
    title = traditional_to_simplified(title).lower()
    tags = [traditional_to_simplified(tag.lower()) for tag in tags]

    return all(tag in title for tag in tags)


def generate_folder_name(tags: List[str]) -> str:
    """Generate a folder name from a list of tags.
    Example:
        generate_folder_name(["夜晚的水母不会游泳"]) -> "夜晚的水母不会游泳"
        generate_folder_name(["GIRLS", "BAND", "CRY"]) -> "GIRLS BAND CRY"

    Args:
        tags: A list of tags.

    Returns:
        A folder name generated from the tags.
    """
    folder_name = " ".join(tags)
    folder_name = (
        folder_name.replace("\\", " ")
        .replace("/", " ")
        .replace(":", " ")
        .replace("*", " ")
        .replace("?", " ")
        .replace('"', " ")
        .replace("<", " ")
        .replace(">", " ")
        .replace("|", " ")
    )
    folder_name = folder_name.strip()
    return folder_name


def extract_tags_from_title(title: str) -> List[str]:
    """Extract tags from a title, excluding episode numbers.

    Example:

        extract_tags_from_title("[喵萌奶茶屋&LoliHouse] 夜晚的水母不会游泳 / Yoru no Kurage wa Oyogenai - [WebRip 1080p HEVC-10bit AAC][简繁日内封字幕]") -> ['喵萌奶茶屋&LoliHouse', '夜晚的水母不会游泳', '/', 'Yoru', 'no', 'Kurage', 'wa', 'Oyogenai', 'WebRip', '1080p', 'HEVC-10bit', 'AAC', '简繁日内封字幕']

        extract_tags_from_title("【悠哈璃羽字幕社】葬送的芙莉莲/Sousou no Frieren][x264 1080p][CHS]" -> ['悠哈璃羽字幕社', '葬送的芙莉莲', 'Sousou', 'no', 'Frieren', 'x264', '1080p', 'CHS'])

    Args:
        title: The title to extract tags from.

    Returns:
        A list of tags extracted from the title.

    """
    # Remove episode numbers, assuming they are in the format " - 01 " or similar
    title = re.sub(r" - \d+ ", " ", title)

    # Split the title into tags using special characters as delimiters
    # The regex pattern "[\[\]\/\s]" matches any of the characters: [ ] / space
    tags = re.split(r"[\[\]\/\s]", title)

    # Remove empty strings from the list of tags
    tags = [tag for tag in tags if tag]

    return tags


if __name__ == "__main__":
    print(
        is_tag_match_title(
            ["夜晚的水母不会游泳"],
            "[ANi] Yoru no Kurage wa Oyogenai / 夜晚的水母不會游泳 - 04 [1080P][Baha][WEB-DL][AAC AVC][CHT][MP4]",
        )
    )
    print(
        is_tag_match_title(
            ["GIRLS", "BAND", "CRY", "[北宇治字幕组]", "简体内嵌"],
            "[北宇治字幕组] GIRLS BAND CRY [04][WebRip][HEVC_AAC][简体内嵌]",
        )
    )
