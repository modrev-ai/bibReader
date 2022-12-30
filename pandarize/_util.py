import requests
import pandas as pd
from datetime import datetime
from pylatexenc.latex2text import LatexNodes2Text
import re
import os
import yaml as pyyaml
import pkgutil

def source_loader(source, savefile):
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

    return raw

def validate_config(obj):
    '''Validates yaml config files'''
    pass

def load_config(yaml, path, ftype='bib'):
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
            return load(f)
    else:
        data = pkgutil.get_data(__name__, "/config/config.yaml").decode('utf-8')
        return load(data)

def rfindall(string, pattern):
    '''Find index of all occurrence of the pattern'''
    
    indexes = []
    while not string.rfind(pattern) == -1:
        idx = string.rfind(pattern)
        indexes += [idx]
        string = string[:idx]
        
    return indexes

def rfindall_matched(string, pattern, key):
    '''Find all indices of the match pattern w.r.t to the key value
    
    E.g., the function returns [5] when attempts to find 
    pattern ({abc}) in the string '123{abc}def' w.r.t. the key (b)
    
    Args:
    -----
    string : string; string to be searched
    pattern : regex; regex pattern to be searched in string
    key : string; a character from the string
    
    Returns:
    out : list; returns a list of integers for each index
    '''
    match_index = []
    for match in re.finditer(pattern, string):
       match_index.append(match.start() + match.group().rfind(key))
    return match_index

def bib_preprocessing(raw):
    '''Pre-processes raw bib file'''
    
    raw = raw.replace('\n', '').replace('\r', '') #remove linebreaks and linefeed
    raw = re.sub(' +', ' ', raw) #contract whitespace
    
    return raw

def bib_parser(raw, idxkey, postprocess):
    '''Main bib parsing logic'''
    all_lst = []
    lst = []
    start = None
    standby = None

    for i, c in enumerate(raw):
        if c == '@':
            if not i in idxkey: #skip if not true start
                continue
            
            if lst:
                # fixes cases when extra comma is added to the last key:value item
                fix = raw[curr_idx:last_pair-2] + raw[last_pair-2:last_pair+1].replace(',', '')
                lst.append(fix) #edge case for last key:value pair
                all_lst.append(_itemize_bib(lst))
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
            lst.append(raw[curr_idx:i+1])
            all_lst.append(_itemize_bib(lst))
        elif c == ' ':
            pass
        else:
            standby = False

    df = pd.DataFrame(all_lst)
    if postprocess:
        df = postprocessing(df)

    return df

def truncate_names(srs):
    '''Truncates names in Pandas series'''
    pass

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
                # print(s, sorted(rfindall(s, '=')))
                ii = sorted(rfindall(s, '='))[0]
                if s[-1] == ',':
                    s = s[:-1]
                out = LatexNodes2Text().latex_to_text(s[ii+1:]).strip()
                dic[s[:ii].strip()] = out
            
    for i in lst:
        new_lst.append(LatexNodes2Text().latex_to_text(i))
        
    return dic

def check_string(string):
    '''Screens for misinterpreted strings that interferes parsing (deprecated)'''
    
    # for patterns {\'c} and {\%}
    patterns = [r"\{[\]?[\\]?[']?[a-zA-Z|%]\}", r"[\\]?[~]?{}", r"{\.}", r"placeholder@"]
    for idx, pattern in enumerate(patterns):
        for i in re.findall(pattern, string):
            if idx == 0:
                string = string.replace(i, i[-2])
            elif idx == 1:
                string = string.replace(i, '')
                #placeholder for future conditions

    return string

def check_url(string):
    '''Checks whether string is an url or not
    '''
    keywords = ['https://', 'http://', 'www.']

    for keyword in keywords:
        if keyword in string:
            return True

    return False

def stamper(target, marker='%'):
    '''Creates head stamp on the transformed dataframe
    '''
    msg = f'{marker}'*60 + '\n'
    msg += f'{marker} This {target} file is created and stylized by pandarize\n'
    msg += f'{marker} Date: {datetime.today().date()}\n'
    msg += f'{marker} Author: Jong M. Shin\n'
    msg += f'{marker} Email: jshinm@gmail.com\n'
    msg += f'{marker} Webpage: https://pypi.org/project/pandarize/\n'
    msg += f'{marker}'*60 + '\n\n'

    return msg

def manual_drop(raw, keys):
    for key in keys:
        raw = raw.replace(key,'')
    
    return raw

def postprocessing(df):
    '''Post-process of constructed pandas DataFrame. Runs multiple checks.'''
    
    # Author Name Check for Biber
    df['author'] = df['author'].apply(lambda x: convert_names(x))
    
    return df

def check_names(string, sep, connector):
    '''Checks for valid author names'''
    if connector in string:
        return True
    
    # skip in case at least one name is already converted
    # or there's misformatting issue
    if sep in string:
        return True
    
    return False

def convert_names(string, sep=',', connector='and'):
    """Convert First MI Last names to Last, First MI format.

    Args:
        string (str): parsed string that contains names with (name)(sep)(name) format
        sep (str, optional): original string separator between names. Defaults to ','.
        connector (str, optional): new name connector that will connect converted names. Defaults to 'and'.

    Returns:
        str: converted names connected by `connector`
    """
    
    padded_connector = f' {connector} '
    
    if check_names(string, sep=sep, connector=padded_connector):
        return string
    
    names = ''
    lst = string.split(sep)
    
    for i, nms in enumerate(lst):
        try:
            nm = nms.strip().split(' ')
            names += f'{nm[-1]}, {nm[0]}'
            if len(nm) > 2:
                for mname in nm[1:-1]:
                    names += f' {mname[0].upper()}.'
            if i+1 != len(lst):
                names += f'{padded_connector}'
        except Exception as e:
            print(f'{e} for {nms} at {i}th index')
            
    # conditional here for truncate author list
    
            
    return names

def bib_writer(df, types, alias, dirs):
    '''bib writer and formatter that converts pandas 
    dataframe into a bib file
    '''

    def parse(row, types=types, alias=alias):
        items = []

        for i, (idx, item) in enumerate(zip(row.index, row)):
            if pd.isnull(item) or item == '':
                continue
            item = str(item)
            if idx == types:
                header = f'@{item}' + '{'
            elif idx == alias:
                alias = item + ',\n'
            else:
                item_i = f'\t{idx} = ' + '{' + f'{item}' + '},\n'
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

    with open(f'{dirs}output.bib', 'w', encoding='utf-8') as f:
        f.write(out)