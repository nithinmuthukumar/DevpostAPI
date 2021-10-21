import requests
from bs4 import BeautifulSoup
import urllib.parse


# api.devpost.com/software
# ?page=
# https://devpost.com/api/hackathons?challenge_type[]=in-person
class DevpostScraper:
    parser = "html.parser"
    baseurl = "https://devpost.com/"
    param_indicators = ["?", "&"]

    def __init__(self):
        pass

    def get_hackathons(self, *, amount, order_by=None, location=None, status=None,
                       length=None, themes=None, organization=None, open_to=None, search=None):
        page = 1
        url = "https://devpost.com/api/hackathons"
        params = [("order_by", order_by), ("challenge_type[]", location), ("status[]", status), ("length[]", length),
                  ("themes[]", themes), ("organization", organization), ("open_to[]", open_to), ("search", search)]
        params = {k: v for k, v in params if v}
        hackathons = []
        url_parts = list(urllib.parse.urlparse(url))
        query = dict(urllib.parse.parse_qsl(url_parts[4]))
        query.update(params)
        url_parts[4] = urllib.parse.urlencode(query)
        req_url = urllib.parse.urlunparse(url_parts)
        paging_data = requests.get(req_url).json()["meta"]
        amount = min(amount, paging_data["total_count"])

        while amount > 0:
            data = requests.get(req_url + self.param_indicators[len(params)] + f"{page=}").json()["hackathons"]

            print(req_url + f"&{page=}")
            if amount >= len(data):
                amount -= len(data)
                hackathons.extend(data)
            else:
                hackathons.extend(data[:amount])
                amount = 0

            page += 1
        return hackathons

    def get_hackathon_projects(self, hackathon_url):
        pass

    def get_projects(self, *, amount):
        # print([img['src'] for img in soup.findAll(True, {'class': ['software_thumbnail_image']})])
        page = 1
        projects = []
        url = "https://api.devpost.com/software"
        while amount > 0:
            data = requests.get(url + self.param_indicators[0] + f"{page=}").json()["software"]
            if amount >= len(data):
                amount -= len(data)
                projects.extend(data)
            else:
                projects.extend(data[:amount])
                amount = 0

            page += 1
        return projects


if __name__ == "__main__":
    dps = DevpostScraper()
    print([i["title"] for i in dps.get_hackathons(amount=2, search="MasseyHacks VII")])
    print([i["name"] for i in dps.get_projects(amount=4)])
