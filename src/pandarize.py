import pandas as pd
import src.util as util

class Pandarize:
    def __init__(self):
        self.raw = None
        self.df = None

    def load(self, source=None):
        '''Loads data from the source

        TODO: source type inference
        '''

        self.raw = util._url_loader(url=source)

    def fit(self, kind='bib'):
        if kind == 'bib':
            self.df = util._bib_parser(raw=self.raw)

