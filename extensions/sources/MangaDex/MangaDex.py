import logging
import re
from pathlib import Path
import requests

from FMD3.sources import add_source
from FMD3.sources.SearchResult import SearchResult
from FMD3.sources.ISource import ISource
from FMD3.models.chapter import Chapter
from FMD3.models.series_info import SeriesInfo

from  .utils import get_demographic, get_rating, check_empty_chapters, check_group_id
from .Settings import Keys, controls

MANGAINFO = {}
_API_URL = 'https://api.mangadex.org'  # -- This is the url to the JSON API. Call this url to look at the API documentation.
_API_PARAMS = '?includes[]=author&includes[]=artist&includes[]=cover_art'
_COVER_URL = 'https://uploads.mangadex.org/covers'
_GUID_PATTERN = re.compile(r'.{8}-.{4}-.{4}-.{4}-.{12}')
# _MAPPING_FILE = 'userdata/mangadex_v5_mapping.txt'
_MAPPING_FILE = 'mangadex_v5_mapping.txt'

"""Dictionary with keypair values that maps v3 ids to v5"""
api_mapping = {}


def parse_manga_uuid(url):
    mid = re.search(_GUID_PATTERN, url)
    manga_id = None
    # Extract manga ID from URL
    # If no GUID (v5) was found, check if old ID (v3) is present
    if mid is None:
        # Old id
        # Extract manga ID from URL (v3)
        mid = re.search(r'\d{4}/(\d+)', url).group(1)
        # Check if GUID is mapped locally
        if mid:
            # Look up GUID for the extracted manga ID
            if mid in api_mapping:
                manga_id = api_mapping[mid]
                print('MangaDex: Legacy ID Mapping found in local text file:', mid)
            else:
                # Retrieve GUID from legacy API endpoint
                resp = requests.post(_API_URL + '/legacy/mapping', json={'type': 'manga', 'ids': [mid]},timeout=20)
                if resp.status_code == 200 and resp.json()['success']:
                    newid = resp.json()['data'][0]['id']
                    print('MangaDex: Legacy ID Mapping retrieved from API:', newid)
                    manga_id = newid
    else:
        manga_id = mid.group()
    return manga_id


