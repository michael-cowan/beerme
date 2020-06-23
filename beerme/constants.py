import os

# header used to scrape from brewersfriend
HDR = {'User-Agent': ' '.join(['Mozilla/5.0',
                               '(X11; Linux x86_64)',
                               'AppleWebKit/537.11',
                               '(KHTML, like Gecko)',
                               'Chrome/23.0.1271.64 Safari/537.11'])}

# brewersfriend url
BASEURL = 'http://www.brewersfriend.com'

# base url for each homebrew recipe page
RECIPE_BASEURL = BASEURL + '/homebrew/recipe/view'

# directory of homebrew database
DATADIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       '..',
                       'data')

# pickle database path
DBPATH = os.path.join(DATADIR, 'bdb.pickle')

# path to csv of homebrew info (RID and name) needed to build URL path
# using a csv for easy updating through appending
URLDATAPATH = os.path.join(DATADIR, 'beer_urls.csv')

# path to pickle of known homebrew names that could not be scraped
FAILPATH = os.path.join(DATADIR, 'fails.pickle')
