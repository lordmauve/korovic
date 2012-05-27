import os
from setuptools import setup, find_packages
packages = list(find_packages())
try:
    import py2exe
except ImportError:
    pass
else:
    import sys
    sys.path.insert(0, 'win32')


here = os.path.dirname(__file__)
data_files = {}
for path, dirs, files in os.walk(os.path.join(here, 'korovic', 'data')):
    for f in files:
        p = os.path.join(path, f)
        data_files.setdefault(path, []).append(p)

data_files = data_files.items()

setup(
    name='korovic',
    version='1.1.0',
    packages=find_packages(),
    description="Dr. Korovic's Flying Atomic Squid",
    long_description=open('README').read(),
    author='Daniel Pope',
    author_email='lord.mauve@gmail.com',
    url='http://www.pyweek.org/e/wasabi/',
    install_requires=[
        'pyglet>=1.1.4',
        'pymunk==2.1.0',
        'pygame>=1.9.1',
        'lepton==1.0b2',
        'distribute>=0.6'
    ],
    package_data={
        'korovic': ['data/*/*'],
    },
    entry_points={
        'console_scripts': [
            'korovic = korovic.__main__:main',
        ]   
    },
    dependency_links=[
        'http://pygame.org/ftp/'
    ],
    windows=['run_game.py'],
    options={
        "py2exe": {
            "packages": ['pymunk']
        }
    },
    data_files=data_files
)
