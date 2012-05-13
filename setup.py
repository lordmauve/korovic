from setuptools import setup, find_packages

setup(
    name='korovic',
    version='1.0',
    packages=find_packages(),
    description="Dr. Korovic's Flying Atomic Squid",
    long_description=open('README').read(),
    author='Daniel Pope',
    author_email='lord.mauve@gmail.com',
    url='http://www.pyweek.org/e/wasabi/',
    install_requires=[
        'pyglet>=1.1.4',
        'pymunk==2.1.0',
        'pygame>=1.9.1release',
        'lepton==1.0b2'
    ],
    package_data={
        'korovic': ['data/*/*'],
    },
    entry_points={
        'console_scripts': [
            'korovic = korovic.__main__:main',
            ]   
        }
    )
