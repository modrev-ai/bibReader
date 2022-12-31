from distutils.core import setup
from setuptools import find_packages
import pandarize

VERSION = pandarize.__version__
with open('README.md', 'r') as f:
    README = f.read()

setup(
    name='Pandarize',
    version=VERSION,
    author='Jong M. Shin',
    author_email='jshinm@gmail.com',
    packages=find_packages(),
    package_data = {"": ['pandarize/config/config.yaml']},
    url='https://github.com/jshinm/pandarize/',
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