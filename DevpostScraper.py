import re

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

    def add_queries_to_url(self, url, params):
        url_parts = list(urllib.parse.urlparse(url))
        query = dict(urllib.parse.parse_qsl(url_parts[4]))
        query.update(params)
        url_parts[4] = urllib.parse.urlencode(query)
        req_url = urllib.parse.urlunparse(url_parts)
        return req_url

    def get_hackathons(self, *, amount, order_by=None, location=None, status=None,
                       length=None, themes=None, organization=None, open_to=None, search=None):
        page = 1
        url = "https://devpost.com/api/hackathons"
        params = [("order_by", order_by), ("challenge_type[]", location), ("status[]", status), ("length[]", length),
                  ("themes[]", themes), ("organization", organization), ("open_to[]", open_to), ("search", search)]
        params = {k: v for k, v in params if v}
        hackathons = []
        req_url = self.add_queries_to_url(url, params)

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

    def get_hackathon_projects(self, hackathon_url, category=None):
        projects_url = hackathon_url + "submissions/search"
        params = {}
        if category:
            category_info = next(i for i in self.get_hackathon_categories(hackathon_url) if i['name'] == category)
            params = {"prize_filter[prizes][]": category_info['id']}
            projects_url = self.add_queries_to_url(projects_url, params)

        # large-4 small-12 columns gallery-item
        # print([img['src'] for img in soup.findAll(True, {'class': ['software_thumbnail_image']})])

        projects = []

        while True:
            print(projects_url)
            page = requests.get(projects_url)
            soup = BeautifulSoup(page.content, self.parser)
            project_divs = soup.findAll("div", {'data-software-id': re.compile(r".*")})
            for project in project_divs:
                image = project.find("img", {"class": "software_thumbnail_image"}, src=True, alt=True)
                project = {
                    "url": project.find("a", {"class": 'link-to-software'}, href=True)['href'],
                    "imageUrl": image['src'],
                    'name': image['alt'],
                    'tagLine': project.find('p', {"class": "tagline"}).get_text().strip(),
                    'likes': int(project.find('span', {"data-count": "like"}).get_text().strip()),
                    'commentCount': int(project.find('span', {"data-count": "comment"}).get_text().strip()),
                    'members': [{"name": s["alt"], "username": s["title"], "imageUrl": s["src"]}
                                for s in
                                project.find_all("img", {"class": "user-photo"}, alt=True, src=True, title=True)],
                    'isWinner': bool(project.find("aside",{"class":"entry-badge"}))

                }
                projects.append(project)
            next_button = soup.find("li", {"class": "next_page"})

            if not next_button or "unavailable" in next_button['class']:
                break
            else:
                projects_url = hackathon_url + next_button.find('a')['href']
                if category:
                    projects_url = self.add_queries_to_url(projects_url, params)
        return projects

    def get_hackathon_categories(self, hackathon_url):
        projects_url = hackathon_url + "submissions/search"
        page = requests.get(projects_url)
        soup = BeautifulSoup(page.content, self.parser)

        submission_filters = soup.findAll("label", {"class": "checkbox"})
        return [{"name": filter.get_text(),
                 "id": int(filter.find("input", {"name": "prize_filter[prizes][]"})["value"])} for
                filter in submission_filters]

    def get_projects(self, *, amount):

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
    # print([i["title"] for i in dps.get_hackathons(amount=2, search="MasseyHacks VII")])
    # print([i["name"] for i in dps.get_projects(amount=4)])
    # print(dps.get_hackathon_projects("https://hack-the-valley-v.devpost.com/"))
    print(dps.get_hackathon_projects("https://hack-the-valley-v.devpost.com/", "Best Use of Assembly AI's API"))
