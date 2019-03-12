from setuptools import setup, find_packages

setup(
    name='reticfox',
    version='0.0.1a',
    license='GPLv3',
    description='Scripts to parse and move iCESM LGM slices for LGM Data Assimilation',

    author='S. Brewster Malevich',
    author_email='malevich@email.arizona.edu',
    url='https://github.com/brews/reticfox',

    packages=find_packages(),
    install_requires=['numpy', 'scipy', 'xarray', 'click', 'Ngl', 'dask', 'gsw'],

    entry_points={
        'console_scripts': [
            'reticfox = reticfox.cli:reticfox_cli',
        ]
    },
)
