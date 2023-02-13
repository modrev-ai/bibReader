import pandas as pd
from ._util import *
from .loader import Loader
from .parser import Parser

class bReader(Loader, Parser):
    
    def __init__(self):
        self.initialize()

    def initialize(self, path=None):
        '''Initializes the setting either for the first time by
        loading a default yaml config file in system dir or 
        load from an user-specified existing the file in `path`
        '''
        self.load_config(path=path)

    def load(self, source=None, savefile=None):
        '''Loads raw data from either local file or the url
        '''
        self.source_loader(source=source, savefile=savefile)
        self.bib_preprocessing()

    def fit(self, kind='bib', postprocess=False):
        '''Method that infers data structure (in the future)
        '''
        if kind == 'bib':
            self.bib_parser(postprocess=postprocess)

    def transform(self, formats='bib', filename='output'):
        '''Transform loaded data into a specified data type
        '''
        if formats == 'bib':
            self.bib_writer(filename=filename)
            
    def describe(self):
        '''Generates basic metadata'''
        
        if self.df is None:
            print('No file is loaded. Please load() and fit() to create metadata.')
            return 
            
        if self.df.shape[0] == 0 or self.df.shape[1] == 0:
            print('The file has not been loaded successfully. Please check the file path and/or make sure that file is not corrupted.')
            return 
            
        print(f'''The loaded file has {self.df.shape[0]} rows and {self.df.shape[1]} columns.\n
              ''')
