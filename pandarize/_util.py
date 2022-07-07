import requests
import pandas as pd
from datetime import datetime
import os

def url_loader(url):
    r = requests.get(url=url)
    r = r.content

    if isinstance(r, bytes):
        raw = r.decode('utf-8')
    elif isinstance(r, str):
        pass
    else:
        raise Exception('The source cannot be parsed')

    return raw

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

def bib_parser(raw):
    df_out = pd.DataFrame()
    raw = manual_drop(raw, keys=['\n'])
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

def bib_writer(df, types, alias, dirs):
    '''bib writer and formatter that converts pandas 
    dataframe into a bib file
    '''

    def parse(row, types=types, alias=alias):
        items = []

        for idx, item in zip(row.index, row):
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
        out_text += '}\n'

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