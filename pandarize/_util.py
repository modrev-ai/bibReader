import requests
import pandas as pd
from datetime import datetime
from pylatexenc.latex2text import LatexNodes2Text
import re
import os

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

def rfindall(string, pattern):
    '''Find index of all occurrence of the pattern'''
    
    indexes = []
    while not string.rfind(pattern) == -1:
        idx = string.rfind(pattern)
        indexes += [idx]
        string = string[:idx]
        
    return indexes

def bib_parser(raw):
    '''Main bib parsing logic'''
    all_lst = []
    lst = []
    start = None
    standby = None

    raw = raw.replace('\n', '').replace('\r', '') #remove linebreaks and linefeed
    raw = re.sub(' +', ' ', raw) #contract whitespace

    for i, c in enumerate(raw):
        if c == '@':
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
    df = postprocessing(df)

    return df

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

def bib_parser_old(raw):
    '''Old bib parsing logic (deprecated and replaced by the new logic)'''
    df_out = pd.DataFrame()
    raw = manual_drop(raw, keys=['\n'])
    raw = check_string(raw)
    is_newRow = True

    for i, char in enumerate(raw[:]):
        
        if char == '@' and is_newRow:
            new_row = {}
            get_type = i+1
        elif char == '{':
            if get_type:
                new_row['type'] = raw[get_type:i].strip()
                get_type = None
                get_alias = i+1 #get the alias
            elif curr_name != None:
                get_item = i+1
            else:
                pass
        elif char == '}':
            if get_item:
                new_row[curr_name] = raw[get_item:i]
                get_item = None
                curr_name = None
            else:
                df_row = pd.DataFrame.from_dict(new_row, orient='index').T
                df_out = pd.concat([df_out, df_row])
                is_newRow = True
        elif char == '=' and get_name:
            curr_name = raw[get_name:i].strip()
            new_row[curr_name] = None
            get_name = None
        elif char == ',':
            if get_alias:
                new_row['alias'] = raw[get_alias:i]
                get_alias = None
                is_newRow = False
            elif curr_name:
                continue #edge case to handle comma (,) in the content
            get_name = i+1
        else:
            pass
    
    df_out.reset_index(drop=True, inplace=True)

    return df_out

def check_names(string, connector):
    '''Checks for valid author names'''
    if connector in string:
        return True
    return False

def convert_names(string, sep=',', connector='and'):
    '''Convert First MI Last names to Last, First MI format.
    '''
    padded_connector = f' {connector} '
    
    if check_names(string, connector=padded_connector):
        return string
    
    names = ''
    lst = string.split(sep)
    
    for i, nms in enumerate(lst):
        nm = nms.strip().split(' ')
        names += f'{nm[-1]}, {nm[0]}'
        if len(nm) > 2:
            for mname in nm[1:-1]:
                names += f' {mname[0].upper()}.'
        if i+1 != len(lst):
            names += f'{padded_connector}'
            
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
        out_text += '\n}\n'

        return out_text

    N = df.shape[0]

    # Add stamper before the first header
    out = stamper(target='bib')

    for i in range(N):
        out += parse(df.iloc[i,:]) + '\n'

    if not os.path.exists(path=dirs):
        os.mkdir(path=dirs)

    with open(f'{dirs}output.bib', 'w', encoding='utf-8') as f:
        f.write(out)