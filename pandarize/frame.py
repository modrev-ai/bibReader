import pandas as pd
from pandarize._util import *

class Pandarizer:
    def __init__(self):
        self.raw = None
        self.df = None
        self.idxkey = None

    def load(self, source=None, savefile=None):
        '''Loads raw data from either local file or the url
        '''
        self.raw = source_loader(source=source, savefile=savefile)
        self.raw = bib_preprocessing(raw=self.raw)
        self.idxkey = rfindall_matched(self.raw, r'[.*]?@[^}]*{*[,]', '@')

    def fit(self, kind='bib', postprocess=False):
        '''Method that infers data structure (in the future)
        '''
        if kind == 'bib':
            self.df = bib_parser(raw=self.raw, idxkey=self.idxkey, postprocess=postprocess)

    def transform(self, formats='bib', types=None, alias=None, dirs=None):
        '''Transform loaded data into a specified data type
        '''
        if formats == 'bib':
            bib_writer(df=self.df, types=types, alias=alias, dirs=dirs)