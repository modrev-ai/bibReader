import pandas as pd
from pandarize._util import *

class Pandarizer:
    def __init__(self):
        self.raw = None
        self.df = None

    def load(self, source=None, savefile=None):
        '''Loads raw data from either local file or the url
        '''
        self.raw = source_loader(source=source, savefile=savefile)

    def fit(self, kind='bib'):
        '''Method that infers data structure (in the future)
        '''
        if kind == 'bib':
            self.df = bib_parser(raw=self.raw)

    def transform(self, formats='bib', types=None, alias=None, dirs=None):
        '''Transform loaded data into a specified data type
        '''
        if formats == 'bib':
            bib_writer(df=self.df, types=types, alias=alias, dirs=dirs)