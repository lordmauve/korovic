from setuptools import setup, find_packages

setup(
    name='korovic',
    version='1.0',
    packages=find_packages(),
    install_requires=[
        'pyglet>=1.1.4',
        'pymunk==2.1.0'
    ],
    package_data={
        'gamename': ['data/*'],
    },
    entry_points={
        'console_scripts': [
            'korovic = korovic.__main__:main',
            ]   
        }
    )
