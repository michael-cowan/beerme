import setuptools

with open('beerme/_version.py', 'r') as fid:
    exec(fid.read())

with open('README.md', 'r') as readme:
    # ignore images, gifs, etc.
    description = ''.join([i for i in readme.readlines()
                           if not i.startswith('![')])

desc = 'tools to scrape and analyze brewing recipes from brewersfriend.com'

setuptools.setup(name='beerme',
                 version=__version__,
                 author='Michael Cowan',
                 url='https://www.github.com/michael-cowan/beerme',
                 description=desc,
                 long_description=description,
                 long_description_content_type='text/markdown',
                 packages=setuptools.find_packages(),
                 entry_points={
                     'console_scripts': ['beerme-scrape=beerme.bin.scrape:scrape'],
                 },
                 python_requires='>=3',
                 install_requires=['bs4', 'click>=7'])
