from setuptools import setup, find_packages

setup(  name='YiFi',
        author='Blesslin Jerish R',
        version='1.0.1',
        description='Just a .torrent 8K UHD database downloader for YTS Web Application.',
        packages=find_packages(),
        install_requires=['requests', 'argparse', 'tqdm', 'fake-useragent'],
        entry_points={'console_scripts': 'YiFi = YiFi.main:main'},
        license=open('LICENSE').read(),
        keywords=['yts', 'yify','Blesslin Jerish R', 'scraper', 'media', 'download', 'downloader', 'torrent']
    )