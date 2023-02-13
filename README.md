[![PyPI](https://github.com/jshinm/pandarize/actions/workflows/publish-package.yml/badge.svg)](https://github.com/jshinm/pandarize/actions/workflows/publish-package.yml)
# bibReader
The bibReader reads non-standard bib format from files/url and convert them into pandas DataFrames to easily work with the data, and then tranforms them back into a standardized bib file.

# Installation
```
pip install bibReader
```

# Basic Usage Guide
```python
from bibReader.frame import bReader

bib = bReader() #instantiate bReader class
bib.load(source='https://somewebsite.com/filename.bib') #it can load from url or local source
bib.fit() #infers data types and parse it into pandas dataframe
bib.transform() #changes pandas dataframe into different mode of data types
```
