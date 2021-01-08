import datetime
import heapq
import requests

from ayumi import Ayumi
from difflib import SequenceMatcher

ANILIST_API_URL = "https://graphql.anilist.co"

QUERY = '''
query ($page: Int, $seasonYear: Int, $status: MediaStatus, $startDate: FuzzyDateInt, $endDate: FuzzyDateInt) {
    Page (page: $page) {
        pageInfo {
            hasNextPage
        }

        media(status: $status, type: ANIME, seasonYear: $seasonYear, startDate_lesser: $startDate, endDate_greater: $endDate) {
            title {
                userPreferred
                native
                english
                romaji
            }
        }
    }
}
'''


def _similarity(title1, title2):
    return SequenceMatcher(None, title1, title2).ratio()


def _get_shows(status: str, **kwargs):
    """
    Fetch all the airing, recently finished, and soon to be airing shows
    Run string siimlarity and return the string most likely to be the same show.
    """

    shows = list()
    page = 1
    has_next_page = True

    while has_next_page:

        Ayumi.info("Now requesting shows from page {} of status {}...".format(page, status), color=Ayumi.CYAN)

        variables = {
            'page': page,
            'status': status
        }

        k_year = kwargs.get('year')
        if k_year:
            Ayumi.debug("Set seasonYear argument to {}".format(k_year), color=Ayumi.CYAN)
            variables['seasonYear'] = int(k_year)

        k_sd = kwargs.get('start_date')
        if k_sd:
            Ayumi.debug("Set startDate_lesser argument to {}".format(k_sd), color=Ayumi.CYAN)
            variables['startDate'] = int(k_sd)
        
        k_ed = kwargs.get('end_date')
        if k_ed:
            Ayumi.debug("Set endDate_greater argument to {}".format(k_ed), color=Ayumi.CYAN)
            variables['endDate'] = int(k_ed)

        try:
            ani_res = requests.post(
                ANILIST_API_URL,
                json={
                    'query': QUERY,
                    'variables': variables
                })
        except requests.exceptions.ConnectionError:
            Ayumi.warning("Unable to contact Anilist, the site or your connection may be down.", color=Ayumi.LRED)
            return shows

        if ani_res.status_code != 200:
            Ayumi.warning("Anilist returned unaccepted HTTP code {} upon request.".format(ani_res.status_code), color=Ayumi.LRED)
            return shows

        try:
            ani_json = ani_res.json()['data']['Page']
            has_next_page = ani_json['pageInfo']['hasNextPage']
            page += 1

            for media in ani_json['media']:
                for media_title in media['title'].values():
                    if media_title:
                        Ayumi.debug("Adding show {} to show list".format(media_title))
                        shows.append(media_title)

        except:
            Ayumi.warning("Unable to parse JSON response from Anilist.", color=Ayumi.LRED)
            return shows

    return shows


def find_closest_title(title):
    """
    Finds the closest title from Anilist for Airing and Not_Yet_Released shows
    """
    now = datetime.datetime.now()
    date_next_month = int((now + datetime.timedelta(weeks=4)).strftime("%Y%m%d"))
    date_last_month = int((now - datetime.timedelta(weeks=4)).strftime("%Y%m%d"))
    shows = list()
    heap = list()

    shows.extend(_get_shows("RELEASING"))
    shows.extend(_get_shows("NOT_YET_RELEASED", start_date=date_next_month))
    shows.extend(_get_shows("FINISHED", end_date=date_last_month))

    for show in shows:
        ratio = _similarity(title, show)
        Ayumi.debug('Matched "{}" against "{}" for a ratio of {}'.format(title, show, ratio))
        heapq.heappush(heap, (ratio, show))

    top_5 = heapq.nlargest(5, heap)
    Ayumi.info("Displaying (up to) top 5 matches of {} results:".format(len(heap)), color=Ayumi.LBLUE)
    for top in top_5:
        Ayumi.info("{}: {}".format(top[1], top[0]), color=Ayumi.LBLUE)

    if top_5:
        Ayumi.info('Returning top match: {}'.format(top_5[0][1]), color=Ayumi.LGREEN)
        return top_5[0][1]
    else:
        Ayumi.warning("No shows were fetched by Naomi, returning None", color=Ayumi.LYELLOW)
        return None
