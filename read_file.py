import sys
import os
import re
import shutil
import copy
from functools import partial
import time
from copy import deepcopy

from ult_generator import header_parser
import re
import os


def finddir(startdir, target, root_path):
    try:
        # startdir = startdir.replace('/', '\\')
        os.chdir(startdir)
    except:
        # print('startdir err')
        # print(startdir)
        return None
    for new_dir in os.listdir(os.curdir):
        #print(new_dir)
        if new_dir == target:
            result = os.getcwd() + os.sep + new_dir
            #print(result)
            #os.chdir(root_path)
            return result
        if os.path.isdir(new_dir):
            result = finddir(new_dir, target, root_path)
            if result:
                return result
            os.chdir(os.pardir)
    return None

def find_super_class_file(class_name, includes, media_path):
    #print(includes)
    for include in includes:
        file_full_name = finddir(media_path, include, os.getcwd())
        if not file_full_name:
            continue
        with open(file_full_name, 'r') as fin:
            lines = fin.readlines()
            # if 2 class with same name occur in 2 different include files, may cause error
            for line in lines:
                if line.strip().startswith('class') and line.strip()[5:].strip().startswith(class_name):
                    if 6 + len(class_name) + 1 >= len(line):
                        continue
                    next_character = line[6 + len(class_name) + 1]
                    if next_character.isalnum() or next_character == '_':
                        continue
                    return file_full_name

def findSubClass(class_dic, super_class):
    for key, value in class_dic.items():
        if super_class in value:
            return key
    return None

def read_h_file(fileFullName):
    """

    :param input_file:
    :param media_path:
    :return:
    """

    index = max(fileFullName.rfind('\\'), fileFullName.rfind('/'))
    filePath = fileFullName[:index]
    fileName = fileFullName[index+1:]
    index = max(filePath.find('media_driver_next\\agnostic'), filePath.find('media_driver_next/agnostic'))
    media_path = filePath[:index+26]

    parser = header_parser.HeaderParser(fileName, filePath)
    print(os.getcwd())
    parser.read_file()
    parser.parse_file_info()
    super_class_dic = deepcopy(parser.super_class)
    super_class_list = []
    for key, value in super_class_dic.items():
        super_class_list.extend(value)
    includes = deepcopy(parser.includes)
    while super_class_list:
        super_class =  super_class_list[0]
        sub_class = findSubClass(super_class_dic, super_class)
        root_path = os.getcwd()
        s = find_super_class_file(super_class, includes, media_path)
        del super_class_list[0]
        print(s)
        os.chdir(root_path)
        if not s:
            break
        idx = max(s.rfind('/'), s.rfind('\\'))
        file_name = s[idx + 1:]
        file_path = s[:idx + 1]
        super_parser = header_parser.HeaderParser(file_name, file_path)
        super_parser.read_file()
        super_parser.parse_file_info()
        # add super class's method to parser
        for i, m in enumerate(super_parser.methods_info):
            if m['method_name'] in super_parser.functions_of_class[super_class] and m['method_name'] not in parser.functions_of_class[sub_class]:
                 parser.methods.append(super_parser.methods[i])
                 parser.methods_info.append(m)
                 parser.functions_of_class[sub_class].append(m['method_name'])
        # add super class's super class for check
        if super_class in super_parser.super_class:
            super_class_dic[sub_class].extend(super_parser.super_class[super_class])
            super_class_list.extend(super_parser.super_class[super_class])
        includes = includes | super_parser.includes
    return parser

#read_h_file(r'C:\Users\lingsun\gfx\gfx-driver\Source\media\media_driver\media_driver_next\agnostic\common\vp\hal\packet\vp_cmd_packet.h')
