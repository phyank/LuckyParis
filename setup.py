from distutils.core import setup

setup(
    name='LuckyParis',
    version='0.9',
    packages=['UI', 'bin', 'login', 'utils', 'utils.loader', 'spider', 'elector', 'database'],
    url='https://github/sjtuEleClub/LuckyParis',
    license='',
    author='phyank',
    author_email='aomoriraku@gmail.com',
    description='',
    install_requires=['scrapy','Jinja2','requests','pytesseract']
)
