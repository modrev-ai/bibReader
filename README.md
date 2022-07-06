# Pandarize
This project aims to turn all kinds of data structure/types into a nice tabulated pandas DataFrame

# Installation
```
pip install pandarize
```

# Basic Usage Guide
```python
from pandarize.frame import Pandarizer

pdr = Pandarizer() #instantiate Pandarizer class
pdr.load(source='https://somewebsite.com/filename.bib') #it can load from url or local source
pdr.fit() #infers data types and parse it into pandas dataframe
pdr.transform() #changes pandas dataframe into different mode of data types
```

# Currently Supported Data Types
- bib

