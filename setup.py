#

from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='cypress',
    version='0.0.1',
    description='A visual programming environment for Python',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'cypress = cypress.__main__:main',
        ],
    },
)
        

