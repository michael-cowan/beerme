import os
import urllib.request
import string
import re
from datetime import datetime as dt
from bs4 import BeautifulSoup
import beerme_io

# brewersfriend url
BASEURL = 'http://www.brewersfriend.com'

# directory of homebrew database
DATADIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       '..',
                       'data')

# pickle database path
DBPATH = os.path.join(DATADIR, 'bdb.pickle')

# header used to scrape from brewersfriend
HDR = {'User-Agent': ' '.join(['Mozilla/5.0',
                               '(X11; Linux x86_64)',
                               'AppleWebKit/537.11',
                               '(KHTML, like Gecko)',
                               'Chrome/23.0.1271.64 Safari/537.11'])}


def bs_scrape(url):
    """
    Generic function to scrape a webpage into a BeautifulSoup object

    Args:
    url (str): url of a website

    Returns:
    (BeautifulSoup): bs object of the HTML website
    """
    # create page request
    req = urllib.request.Request(url, headers=HDR)

    # request page
    site = urllib.request.urlopen(req)
    text = site.read()

    # read site into BeautifulSoup
    return BeautifulSoup(text, 'html.parser')


def scrape_recipe_urls(num_pages=0, sortby_rating=True):
    """
    Generator that scrapes beer recipe urls

    KArgs:
    num_pages (int): number of pages to scrape (20 beers per page)
                     if <= 0, no page limit (will scrape all 8028 pages)
                     (Default: 0 [no page limit])
    sortby_rating (bool): if true, pages are sorted by beer rating
                          (Default: True)

    Returns:
    (str): each generation is a url of a homebrew recipe
    """
    # total of 8027 pages of beers
    if num_pages <= 0:
        num_pages = 8028

    for page in range(1, min(num_pages + 1, 8028)):
        # build url for page of recipes
        url = BASEURL + '/homebrew-recipes/page/%i' % page
        if sortby_rating:
            url = url + '?sort=rating-desc'

        # iteratively yield recipe urls (NOTE: does not include BASEURL)
        for val in bs_scrape(url).find_all('a', {'class': 'recipetitle'}):
            yield BASEURL + val['href']


def clean_brew_details(table, name=''):
    """
    Function to parse HTML table tags from homebrew recipe pages

    Args:
    table (BeautifulSoup tag): table object to parse

    Kargs:
    name (str): name of table given by recipe
                - e.g. fermentation, hops, etc.

    Returns:
    (list of lists): list matrix of data labels and values
    """
    # groups based on further cleaning needed
    nocleaning = {'mashsteps', 'others'}

    # extract all text, ignoring invisible text (i.e. where display = none)
    data = [[val.get_text('||', strip=True).strip('--')
             for val in tr.find_all(['th', 'td'])]
            for tr in table.find_all('tr')]

    if name in nocleaning:
        return data

    elif name == 'yeasts':
        # create single list with alternating columns and values
        data = ['name', data[0][0]] + data[1][0].split('||')

        # reshape into row of column names and row of values
        data = [data[::2], data[1::2]]

    elif name == 'primingmethod':
        # absolute madness in a list comprehension :)
        data = [i.replace('||', '_').strip('\xa0').strip('\t')
                for rowtext in data[0][0].split('\n')
                for i in rowtext.split(': ')]

        # reshape into row of column names and row of values
        data = [data[::2], data[1::2]]

    elif name == 'water':
        # replace || with _ for ion names
        data[0] = ['_'.join(d.split('||')) for d in data[0]]

        # convert values to floats
        data[1] = [None if not d else float(d) for d in data[1]]

        # add description to end of columns
        data[0].append('description')
        desc = '' if len(data) <= 2 else data[2][0]
        data[1].append(desc)

        # drop bottom columns
        data = data[:2]

    # None is comments section
    elif name is None:
        # flatten matrix
        data = [txt for row in data for txt in row]

        # drop empty strings and the first item
        # (which is a long text of all comments)
        data = [txt for txt in data[1:] if txt]

        # column names
        cols = ['user', 'date_time', 'rating', 'comment']
        vals = []
        for j, com in enumerate(data):
            com = com.split('||')
            user = com[0]

            # NOTE: I can easily convert these to datetime objects,
            # but then I can't save as a json file...
            # Convert using: dt.strptime(com[2], '%m/%d/%Y at %I:%M%p')
            date_time = com[2]

            if len(com) == 3:
                rating = None
                comment = ''
            else:
                if re.match('[0-5] of 5', com[3]):
                    rating = int(com[3][0])
                else:
                    rating = None
                i = 4 if rating else 3
                comment = '\n'.join(com[i:])

            # add row of comment data
            vals.append([user, date_time, rating, comment])

        # create matrix of column names and values
        data = [cols] + vals

    # else just drop text after ||
    else:
        data = [[d.split('||')[0] for d in row] for row in data]

        # drop last "Total" row from fermentablesss
        if name == 'fermentables' and 'Total' in data[-1]:
            data = data[:-1]

    return data