class MangaDex(ISource):
    ID = 'd07c9c2425764da8ba056505f57cf40c'
    NAME = 'MangaDex'
    ROOT_URL = 'https://mangadex.org'
    CATEGORY = 'English'
    MaxTaskLimit = 1

    def init_settings(self):
        self.settings = controls
        if Path(_MAPPING_FILE).exists():
            with open(_MAPPING_FILE, 'r',encoding="UTF-8") as mapping_file:
                for line in mapping_file:
                    old, new = line.split(";")
                    api_mapping[old] = new

    def get_new_chapters(self, series_id, last_chapter: int):
        manga_id = parse_manga_uuid(series_id)
        return super().get_new_chapters(manga_id, last_chapter)

    def get_chapters(self, series_id) -> list[Chapter]:
        limitparam = 50
        langparam = f"translatedLanguage[]={self.get_setting(Keys.SelectedLanguage)}" if self.get_setting(
            Keys.SelectedLanguage) else []
        offset = 0
        # Handle chapters
        q = "&contentRating[]=safe&contentRating[]=suggestive&contentRating[]=erotica&contentRating[]=pornographic&includes[]=scanlation_group&order[volume]=asc&order[chapter]=asc"
        chapters = []
        iterations = 0
        while True:
            r = requests.get(
                _API_URL + "/manga/" + series_id + f"/feed?limit={limitparam}&offset={offset}&{langparam}{q}")
            iterations += 1
            offset = limitparam * iterations

            if r.status_code != 200:
                return []
            data = r.json()
            total = data["total"]
            if not data["data"]:
                logging.getLogger(__name__).error("Request did not provide data.",
                                                  extra={"request": r, "request": r.request, "data": r.json()})
                return []

            for chapter in data["data"]:
                if check_empty_chapters(chapter["attributes"]) and check_group_id(
                        filter(lambda x: x["type"] == "scanlation_group", chapter["relationships"])):
                    if chapter["attributes"]["chapter"] is None:
                        logging.getLogger(__name__).warning(
                            f"Skipping chapter '{chapter['id']}' - Mid: '{series_id}' - Number field is None")
                        continue
                    try:
                        ch = Chapter(chapter_id=chapter["id"],
                                     volume=chapter["attributes"]["volume"],
                                     number=float(chapter["attributes"]["chapter"]),
                                     title=chapter["attributes"]["title"],
                                     pages=chapter["attributes"]["pages"],
                                     scanlator=None
                                     # scanlator=list(filter(lambda x: x["type"] == "scanlation_group", chapter["relationships"]))[0][
                                     #     "attributes"]["name"]
                                     )
                        chapters.append(ch)
                    except:
                        logging.getLogger(__name__).exception("Error parsing chapter")

            if total < 50:
                break
            if iterations * limitparam >= total:
                break
        return chapters

    """SeriesMethods"""


    @staticmethod
    def get_info(url) -> SeriesInfo | None:
        manga_id = parse_manga_uuid(url)

        r = requests.get(_API_URL + "/manga/" + manga_id + _API_PARAMS)
        if r.status_code != 200:
            return
        print("asdsa")
        data = r.json()["data"]

        attributes = data["attributes"]
        mi = SeriesInfo()
        mi.id = manga_id
        mi.title = attributes["title"]["en"]
        mi.alt_titles = []
        for item in attributes["altTitles"]:
            for key in item:
                mi.alt_titles.append(item[key])
        mi.description = attributes["description"]["en"]
        mi.authors = list(author_data["attributes"]["name"] for author_data in
                          filter(lambda x: x["type"] == "author", data["relationships"]))
        mi.artists = list(artist_data["attributes"]["name"] for artist_data in
                          filter(lambda x: x["type"] == "artists", data["relationships"]))
        # MangaInfo.cover_art = list(filter(lambda x: x["type"] == "cover_art", data["relationships"]))
        covers = list(filter(lambda x: x["type"] == "cover_art", data["relationships"]))
        if covers:
            mi.cover_url = _COVER_URL + "/" + manga_id + "/" + covers[0]["attributes"]["fileName"]

        mi.genres = [tag["attributes"]["name"]["en"] for tag in
                     attributes["tags"] if
                     tag["attributes"]["name"]["en"] is not None]  # Improvement: option to get locale tags?

        if get_demographic(demographic := attributes["publicationDemographic"]):
            mi.genres.append(demographic)
        mi.demographic = demographic

        if get_rating(rating := attributes["publicationDemographic"]):
            mi.rating = rating
            mi.genres.append(rating)

        if attributes["status"] in ("ongoing", "hiatus"):
            mi.status = "ongoing"
        else:
            mi.status = "completed"
        return mi

    """Pages Methods"""

    def get_page_urls_for_chapter(self, chapter_id) -> list[str]:
        """
        Provides a list of URLs for all pages in a chapter.
        :param chapter_id:
        :return:
        """

        pages = []
        r = requests.get(f'{_API_URL}/at-home/server/{chapter_id}?'.strip())
        if r.status_code != 200:
            return []

        data = r.json()
        url = data["baseUrl"].strip("/")
        hash = data["chapter"]["hash"]
        mode = "dataSaver" if self.get_setting(Keys.DATA_SAVER) else "data"
        links = []
        for image in data["chapter"]["data"]:
            links.append(f"{url}/{mode}/{hash}/{image}")
        # TODO: handle errors
        return links

    def find_series(self, search_title) -> list[SearchResult]:
        query = f"https://api.mangadex.org/manga?limit=10&title={search_title}&includedTagsMode=AND&excludedTagsMode=OR&contentRating%5B%5D=safe&contentRating%5B%5D=suggestive&contentRating%5B%5D=erotica&order%5BlatestUploadedChapter%5D=desc&includes%5B%5D=manga&includes%5B%5D=cover_art"
        response = self.session.get(query)
        if response.status_code == 200:
            data = response.json()["data"]
            return [SearchResult(
                series_id=result["id"],
                title=result["attributes"]["title"]["en"],
                loc_title="",
                year=result["attributes"]["year"],
                cover_url="https://uploads.mangadex.org/covers/" + result["id"] + "/" +
                          list(filter(lambda x: x["type"] == "cover_art", result["relationships"]))[0]["attributes"][
                              "fileName"]
            )
                for result in data]

        return []


def load_source():
    add_source(MangaDex())
