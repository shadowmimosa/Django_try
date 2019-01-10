<font size=4 face='楷体'>  

# Script for Building TestDemo

### Convert python2 to python3

<a>Completed on 2018.9.20</a>

[TOC]


### Related modules  

- [autotest&period;py](./autotest.py)
  根据模板自动生成接口测试模板
- [AutoTest_alone&period;py](./AutoTest_alone.py)
  根据模板自动生成接口测试模板
- [Itchat_method&period;py](./Itchat_method.py)
  微信发送消息
- [tool_reptile&period;py](./tool_reptile.py)
  对数据进行过滤筛选 格式化
- [tools_library&period;py](./tools_library.py)
  json数据处理 读取 存储文件
- [Usertool_01&period;py](./Usertool_01.py)
  json数据处理
- [Verification&period;py](./Verification.py) 
  公共json数据校验方法，遍历data数据，校验字符串及整型数值
- [Verification_Field&period;py](./Verification_Field.py)
  校验字段 结果

#### Major modification

+ `raw_input()` unified to  `input()`   
  No Function `raw_input()` in python3  
+ Unify delete `#_*_ coding:utf-8 _*_`   
  UTF-8 is the default encoding of python3  
+ Unify delete `print(***.decode(utf-8))`  
  It also can be changed `print(***.encode(utf-8).decode(utf-8))`, It doesn't make  much sense  
+ Unify Change `print` to `print()`  
  The characteristic of python3  
+ Unity change `open(**, '*')` to `open(**, '*',encoding='UTF-8')`  
  Open file in python3 requires coding format specified  
+ Unify delete `reload(sys)` & `sys.setdefaultencoding('utf-8')`  
  There is no meaning in python3.  

#### Modification of related modules

+ [autotest&period;py](./autotest.py)   
  Delete useless comments  
  Delete `import hashlib`  
  Delete `import logging`  
  Delete `import platform`  
  Delete `import random`  
  Delete `import shutil`  
  Delete `import signal`  
  Delete `import subprocess`  
  Delete `import sys`  
  Delete `import threading`  
  Delete `import traceback`  
  Delete line `getfieldlistlen = len(getfieldlist)`  
  Delete line `ls_time = [start_time_st, end_time_st]`  
  Add exception handling if 'thejoyun.com' not in url  

+ [AutoTest_alone&period;py](./AutoTest_alone.py)  
  Delete useless comments  
  Delete `import hashlib`  
  Delete `import logging`  
  Delete `import platform`  
  Delete `import random`  
  Delete `import shutil`  
  Delete `import signal`  
  Delete `import subprocess`  
  Delete `import sys`  
  Delete `import threading`  
  Delete `import time`  
  Delete `import traceback`  
  Add http header after processing url  
  We need to modify the file directory according to the actual situation.  
  ```python  
  if len(home) < 2:
    demopath = 'C:\\Users\\ShadowMimosa\\Desktop\\STU\\Top\\Lib\\Demo.txt'
    home = 'C:\\Users\\ShadowMimosa\\Desktop\\STU\\Top\\Lib'
  else:
    demopath = home + '\\Demo.txt'
  ```  

+ [Itchat_method&period;py](./Itchat_method.py)  
  Delete useless comments  
  Delete `import datetime`  
  Delete `import json`  
  Delete `import string`  
  Delete `import os`  

+ [tool_reptile&period;py](./tool_reptile.py)  
  Delete useless comments  
  Delete `import sys`  
  Delete `import os`  
  Delete `converCode` 函数，python3中 `json.dumps()` 有变化  
  Change the parameter name `"encodeingtype"` to `"encodingtype"`  
  Change the List assignment method  
  ```python  
  # conditionlist[0] = conditionstr
  conditionlist.append(conditionstr)  
  ```  
  Change `'!='` to `'!='`, Stopping using `'!='`  in python3  
  The method need to be revised   
  `convertCode()` `Dict_sorted()` `Json_to_Dict()` `funfilter()` `FindAndValue()` `pyfilter()`

