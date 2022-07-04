import pandas as pd
import src._util as util

class Pandarize:
    def __init__(self):
        self.raw = None
        self.df = None

    def load(self, source=None):
        '''Loads data from the source

        TODO: source type inference
        '''

        self.raw = util.url_loader(url=source)

    def fit(self, kind='bib'):
        if kind == 'bib':
            self.df = util.bib_parser(raw=self.raw)

