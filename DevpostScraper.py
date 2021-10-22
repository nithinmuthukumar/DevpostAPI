import re

import requests
from bs4 import BeautifulSoup
import urllib.parse

# api.devpost.com/software
# ?page=
# https://devpost.com/api/hackathons?challenge_type[]=in-person
parser = "html.parser"
baseurl = "https://devpost.com/"
param_indicators = ["?", "&"]


def add_queries_to_url(url, params):
    url_parts = list(urllib.parse.urlparse(url))
    query = dict(urllib.parse.parse_qsl(url_parts[4]))
    query.update(params)
    url_parts[4] = urllib.parse.urlencode(query)
    req_url = urllib.parse.urlunparse(url_parts)
    return req_url


def get_project_info(project_url):
    page = requests.get(project_url)
    soup = BeautifulSoup(page.content, parser)
    hackathon_soup = soup.find("div", {"id": 'submissions'}).find('ul', {"class": "software-list-with-thumbnail"})
    hackathons = []
    for h in hackathon_soup.findChildren('li', recursive=False):
        hackathon = dict()
        hackathon['name'] = h.find('p').get_text().strip()
        hackathon['imgUrl'] = "https:" + h.find('img', src=True)['src']
        hackathon['hackathonUrl'] = h.find('p').find('a')['href']
        hackathon['awards'] = []
        if h.find('ul'):
            hackathon['awards'] = ["".join(i.findAll(text=True, recursive=False)).strip() for i in h.findAll('li')]
        hackathons.append(hackathon)

    project = {
        'videoLink': soup.find('div', {'id': 'gallery'}).find('iframe')['src'],
        'hackathons': hackathons,
        'members': ''

    }
    return project


def get_hackathons(*, amount, options={},):
    page = 1
    url = "https://devpost.com/api/hackathons"
    params = {"order_by": 'order_by', 'location': "challenge_type[]", 'status': 'status[]', "length": 'length[]',
              "themes": 'themes[]', "organization": 'organization', "open_to": 'open_to[]', "search": 'search'}
    params = {params[k]: v for k, v in options.items()}
    hackathons = []
    req_url = add_queries_to_url(url, params)

    paging_data = requests.get(req_url).json()["meta"]
    amount = min(amount, paging_data["total_count"])

    while amount > 0:
        data = requests.get(req_url + param_indicators[len(params)] + f"{page=}").json()["hackathons"]

        print(req_url + f"&{page=}")
        if amount >= len(data):
            amount -= len(data)
            hackathons.extend(data)
        else:
            hackathons.extend(data[:amount])
            amount = 0

        page += 1
    return hackathons


def get_profile_projects(profile_url):
    page = requests.get(profile_url)
    soup = BeautifulSoup(page.content, parser)
    return get_projects_from_page(soup)


def get_projects_from_page(soup):
    projects = []

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
            'isWinner': bool(project.find("aside", {"class": "entry-badge"}))

        }
        projects.append(project)
    return projects


def get_hackathon_projects(hackathon_url, category=None, sort_by=None):
    if not sort_by and not category:
        projects_url = hackathon_url + "project-gallery"
    else:
        projects_url = hackathon_url + "submissions/search"
    params = {}
    if sort_by:
        params['sort'] = sort_by
    if category:
        category_info = next(i for i in get_hackathon_categories(hackathon_url) if i['name'] == category)
        params = {"prize_filter[prizes][]": category_info['id']}
        if sort_by:
            params['sort'] = sort_by
        projects_url = add_queries_to_url(projects_url, params)

    # large-4 small-12 columns gallery-item
    # print([img['src'] for img in soup.findAll(True, {'class': ['software_thumbnail_image']})])

    projects = []

    while True:
        page = requests.get(projects_url)
        soup = BeautifulSoup(page.content, parser)
        projects.extend(get_projects_from_page(soup))

        next_button = soup.find("li", {"class": "next_page"})

        if not next_button or "unavailable" in next_button['class']:
            break
        else:
            projects_url = hackathon_url + next_button.find('a')['href']
            if category or sort_by:
                projects_url = add_queries_to_url(projects_url, params)

    return projects


def get_hackathon_categories(hackathon_url):
    projects_url = hackathon_url + "submissions/search"
    page = requests.get(projects_url)
    soup = BeautifulSoup(page.content, parser)

    submission_filters = soup.findAll("label", {"class": "checkbox"})
    return [{"name": f.get_text(),
             "id": int(f.find("input", {"name": "prize_filter[prizes][]"})["value"])} for
            f in submission_filters]


def get_projects(*, amount):
    page = 1
    projects = []
    url = "https://api.devpost.com/software"
    while amount > 0:
        data = requests.get(url + param_indicators[0] + f"{page=}").json()["software"]
        if amount >= len(data):
            amount -= len(data)
            projects.extend(data)
        else:
            projects.extend(data[:amount])
            amount = 0

        page += 1
    return projects


if __name__ == "__main__":
    print([i['title'] for i in get_hackathons(amount=50, options={'search':"MasseyHacks"})])
    # print([i["name"] for i in dps.get_projects(amount=4)])
    # print(dps.get_hackathon_projects("https://hack-the-valley-v.devpost.com/"))
    # print(dps.get_hackathon_projects("https://hack-the-valley-v.devpost.com/"))
    #    print(dps.get_profile_projects('https://devpost.com/shutong5s'))
    print(get_project_info('https://devpost.com/software/shopadvisr'))
