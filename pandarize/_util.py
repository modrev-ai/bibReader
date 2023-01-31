from datetime import datetime
import re

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

def truncate_names(srs):
    '''Truncates names in Pandas series'''
    pass

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
    msg += f'{marker} Webpage: https://pypi.org/project/pandarize/\n'
    msg += f'{marker}'*60 + '\n\n'

    return msg

def manual_drop(raw, keys):
    for key in keys:
        raw = raw.replace(key,'')
    
    return raw

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
