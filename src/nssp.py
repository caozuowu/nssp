# nsssp: Next Step Style Plist
# Decode a next step style string to a dict/list
# Encode a dict/list to a string
# Support comment in sting
 
# format EX:
# {
#     /*comment key_a begin*/
#     key_a = 'value1'; /*comment this is value1*/
#     key_b = value2;
#     key_c = (1,a,b);
#     /*comment key_a end*/
#     key_d = {
#         sub_key_a = ({},{},{});
#         sub_key_b /*comment sub_key_b*/ = {
#
#         };
#     };
# }

import sys
 
__STRING_TYPE = 'basestring' if sys.version_info[0] == 2 else 'str'
 
__KEY_SYMBLES = [
    '{',
    '}',
    '(',
    ')',
    '=',
    ';',
    ','
]
 
def read(NSSPString):
    start, stack = 0, []
    while start < len(NSSPString):
        char, end, comments = __nextSymble(start, NSSPString)
        if char == '{':
            stack.append({})
        elif char == '(':
            stack.append([])
        elif char in ['}', ')']:
            stack.append(char)
        elif char == '=':
            key = __filt(NSSPString[start: end], comments)
            stack.append(key)
            stack.append('=')
        elif char == ';':
            top = stack.pop()
            if top in ['}', ')']:
                value = stack.pop()
                _ = stack.pop()
                key = stack.pop()
                stack[-1][key] = value
            elif top == '=':
                value = __filt(NSSPString[start: end], comments)
                key = stack.pop()
                stack[-1][key] = value
            else:
                TypeError("NSSylePlist __decode error, incorrect format at {end}", end = end)
        elif char == ',':
            top = stack.pop()
            if top in ['}', ')']:
                value = stack.pop()
                stack[-1].append(value)
            elif isinstance(top, list):
                value = __filt(NSSPString[start: end], comments)
                top.append(value)
                stack.append(top)
            else:
                TypeError("NSSylePlist __decode error, incorrect format at {end}", end = end)
        start = end + 1
    return stack[0]
 
def __filt(string, comments = []):
    out = string
    for c in comments:
        out = out.replace(c, '')
    out = out.strip()
    return out
 
def __cutSting(start, string):
    end, length = start + 1, len(string)
    if string[start] == '"':
        while end < length and not (string[end] == '"' and string[end-1] != '\\'):
            end += 1
        return (start, end, string[start: end + 1])
    else:
        return (start, start, '')
 
def __cutLineComment(start, string):
    end, length = start+2, len(string)
    if string[start: start+2] == '//':
        while end < length and string[end] != '\n':
            end += 1
        return (start, end, string[start: end+1])
    else:
        return (start, start, '')
 
def __cutBlockcomment(start, string):
    end, length = start+2, len(string)
    if string[start: start+2] == '/*':
        while end < length-1 and string[end: end + 2] != '*/':
            end += 1
        return (start, end+1, string[start: end+2])
    else:
        return (start, start, '')
 
def __nextSymble(start, string, keys = __KEY_SYMBLES):
    end = start
    length = len(string)
    blockComments = []
    while end < length:
        if string[end] == '"':
            _, end, _  = __cutSting(end, string)
        elif string[end: end+2] == '//':
            _, end, _ = __cutLineComment(end, string)
        elif string[end: end+2] == '/*':
            _, end, value = __cutBlockcomment(end, string)
            blockComments.append(value)
        if string[end] in keys:
            return (string[end], end, blockComments)            
        end += 1
    return (None, end, blockComments)

_string = open(r'C:\Users\zuowu\Desktop\projects\nssp\testfiles\project.pbxproj').read()
a = read(_string)
 
def write(obj, spacing, level):
    if type(obj) is dict:
        string = '{\n'
        for key, value in obj.items():
            string += spacing * (level + 1) * ' ' + key + " = " + write(value, spacing, level) + ';\n'
        string += spacing * level * ' ' + '}'
        return string
    elif type(obj) is list:
        string = '(\n'
        for value in obj:
            string += spacing * (level + 2) * ' ' + write(value, spacing, level) + ',\n'
        string +=  spacing * (level+1) * ' ' + ')'
        return string
    elif type(obj) is str:
        return obj
    else:
        return str(obj)
   
print(write(a, 4, 0))
