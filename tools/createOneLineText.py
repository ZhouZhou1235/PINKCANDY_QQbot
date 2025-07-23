# 创建单行文本

import os

workPath = os.getcwd().replace("\\","/")
input_path = workPath+"/tools/createOneLineText_input.txt"
output_path = workPath+"/tools/createOneLineText_output.txt"

text = ''

with open(input_path,'r',encoding='UTF-8') as f:
    text = f.read()
    text = ' '.join(text.splitlines())

with open(output_path,'w+',encoding='UTF-8') as f:
    f.write(text)