def parse_brew_data(soup):
    """
    Parses and cleans data of a homebrew recipe

    Args:
    soup (BeautifulSoup): bs object of homebrew recipe page

    Returns:
    (dict): organized data of a homebrew recipe
    """
    # get homebrew details from table tags on page
    brew = {d.get('id'): clean_brew_details(d.table, d.get('id'))
            for d in soup.find_all('div', {'class': 'brewpart'}) if d.table}

    # convert None to comments label
    if None in brew:
        brew['comments'] = brew.pop(None)

    # get the general beer stats
    # OG, FG, ABV, IBU, SRM, Mash pH
    stats = soup.find('div', id='calStatsGreyBar') \
                .getText('||', strip=True) \
                .replace('\t', '') \
                .replace(':', '') \
                .split('||')

    # get labels and values
    stat_lab = stats[::2]
    stat_val = stats[1::2]

    # convert stats to numbers
    for i, val in enumerate(stat_val):
        if val == 'n/a':
            val = None
        elif '%' in val:
            val = float(val[:-1]) / 100
        # assume P indicates plato units of SG
        elif 'P' in val:
            print('Contains Plato Units!!!')
            # convert plato to SG
            plato = float(val[:-2])
            val = 1 + (plato / (258.6 - 227.1 * (plato / 258.2)))
        else:
            val = float(val)
        stat_val[i] = val

    # add stats as dictionary
    brew['stats'] = {k: v for k, v in zip(stat_lab, stat_val)}

    # get recipe stats (method, style, boil time, calories, carbs, etc.)
    recipe = [txt for stat in soup.find_all('span', {'class': 'viewStats'})
              for txt in stat.getText(strip=True).split(':') if txt]

    # get labels and values
    # add author and brewing notes to recipe
    rec_lab = recipe[::2] + ['author', 'notes']
    rec_val = recipe[1::2]

    # author
    rec_val.append(soup.find(itemprop='author').text)

    # notes
    notes = soup.find('div', {'class': 'ui message'})
    if notes and notes.p:
        txt = notes.p.text
    else:
        txt = ''
    rec_val.append(txt)

    # add recipe data as dictionary
    brew['recipe'] = {k: v for k, v in zip(rec_lab, rec_val)}

    return brew


def scrape_a_brew(soup=None, url=None, rid=None):
    """
    Scrapes a single homebrew recipe from brewersfriend.com
    - can take multiple argument types

    KArgs:
    soup (BeautifulSoup): bs object of homebrew recipe page
    url (str): complete url to homebrew recipe page
    rid (int || str): unique homebrew Recipe ID

    Returns:
    (dict): organized data of a homebrew recipe
    """
    if soup is None:
        if url is None:
            if rid is None:
                raise ValueError("Please pass in url or rid")
            url = BASEURL + '/homebrew/recipe/view/%i' % rid

        soup = bs_scrape(url)

    if soup.title.text.startswith('Permission Error'):
        return False
    else:
        return parse_brew_data(soup)


def batch_scrape(max_num=5, sortby_rating=True, save_json=False):
    """
    Scrapes multiple homebrew recipes and saves/updates a database
    Example beers:
    - Southern Tier Pumking Clone
        - rid = 16367
    - 60-minute clone
        - rid = 110851

    KArgs:
    max_num (int): maximum number of new beers to scrape
                   if == -1, no limit is given
                   (Default: 5)
    sortby_rating (bool): if true, pages are sorted by beer rating
                          (Default: True)
    save_json (bool): if True, will also save database as a json file
                      (Default: False)

    Returns:
    None
    """
    # get RIDs of beers whose data has already been found
    all_data = beerme_io.read_pickle(DBPATH)
    if all_data is None:
        all_data = {}
        found_rids = set()
    else:
        found_rids = set(all_data.keys())

    print(f'Currently have {len(found_rids)} homebrews in database')

    # track/limit number of new beers added to data
    added = 0
    for url in scrape_recipe_urls(sortby_rating=sortby_rating):
        # get RID # and name of beer from url
        rid, name = url.split('/')[-2:]

        # don't rescrape data of beer already in database
        if rid in found_rids:
            continue

        print(f'Getting data for {"/".join([rid, name])}')
        soup = bs_scrape(url)

        # if page was successfully loaded, get the homebrew data
        if soup:
            brew = scrape_a_brew(soup=soup)

            # if homebrew data was successfully loaded and cleaned,
            # add it to the database
            if brew:
                all_data[rid] = {'name': name,
                                 'url': url,
                                 'author': brew['recipe'].pop('author')}
                all_data[rid].update(brew)
                found_rids.add(rid)
                added += 1
                if added == max_num:
                    break

    # save database if new homebrews have been added
    if added:
        if save_json:
            beerme_io.write_json(DBPATH.replace('.pickle', '.json'), all_data)

        if beerme_io.write_pickle(DBPATH, all_data):
            print(f'Saved Beer database to {DBPATH}!')


if __name__ == '__main__':
    batch_scrape(1, sortby_rating=True, save_json=True)
