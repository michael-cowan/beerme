import click
from pprint import pprint
import beerme.scraper as scrap
import beerme.constants as const
import beerme.beerme_io as beerio
from beerme import __version__

@click.command(name='beerme-scrape',
               context_settings=dict(help_option_names=['-h', '--help']))
@click.version_option(__version__)
@click.option('-n', '--number', default=100, type=int, metavar='<i>',
              help='number of recipes to scrape', show_default=True)
@click.option('-l', '--current-length', is_flag=True, help='current number of recipes in db')
@click.option('--example', is_flag=True, help='print raw data for one recipe')
def scrape(number, current_length, example):
    """
    beerme-scrape: scrape beer recipes from brewersfriend.com
    """
    if current_length or example:
        all_data = beerio.read_pickle(const.DBPATH)
        if current_length:
            print(f'Currently have {len(all_data):,} recipes in database.')
        if example:
            pprint(all_data.popitem()[1])
    else:
        scrap.batch_scrape(number, sortby_rating=True, save_json=False)

