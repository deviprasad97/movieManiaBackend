# Import required libraries
from bs4 import BeautifulSoup, NavigableString


def extract_release_info(soup):
    # Find the target span tag
    target_span = soup.find(lambda tag: tag.name == "span" and tag.get("class") == ["subheading", "grey"])

    # Initialize variables
    studio, year, duration, rating, release_date = None, None, None, None, None

    # Iterate over siblings of the target span tag to extract information
    for sibling in target_span.next_siblings:
        if sibling.name == "span" and sibling.get("class") == ["subheading", "grey"]:
            break  # Stop at the next similar span tag

        if sibling.name == "a" and 'studioid' in sibling.get('href', ''):
            studio = sibling.text.strip()
        elif sibling.name == "a" and 'year' in sibling.get('href', ''):
            year = int(sibling.text.strip())
        elif sibling.name == "span" and sibling.get("id") == "runtime":
            duration = sibling.text.strip()
        elif sibling.name == "a" and 'releasedates' in sibling.get('href', ''):
            release_date = sibling.text.strip()

    # The rating is a bit tricky to extract directly; it's part of the sibling text
    if target_span:
        remaining_text = target_span.text
        rating_parts = [part.strip() for part in remaining_text.split('|') if "Rated" in part]
        rating = rating_parts[0] if rating_parts else None

    # Constructing the information dictionary
    movie_info = {
        "Studio": studio,
        "Year": year,
        "Duration": duration,
        "Rating": rating,
        "Release Date": release_date
    }
    return movie_info


# Function to safely extract text
def extract_text(soup, text):
    # Find the tag containing the text "Discs"
    discs_tag = soup.find(lambda tag: tag.name == "span" and tag.get("class") == ["subheading"] and text == tag.text)
    # Initialize a list to hold all the extracted lines
    info = []
    try:
        # Iterate over subsequent siblings until the next <span class="subheading"> tag
        for sibling in discs_tag.next_siblings:
            if sibling.name == "span" and "subheading" in sibling.get('class', []):
                break  # Stop at the next subheading
            if isinstance(sibling, NavigableString):
                info.append(sibling.strip())

        # Filter out empty strings
        info = [line for line in info if line]
    except Exception:
        return info

    return info