from distutils.core import setup
from setuptools import find_packages
import yaml
import pandarize

VERSION = pandarize.__version__
with open('README.md', 'r') as f:
    README = f.read()

# load from config file
with yaml.safe_load('config/config.yaml')['app'] as y:
    APPNAME = y['appname']
    URL = y['url']

setup(
    name=APPNAME,
    version=VERSION,
    author='Jong M. Shin',
    author_email='jshinm@gmail.com',
    packages=find_packages(),
    package_data = {"": ['pandarize/config/config.yaml']},
    include_package_data=True,
    url=URL,
    license='MIT',
    description='Turns data into panda dataframe',
    readme='README.md',
    long_description_content_type='text/markdown',
    long_description=README,
    requires=['pandas', 'requests', 'pyyaml'],
    install_requires=["pandas", 'requests', 'pyyaml'],
    classifiers = [
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent"
    ]
)