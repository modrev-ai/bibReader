from distutils.core import setup
from setuptools import find_packages
import bibReader

VERSION = bibReader.__version__
with open('README.md', 'r') as f:
    README = f.read()

setup(
    name='bibReader',
    version=VERSION,
    author='Jong M. Shin',
    author_email='jshinm@gmail.com',
    packages=find_packages(),
    package_data = {"": ['bibReader/config/config.yaml']},
    include_package_data=True,
    url='https://github.com/jshinm/bibReader/',
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