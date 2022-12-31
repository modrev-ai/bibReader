import re
import os
import pandas as pd
from ._util import *
from pylatexenc.latex2text import LatexNodes2Text

class Parser:
    def __init__(self):
        self.df = None

    def bib_preprocessing(self):
        '''Pre-processes raw bib file'''
        
        raw = self.raw.replace('\n', '').replace('\r', '') #remove linebreaks and linefeed
        raw = re.sub(' +', ' ', raw) #contract whitespace
        
        self.raw = raw

    def postprocessing(self, df):
        '''Post-process of constructed pandas DataFrame. Runs multiple checks.'''
        
        # Author Name Check for Biber
        if self.settings['convert_names']:
            df['author'] = df['author'].apply(lambda x: convert_names(x))
        
        return df

    def bib_parser(self, postprocess):
        '''Main bib parsing logic'''
        all_lst = []
        lst = []
        start = None
        standby = None
        raw = self.raw
        idxkey = rfindall_matched(raw, r'[.*]?@[^}]*{*[,]', '@')

        for i, c in enumerate(raw):
            if c == '@':
                if not i in idxkey: #skip if not true start
                    continue
                
                if lst:
                    # fixes cases when extra comma is added to the last key:value item
                    fix = raw[curr_idx:last_pair-2] + raw[last_pair-2:last_pair+1].replace(',', '')
                    lst.append(fix) #edge case for last key:value pair
                    all_lst.append(self._itemize_bib(lst))
                lst = []
                curr_idx = i
                start = True
            elif c == ',' and start:
                lst.append(raw[curr_idx:i+1])
                start = False
                curr_idx = i+1
            elif c == '}' and i != len(raw)-1:
                last_pair = i #catches last pair and saves position as index
                standby = True
            elif c == ',' and standby:
                # second check to account for misused bracket edge cases
                # e.g., author = {A and B and C and {D} and F}
                standby = False
                
                for check_i in raw[i+1:]:
                    if check_i == '}':
                        break
                    elif check_i == '=':
                        if raw[curr_idx:i+1]:
                            lst.append(raw[curr_idx:i+1]) #remove linebreak
                            curr_idx = i+1
                        else:
                            break
            elif i == len(raw)-1:
                fix = raw[curr_idx:-3] + raw[-3:].replace(',', '')
                lst.append(fix)
                all_lst.append(self._itemize_bib(lst))
            elif c == ' ':
                pass
            else:
                standby = False

        df = pd.DataFrame(all_lst)
        if postprocess:
            df = postprocessing(df)

        self.df = df
        
    @staticmethod
    def _bib_screen(item):
        """Screens main body of bib for any edge case discrepancies

        Args:
            item (str): string item to be analyzed
        """
          
        # Last comma is deemed to be erroneous
        item = item[:-1] + item[-1].replace(',','')
        
        return item
    
    def bib_writer(self, filename):
        '''bib writer and formatter that converts pandas 
        dataframe into a bib file
        '''

        df = self.df
        dirs = 'output/'
        types = 'type' #column name for each bib entry type
        alias = 'alias' #column name for each bib id

        def parse(row, types=types, alias=alias):
            items = []

            for i, (idx, item) in enumerate(zip(row.index, row)):
                if pd.isnull(item) or item == '' and self.settings['remove_empty_entries']:
                    continue
                item = str(item)
                if idx == types:
                    header = f'@{item}' + '{'
                elif idx == alias:
                    alias = item + ',\n'
                else:
                    item_i = f'\t{idx} = ' + '{' + f'{self._bib_screen(item)}' + '},\n'
                    items.append(item_i)

            out_text = header + alias
            for i in items:
                out_text += i
            out_text = out_text[:-2] #remove last comma
            out_text += '\n},\n'

            return out_text

        N = df.shape[0]

        # Add stamper before the first header
        out = stamper(target='bib')

        for i in range(N):
            if i == N-1: #remove the very last comma
                out += parse(df.iloc[i,:])[:-3] + parse(df.iloc[i,:])[-3:].replace(',', '') + '\n'
            else:
                out += parse(df.iloc[i,:]) + '\n'

        if not os.path.exists(path=dirs):
            os.mkdir(path=dirs)

        with open(f'{dirs}{filename}.bib', 'w', encoding='utf-8') as f:
            f.write(out)

    @staticmethod
    def _itemize_bib(lst):
        '''Itemizes bib structured string into a json format'''
        new_lst = []
        dic = {}

        for i, s in enumerate(lst):
            if i == 0:
                ii = s.rfind('@')
                jj = s.rfind('{')
                kk = s.rfind(',')
                dic['type'] = s[ii:jj].replace('@', '')
                dic['alias'] = s[jj:kk].replace('{', '')
            else:
                if s:
                    ii = sorted(rfindall(s, '='))[0]
                    if s[-1] == ',':
                        s = s[:-1]
                    out = LatexNodes2Text().latex_to_text(s[ii+1:]).strip()
                    dic[s[:ii].strip()] = out

        return dic