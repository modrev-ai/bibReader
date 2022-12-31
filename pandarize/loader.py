import os
import yaml as pyyaml
import requests
import pkgutil
from ._util import *

class Loader:
    def __init__(self):
        self.settings = None
        self.raw = None
    
    def source_loader(self, source, savefile):
        if check_url(string=source):
            r = requests.get(url=source)
            r = r.content
        else:
            try:
                with open(source, 'r', encoding='UTF-8', newline='') as f:
                    r = f.read()
            except Exception as e:
                print('Error while reading from local file')

        if isinstance(r, bytes):
            raw = r.decode('utf-8')
        elif isinstance(r, str):
            raw = r
        else:
            raise Exception('The source cannot be parsed')

        if savefile:
            folder, files = os.path.split(savefile)
            if not os.path.exists(path=folder):
                os.mkdir(path=folder)

            with open(savefile, 'w', encoding='UTF-8', newline='') as f:
                f.write(raw)

        self.raw = raw
    
    def validate_config(self, obj):
        '''Validates yaml config files'''
        pass

    def load_config(self, yaml=None, path=None, ftype='bib'):
        '''Loads yaml config file and returns a yaml object'''
        def load(data):
            try:
                dic = {}
                for i in pyyaml.safe_load(data)[ftype]:
                    for key, val in i.items():
                        dic[key] = val
                
                print('Configuration applied. Please change the setting via <class object>.settings as needed.')
                return dic
                
            except:
                print('The config file is either not found or corrupted.')
        
        if yaml and path:
            with open(path) as f:
                self.settings = load(f)
        else:
            data = pkgutil.get_data(__name__, "/config/config.yaml").decode('utf-8')
            self.settings = load(data)