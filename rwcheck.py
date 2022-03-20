#!/usr/bin/env python3
import sys
import rwpy.code as code
from rwpy.errors import IniSyntaxError

def log(message: str):
    print('rwcheck:' + message)


def isensured(text: str):
    return text.isspace() or text == '' or text.startswith('#')


if __name__ == '__main__':
    errors = []
    if len(sys.argv) == 2:
        ini = None
        with open(sys.argv[1],'r') as file:
            try:
                ini = code.create_ini(file.read())
            except IniSyntaxError as e:
                log(str(e))
                exit(-2)
        if ini is None:
            log('文件初始化失败')
        else:
            atbs = filter(lambda x: isinstance(x,code.Attribute),ini.elements)
            for ele in ini.elements:
                if isinstance(ele,code.Attribute):
                    if not atb.value.strip().startswith('@global'):
                        errors.append('行号:{0}|错误的ini头部属性->{1}'.format(atb.linenum,str(atb)))
                else:
                    if not isensured(str(ele)):
                        errors.append('行号:{0}|ini头部非正确的元素->{1}'.format(ele.linenum,str(ele)))
            read_sections = []
            for sec in ini.sections:
                if sec.name in map(lambda x: x.name,read_sections):
                    errors.append('行号:{0}|重复的段落名->{1}'.format(sec.linenum,sec.name))
                read_sections.append(sec)
                read_attributes = []
                for ele in sec.elements:
                    if isinstance(ele,code.Attribute):
                        if ele.key in map(lambda x: x.key,read_attributes):
                            errors.append('行号:{0}|在段落{1}中重复的属性->{2}'.format(ele.linenum,sec.name,str(ele)))
                        read_attributes.append(ele)
                    else:
                        if not isensured(str(ele)):
                            errors.append('行号:{0}|在段落{1}非合法元素->{2}'.format(ele.linenum,sec.name,str(ele)))
    else: 
        log('参数错误')
        exit(-1) 
    for e in errors:
        print(e)