+ [tools_library&period;py](./tools_library.py)  
  Delete useless comments  
  Delete`import json`  
  Delete `from multiprocessing import Process`  
  Modify import mode to `from urllib.parse import quote, unquote` This package has changed in python3  
  Change `'\]' '\['` to `'\\]' '\\['` Avoid ambiguity  
  Change all backslask to double backslash, avoiding ambiguity  
  Change  `str = content.decode(encoding='UTF-8', errors='strict')` to `str = content(encoding='UTF-8', errors='strict')`  
  Change  
  ```python
          if type == 'md5':
            str = encrypttype.get(type)(encstr, bit)
        else:
            str = encrypttype.get(type)(encstr)
        return str
  ```
  To  
  ```python
          if type == 'md5':
            str = encrypttype.get(type)(encstr.encode('utf-8'), bit)
        else:
            str = encrypttype.get(type)(encstr.encode('utf-8'))
        return str
  ```
  Replace `print('Bind failed. Error Code : %s, Message: %s' % (str(msg[0]), msg[1]))` with `pass`  
  Replace `str = content.decode(encoding='UTF-8', errors='strict')` with `str = content(encoding='UTF-8', errors='strict')`  
  Replace `str1 = content(encoding='UTF-8', errors='strict')` with `str1 = str(content, encoding='UTF-8')`  
  Change `string = content.decode('unicode_escape')` to `string = content('unicode_escape')`
  Change  `string = content.decode('unicode_escape')` to `string = content('unicode_escape')`
  Change `str = string.join(l).replace(' ', '')` to `str = ''.join(l).replace(' ', '')`  
  Delete `from Crypto.Cipher import PKCS1_OAEP` No using  
  The `Crypto.Cipher` was abandoned in python3, needing to use `pip3 install pycryptodome`  
  Change `except socket.error, msg:` to `except socket.error as msg:` The method of except & try has changed in python3  
  
+ [Usertool_01&period;py](./Usertool_01.py)  
  Delete useless comments  
  Change `import StringIO` to `from io import StringIO`  
  Change `xrange` to `range`  
  Change `StringIO.StringIO()` to `StringIO()`  
  Change `string.join()` to `''.join()`  
  Change `json.loads(jsonData, "utf-8")` to `json.loads(jsonData)` The encoding argument is ignored and deprecated.  
  Change `file1 = open(name, "wb")` to `file1 = open(name, "w")`  
  Change `file1 = open(name, "rb")` to `file1 = open(name, "r")`  
  Change `f1 = open(name, "ab")` to `f1 = open(name, "a")`  
  Change `f2 = open(name, "rb")` to `f2 = open(name, "r")`  
  Change `f1 = open(name, "rb")` to `f1 = open(name, "r")`  
  Change `f1 = open("id.pkl", "ab")` to `f1 = open("id.pkl", "a")`  
  Change `f2 = open("id.pkl", "rb")` to `f2 = open("id.pkl", "r")`  
  Function `base64Code()` Modified  
  ```python  
    # bype_string = bytes(data, 'utf-8')
    bype_string=data
    missing_padding = len(bype_string) % 4
    if missing_padding != 0:
        bype_string += b'=' * missing_padding
    return base64.decodestring(bype_string)
  ```  
  Function `base64ENCode()` Add  
  ```python
    bytes_string = data.encode(encoding="utf-8")
  ```  
  Function `printUTF(data)` is not Meaningful  
  Function `getRandomValue_Range` Rewrited  
  Function `getRandomValue_List` Rewrited  
  Change `str` to `random_str`  
  Function `getlist()` added exception handling  

  There are almost no Function Comments.   
  Most Finctions input and outout formats are ont standardized.  
  

+ [Verification&period;py](./Verification.py)  
  Delete useless comments  
  Modifying tab and spaces mixing  
  The `items()` was abandoned in python3, needing to use `items()`  
  Add `logging.basicConfig()` to format print log  


+ [Verification_Field&period;py](./Verification_Field.py)  
  Delete unless comments  
  Delete `import sys`  
  Delete `import re`  
  Change argument `test` to default argument in function `analysis_subItem()`  
  Using keyword assignment when quoting method `analysis_subItem()`   
  
  
