import requests
import pandas as pd

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
                new_row[curr_name] = raw[get_item:i].strip()
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