import pandas as pd
from pandarize import _util

class Pandarizer:
    def __init__(self):
        self.raw = None
        self.df = None

    def load(self, source=None, savefile=None):
        '''Loads data from either local file or the url
        '''
        if _util.check_url(string=source):
            self.raw = _util.url_loader(url=source, savefile=savefile)
        else:
            self.df = pd.read_excel(source, dtype=str)
            self.df.fillna('', inplace=True)

    def fit(self, kind='bib'):
        '''Method that infers data structure (in the future)
        '''
        if kind == 'bib':
            self.df = _util.bib_parser(raw=self.raw)

    def transform(self, formats='bib', types=None, alias=None, dirs=None):
        '''Transform loaded data into a specified data type
        '''

        if formats == 'bib':
            _util.bib_writer(df=self.df, types=types, alias=alias, dirs=dirs)