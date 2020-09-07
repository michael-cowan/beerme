import setuptools

with open('beerme/_version.py', 'r') as fid:
    exec(fid.read())

# with open('README.md', 'r') as readme:
#     # ignore gifs
#     description = ''.join([i for i in readme.readlines()
#                            if not i.startswith('![')])

desc = 'scraping and analysis tools for brewing recipes on brewersfriend.com'

setuptools.setup(name='beerme',
                 version=__version__,
                 author='Michael Cowan',
                 url='https://www.github.com/michael-cowan/beerme',
                 description=desc,
                #  long_description=description,
                #  long_description_content_type='text/markdown',
                 packages=setuptools.find_packages(),
                 python_requires='>=3',
                 install_requires=['pandas', 'matplotlib'])
