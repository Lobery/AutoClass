import os
import copy
from xml.dom import minidom
class ClassContent(object):

    def __init__(self):
        self.BLANK_NUM = 100
        self.TestName = ''
        self.inputPara = []
        self.outputPara = []
        self.inputName = []
        self.inputType = []
        self.inputValue = []
        self.outputType = []
        self.outputValue = []
        self.outputName = []
        self.file_header = os.getcwd() + '\\' + 'sample_header.txt'
        self.workspace = ''
        self.includes = ['vp_reder_sfc_base.h', 'pipeline.h']
        #self.lines = []
        self.level = 0
        self.className = ''
        self.functionName = ''
        self.caseName = ''
        self.parser = None
        self.sourceFile = ''
        self.FTindex = ''
        self.returnValue = ''
        self.tag = ''
        self.log = ''
        self.xmlFile = ''
        self.ultPath = ''
        self.xmlPath = ''
        self.typeDic = {'int' : '0',
                        'uint4_t': '0',
                        'uint8_t': '0',
                        'uint16_t': '0',
                        'uint32_t': '0',
                        'uint64_t': '0',
                        'float' : '0',
                        'double' : '0',
                        'std::vector' : '""',
                        'vector' : '""',
                        'std::string' : '""',
                        'string' : '""',
                        'boolean' : 'False',
                        'char' : ''}
        self.TAB_SPACE = 4
        self.TestBaseClass = ''
        self.referencePath = ''

    def clear(self):
        self.TestName = ''
        self.inputPara = []
        self.inputName = []
        self.inputType = []
        self.inputValue = []
        self.outputPara = []
        self.outputName = []
        self.outputType = []
        self.outputValue = []
        self.log = ''

    def generateCmake(self, type, path, source = ''):
        file = os.path.join(path, 'ult_srcs.cmake')
        if type == '':
            lines = []
            lines.extend(self.getHeaders(type = 'cmake'))
            lines.append('ult_add_curr_to_include_path()\n')
        elif type == 'code':
            if os.path.exists(file):
                with open(file, 'r') as fopen:
                    lines = fopen.readlines()
                for i in range(len(lines)):
                    if lines[i].find('set(TMP_HEADERS') >= 0:
                        lines.insert(i+1, '    ${CMAKE_CURRENT_LIST_DIR}/' + self.sourceFile[:-2] + '_test_data.h' + '\n')
                        lines.insert(i+1, '    ${CMAKE_CURRENT_LIST_DIR}/' + self.sourceFile[:-2] + '_test_case.h' + '\n')
                        lines.insert(i+1, '    ${CMAKE_CURRENT_LIST_DIR}/' + self.sourceFile[:-2] + '_test.h' + '\n')
                        break
                for i in range(len(lines)):
                    if lines[i].find('set(TMP_SOURCES') >= 0:
                        lines.insert(i+1, '    ${CMAKE_CURRENT_LIST_DIR}/' + self.sourceFile[:-2] + '_test_case.cpp' + '\n')
                        lines.insert(i+1, '    ${CMAKE_CURRENT_LIST_DIR}/' + self.sourceFile[:-2] + '_test.cpp' + '\n')
                        break
            else:
                lines = []
                lines.extend(self.getHeaders(type = 'cmake'))
                lines.append('set(TMP_HEADERS_\n')
                lines.append('    ${CMAKE_CURRENT_LIST_DIR}/' + self.sourceFile[:-2] + '_test.h' + '\n')
                lines.append('    ${CMAKE_CURRENT_LIST_DIR}/' + self.sourceFile[:-2] + '_test_case.h' + '\n')
                lines.append('    ${CMAKE_CURRENT_LIST_DIR}/' + self.sourceFile[:-2] + '_test_data.h' + '\n')
                lines.append(')\n')
                lines.append('\n')
                lines.append('set(TMP_SOURCES_\n')
                lines.append('    ${CMAKE_CURRENT_LIST_DIR}/' + self.sourceFile[:-2] + '_test.cpp' + '\n')
                lines.append('    ${CMAKE_CURRENT_LIST_DIR}/' + self.sourceFile[:-2] + '_test_case.cpp' + '\n')
                lines.append(')\n')
                lines.append('\n')
                lines.append('set(ULT_LIB_HEADERS_ ${ULT_LIB_HEADERS_} ${TMP_HEADERS_})\n')
                lines.append('set(ULT_LIB_SOURCES_ ${ULT_LIB_SOURCES_} ${TMP_SOURCES_})\n')
                lines.append('\n')
                lines.append('source_group("' + source + '" FILES ${TMP_HEADERS_} ${TMP_SOURCES_})\n')
                lines.append('\n')
                lines.append('ult_add_curr_to_include_path()\n')
        elif type == 'resource':
            lines = []
            lines.extend(self.getHeaders(type = 'cmake'))
            lines.append('set(TMP_RESOURCES_\n')
            lines.append('    ${CMAKE_CURRENT_LIST_DIR}/media_driver_' + self.tag + '_ult.rc\n')
            lines.append('    )\n')
            lines.append('\n')
            lines.append('set(ULT_RESOURCES_\n')
            lines.append('    ${ULT_RESOURCES_}\n')
            lines.append('    ${TMP_RESOURCES_}\n')
            lines.append(')\n')
            lines.append('\n')
            lines.append('set(TMP_HEADERS_\n')
            lines.append('    ${CMAKE_CURRENT_LIST_DIR}/resource.h\n')
            lines.append(')\n')
            lines.append('\n')
            lines.append('set(ULT_LIB_HEADERS_\n')
            lines.append('    ${ULT_LIB_HEADERS_}\n')
            lines.append('    ${TMP_HEADERS_}\n')
            lines.append(')\n')
            lines.append('\n')
            lines.append('source_group("Resources" FILES ${TMP_RESOURCES_})\n')
            lines.append('source_group("Header Files" FILES ${TMP_HEADERS_})\n')
            lines.append('ult_add_curr_to_include_path()\n')
        else:
            with open(file, 'r') as fopen:
                lines = fopen.readlines()
            newLines = []
            newLines.append('ult_include_subdirectory(' + type + ')\n')
            for idx in reversed(range(len(lines))):
                if lines[idx].find('ult_add_curr_to_include_path()') >= 0:
                    insertIdx = idx
                    break
            lines = lines[:insertIdx] + newLines + lines[insertIdx:]
        with open(file, 'w') as fopen:
            fopen.writelines(lines)

    # generate directory and cmake
    def getFilePath(self, path):
        path = path.strip()
        self.ultPath = path[:path.find('\\media\\') + 1] + 'media\\media_embargo\\media_driver_next\\ult\\'
        separatePath = path.split('\\')
        separatePath = separatePath[separatePath.index('media_driver_next') + 1: ]
        del separatePath[-1]
        if separatePath[0] in ('windows', 'linux'):
            del separatePath[1]
        separatePath.insert(1, 'test')
        separatePath.append('focus_test')
        idx = 0
        while idx < len(separatePath):
            mid = separatePath[idx]
            if mid == 'hal':
                del separatePath[idx]
                idx -= 1
            idx += 1
        if 'codec' in separatePath:
            self.tag = 'codec'
        elif 'vp' in separatePath:
            self.tag = 'vp'
        elif 'cp' in separatePath:
            self.tag = 'cp'
        elif 'os' in separatePath:
            self.tag = 'os'
        else:
            self.tag = 'shared'
            return 'shared not supported currently!'
        cmakeFile = self.ultPath + 'windows\\test\\' + self.tag + '\\ult_srcs.cmake'
        if not os.path.exists(cmakeFile):
            return 'missing cmake file. Platform not supported!'
        with open(cmakeFile, 'r') as fopen:
            lines = fopen.readlines()
        found = False
        insertIndex = -1
        subdirectory = 'ult_include_subdirectory(../../../' + '/'.join(separatePath[:4]) + ')'
        for idx, line in enumerate(lines):
            if line.find('ult_include_subdirectory') >= 0:
                insertIndex = idx
            if line.find(subdirectory) >= 0:
                found = True
        if not found:
            lines.insert(insertIndex + 1, subdirectory + '\n')
        with open(cmakeFile, 'w') as fopen:
            fopen.writelines(lines)
        self.workspace = self.ultPath + 'windows\\test\\' + self.tag + '\\test_data'
        self.xmlPath = self.ultPath + 'test_data\\' + separatePath[0] + '\\' + '\\'.join(separatePath[2:])
        self.referencePath = '../../../../' + 'test_data/' + separatePath[0] + '/' + '/'.join(separatePath[2:]) + '/' + self.className + '/'
        if not os.path.exists(self.workspace):
            os.makedirs(self.workspace)
            cmakeFile = self.ultPath + 'windows\\test\\' + self.tag + '\\ult_srcs.cmake'
            with open(cmakeFile, 'r') as fopen:
                lines = fopen.readlines()
            for idx, line in enumerate(lines):
                if line.find('ult_include_subdirectory') >= 0:
                    lines.insert(idx, 'ult_include_subdirectory(test_data)\n')
                    break
            for idx, line in enumerate(lines):
                if line.find('target_include_directories(${ULT_LIB_PROJECT_NAME_} BEFORE') >= 0:
                    lines.insert(idx + 1, '    PRIVATE ${CMAKE_CURRENT_LIST_DIR}/test_data\n')
                    break
            with open(cmakeFile, 'w') as fopen:
                fopen.writelines(lines)
            self.generateCmake('resource', self.workspace)
        self.codePath = self.ultPath + '\\'.join(separatePath[:4])
        midPath = separatePath[4:]
        if not os.path.exists(self.codePath):
            os.makedirs(self.codePath)
        while midPath:
            if not os.path.exists(self.codePath + '\\ult_srcs.cmake'):
                self.generateCmake('', self.codePath)
            if not os.path.exists(self.codePath + '\\' + midPath[0]):
                self.generateCmake(midPath[0], self.codePath)
                os.mkdir(self.codePath + '\\' + midPath[0])
            self.codePath = self.codePath + '\\' + midPath[0]
            del midPath[0]
        source = separatePath[:3]
        if 'encode' in separatePath:
            source.append('encode')
        elif 'decode' in separatePath:
            source.append('decode')
        elif len(separatePath) > 4:
            source.append(separatePath[4])
        self.generateCmake('code', self.codePath, '\\\\'.join(source[1:]))
        return ''

    def isEnumType(self, type):
        if type in self.typeDic:
            return 0
        for enumItem in self.parser.enum:
            if enumItem[0] == type:
                return 1
        print('WARNING: Cannot find enum type = ' + type + '.')
        return 1

    # append if exists
    def generateTestDataH(self, update = False):
        file = os.path.join(self.codePath, self.sourceFile[:-2] + '_test_data.h')
        removeHead, removeTail = -1, -1
        if self.parser.namespace:
            indent = self.TAB_SPACE
        else:
            indent = 0
        if not update:
            lines = []
            lines.extend(self.getHeaders(type = 'h', fileName = self.sourceFile[:-2] + '_test_data.h'))
            define = '__' + (self.sourceFile[:-2] + '_test_data_h').upper() + '__'
            lines.append('#ifndef ' + define + '\n')
            lines.append('#define ' + define + '\n')
            lines.append('#include "read_test_data_xml.h"\n')
            if self.parser.namespace:
                lines.append('namespace ' + self.parser.namespace + '\n')
                lines.append('{\n')
            if self.parser.namespace:
                lines.append('}\n')
            lines.append('#endif\n')
        else:
            with open(file,'r') as fout:
                lines = fout.readlines()
            for line_idx, line in enumerate(lines):
                if line.find('class ' + self.className + '_' + self.functionName) >= 0:
                    removeHead = line_idx - 1
                    break
            if removeHead >= 0:
                for line_idx in range(removeHead + 1, len(lines)):
                    if lines[line_idx].find('};') >= 0:
                        removeTail = line_idx
                        break

        insertLines = []
        insertLines.append('\n')
        insertLines.append(' ' * indent + 'class ' + self.className + '_' + self.functionName + '_TestData : public TestDataXml\n')
        insertLines.append(' ' * indent + '{\n')
        insertLines.append(' ' * indent + 'public:\n')
        indent += self.TAB_SPACE
        insertLines.append(' ' * indent + self.className + '_' + self.functionName + '_TestData(uint32_t inputRcId, std::string &testName)\n')
        insertLines.append(' ' * indent + '{\n')
        indent += self.TAB_SPACE
        insertLines.append(' ' * indent + 'm_readTestData = MOS_New(ReadTestDataFromXml, inputRcId);\n')
        indent -= self.TAB_SPACE
        insertLines.append(' ' * indent + '}\n')
        insertLines.append('\n')
        insertLines.append(' ' * indent + 'virtual ~ ' + self.className + '_' + self.functionName + '_TestData()\n')
        insertLines.append(' ' * indent + '{\n')
        indent += self.TAB_SPACE
        insertLines.append(' ' * indent + 'MOS_Delete(m_readTestData);\n')
        indent -= self.TAB_SPACE
        insertLines.append(' ' * indent + '}\n')
        insertLines.append('\n')
        insertLines.append(' ' * indent + 'MOS_STATUS m_returnValue = MOS_STATUS_SUCCESS;\n')  #m_readTestData->GetInputParams("returnValue", "returnValue", 0);\n')
        insertLines.append('\n')
        insertLines.append(' ' * indent + 'struct _inputParameters\n')
        insertLines.append(' ' * indent + '{\n')
        indent += self.TAB_SPACE
        for item in self.inputPara:
            insertLines.append(' ' * indent + item + ';\n')
        indent -= self.TAB_SPACE
        insertLines.append(' ' * indent + '} inputParameters;\n')
        insertLines.append('\n')
        insertLines.append(' ' * indent + 'struct _outputParameters\n')
        insertLines.append(' ' * indent + '{\n')
        indent += self.TAB_SPACE
        for item in self.outputPara:
            insertLines.append(' ' * indent + item + ';\n')
        indent -= self.TAB_SPACE
        insertLines.append(' ' * indent + '} outputParameters;\n')
        insertLines.append('\n')
        insertLines.append(' ' * indent + 'void SetInput(std::string &caseName)\n')
        insertLines.append(' ' * indent + '{\n')
        indent += self.TAB_SPACE
        for index, item in enumerate(self.inputName):
            if self.inputType[index].find('vector') >= 0:
                insertLines.append(' ' * indent + 'uint32_t count = (uint32_t)m_readTestData->GetInputParams<int>(caseName, "Input", "' + item + '_count", 0);\n')
                insertLines.append(' ' * indent + 'for (uint32_t i = 0; i < count; i++)\n')
                insertLines.append(' ' * indent + '{\n')
                indent += self.TAB_SPACE
                type = self.getVectorType(self.outputPara[index])
                if type == 'bool':
                    insertLines.append(' ' * indent + '.push_back(CustomStringConverter::Str2Bool(inputParameters.' + item + ', m_readTestData->GetInputParams<std::string>(caseName, "Input", "' + item + '", 0));\n')
                elif self.isEnumType(type):
                    type = 'std::string'
                    insertLines.append(' ' * indent + '.push_back(CustomStringConverter::Str2Enum(' + 'inputParameters.' + item + ', m_readTestData->GetInputParams<std::string>(caseName, "Input", "' + item + '_"+std::to_string(i), ' + self.getDefaultValue(self.getVectorType(self.inputPara[index])) + '))); \n')
                else:
                    type, castType = self.getCastType(type)
                    insertLines.append(' ' * indent + 'inputParameters.' + item + '.push_back(' + castType + 'm_readTestData->GetInputParams<' + type +'>(caseName, "Input", "' + item + '_"+std::to_string(i+1), ' + self.getDefaultValue(self.getVectorType(self.inputPara[index])) + ')); \n')
                indent -= self.TAB_SPACE
                insertLines.append(' ' * indent + '}\n')
            else:
                type = self.inputType[index]
                if type == 'bool':
                    insertLines.append(' ' * indent + 'CustomStringConverter::Str2Bool(inputParameters.' + item + ', m_readTestData->GetInputParams<std::string>(caseName, "Input", "' + item + '", 0));\n')
                elif self.isEnumType(type):
                    type = 'std::string'
                    insertLines.append(' ' * indent + 'CustomStringConverter::Str2Enum(inputParameters.' + item + ', m_readTestData->GetInputParams<' + type + '>(caseName, "Input", "' + item + '", ' + self.getDefaultValue(self.inputType[index]) + '));\n')
                else:
                    type, castType = self.getCastType(type)
                    insertLines.append(' ' * indent + 'inputParameters.' + item + ' = ' + castType + 'm_readTestData->GetInputParams<' + type + '>(caseName, "Input", "' + item + '", ' + self.getDefaultValue(self.inputType[index]) + ');\n')
        indent -= self.TAB_SPACE
        insertLines.append(' ' * indent + '}\n')
        insertLines.append('\n')
        insertLines.append(' ' * indent + 'void SetOutputReference(std::string &caseName)\n')
        insertLines.append(' ' * indent + '{\n')
        indent += self.TAB_SPACE
        insertLines.append(' ' * indent + 'CustomStringConverter::Str2Enum(m_returnValue, m_readTestData->GetInputParams<string>(caseName, "ReturnValue", "returnValue", ""));\n')
        for index, item in enumerate(self.outputName):
            if self.outputType[index].find('vector') >= 0:
                insertLines.append(' ' * indent + 'uint32_t count = (uint32_t)m_readTestData->GetInputParams<int>(caseName, "Output", "' + item + '_count", 0);\n')
                insertLines.append(' ' * indent + 'for (uint32_t i = 0; i < count; i++)\n')
                insertLines.append(' ' * indent + '{\n')
                indent += self.TAB_SPACE
                type = self.getVectorType(self.outputPara[index])
                if type == 'bool':
                    insertLines.append(' ' * indent + '.push_back(CustomStringConverter::Str2Bool(outputParameters.' + item + ', m_readTestData->GetInputParams<std::string>(caseName, "Output", "' + item + '", 0));\n')
                elif self.isEnumType(type):
                    type = 'std::string'
                    insertLines.append(' ' * indent + '.push_back(CustomStringConverter::Str2Enum(' + 'outputParameters.' + item + ', m_readTestData->GetInputParams<std::string>(caseName, "Output", "' + item + '_"+std::to_string(i), ' + self.getDefaultValue(self.getVectorType(self.outputPara[index])) + '))); \n')
                else:
                    type, castType = self.getCastType(type)
                    insertLines.append(' ' * indent + 'outputParameters.' + item + '.push_back(' + castType + 'm_readTestData->GetInputParams<' + type + '>(caseName, "Output", "' + item + '_"+std::to_string(i+1), ' + self.getDefaultValue(self.getVectorType(self.outputPara[index])) + ')); \n')
                indent -= self.TAB_SPACE
                insertLines.append(' ' * indent + '}\n')
            else:
                type = self.outputType[index]
                if type == 'bool':
                    insertLines.append(' ' * indent + 'CustomStringConverter::Str2Bool(outputParameters.' + item + ', m_readTestData->GetInputParams<std::string>(caseName, "Output", "' + item + '", 0));\n')
                elif self.isEnumType(type):
                    type = 'std::string'
                    insertLines.append(' ' * indent + 'CustomStringConverter::Str2Enum(' + 'outputParameters.' + item + ', m_readTestData->GetInputParams<' + type + '>(caseName, "Output", "' + item + '", ' + self.getDefaultValue(self.outputType[index]) + '));\n')
                else:
                    type, castType = self.getCastType(type)
                    insertLines.append(' ' * indent + 'outputParameters.' + item + ' = ' + castType + 'm_readTestData->GetInputParams<' + type + '>(caseName, "Output", "' + item + '", ' + self.getDefaultValue(self.outputType[index]) + ');\n')
        indent -= self.TAB_SPACE
        insertLines.append(' ' * indent + '}\n')
        indent -= self.TAB_SPACE
        insertLines.append(' ' * indent + '};\n')
        if removeHead >= 0:
            lines = lines[:removeHead] + lines[removeTail+1:]
        if self.parser.namespace:
            lines = lines[:-2] + insertLines + lines[-2:]
        else:
            lines = lines[:-1] + insertLines + lines[-1:]

        with open(file,'w') as fout:
            fout.writelines(lines)
        print('generate ', file)
        self.log += 'generate ' + file + '.\n'

    def getVectorValue(self, values):
        value = values.strip().strip('{').strip('}').split(',')
        value_list = []
        for v in value:
            v = v.strip()
            if v:
                value_list.append(v)
        return value_list

    def getVectorType(self, para, namespace = True):
        type = para[para.find('<') + 1 : para.rfind('>')].strip()
        if not namespace:
            type = type.replace('std::', '')
        return type

    def generateValue(self, type, value):
        if value[0] in ('"', "'"):
            value = value[1:-1]
        return type, value

    def generateXml(self, update = False, append = True):
        path = os.path.join(self.xmlPath, self.className)
        if not os.path.exists(path):
            os.makedirs(path)
        file = os.path.join(path, self.functionName + '.xml')
        if update:
            with open(file, 'r') as fopen:
                lines = fopen.readlines()
        else:
            lines = []
            lines.append('<?xml version="1.0"?>\n')
        # delete old version
        if update and not append:
            deleteHead, deleteTail = -1, -1
            for idx, line in enumerate(lines):
                if line.find('TestCase name') >= 0 and line.find(self.caseName) >= 0:
                    deleteHead = idx
                    break
            if deleteHead < 0:
                print('Update xml error!')
                return
            for idx in range(deleteHead + 1, len(lines)):
                if lines[idx].find('/TestCase') >= 0:
                    deleteTail = idx
                    break
            if deleteTail < 0:
                print('Update xml error!')
                return
            lines = lines[:deleteHead] + lines[deleteTail + 1:]
        indent = 0
        idx = 0
        #has_root = False
        #if len(lines) >= 2 and (lines[0].find('<root>') >= 0 or lines[1].find('<root>') >= 0):
        #    has_root = True
        #    del lines[-1]
        #while idx < len(lines):
        #    if not has_root and indent == 0 and lines[idx].find('TestCase name') >= 0:
        #        lines.insert(idx, '<root>\n')
        #        indent = 4
        #        has_root = True
        #    else:
        #        lines[idx] = ' ' * indent + lines[idx]
        #    idx += 1
        #if has_root:
        #    indent = 4
        lines.append(' ' * indent + '<TestCase name = "' + self.caseName + '">\n')
        lines.append(' ' * indent + '    <Input>\n')
        for i in range(len(self.inputPara)):
            if self.inputType[i].find('vector') >= 0:
                VectorType = self.getVectorType(self.inputPara[i], False)
                values = self.getVectorValue(self.inputValue[i])
                lines.append(' ' * indent + '        <' + self.inputName[i] + '_count type = "int" value = "' + str(len(values)) + '"/>\n')
                for idx, value in enumerate(values):
                    type, value = self.generateValue(VectorType, value)
                    lines.append(' ' * indent + '        <' + self.inputName[i] + '_' + str(idx) + ' type = "' + type + '" value = "' + value + '"/>\n')
            else:
                type, value = self.generateValue(self.inputType[i], self.inputValue[i])
                lines.append(' ' * indent + '        <' + self.inputName[i] + ' type = "' + type + '" value = "' + value + '"/>\n')
        lines.append(' ' * indent + '    </Input>\n')
        lines.append(' ' * indent + '    <ReturnValue>\n')
        lines.append(' ' * indent + '        <returnValue type = "MOS_STATUS" value = "MOS_STATUS_SUCCESS"/>\n')
        lines.append(' ' * indent + '    </ReturnValue>\n')
        lines.append(' ' * indent + '    <Output>\n')
        for i in range(len(self.outputPara)):
            if self.outputType[i].find('vector') >= 0:
                VectorType = self.getVectorType(self.outputPara[i], False)
                values = self.getVectorValue(self.outputValue[i])
                lines.append(' ' * indent + '        <' + self.outputName[i] + '_count type = "int" value = "' + str(len(values)) + '"/>\n')
                for idx, value in enumerate(values):
                    type, value = self.generateValue(VectorType, value)
                    lines.append(' ' * indent + '        <' + self.outputName[i] + '_' + str(idx) + ' type = "' + type + '" value = "' + value + '"/>\n')
            else:
                type, value = self.generateValue(self.outputType[i], self.outputValue[i])
                lines.append(' ' * indent + '        <' + self.outputName[i] + ' type = "' + type + '" value = "' + value + '"/>\n')
        lines.append(' ' * indent + '    </Output>\n')
        lines.append(' ' * indent + '</TestCase>\n')
        #if has_root:
        #    lines.append('</root>\n')
        with open(file, 'w', encoding='UTF-8') as fopen:
            fopen.writelines(lines)
        print('generate ', file)
        self.log += 'generate ' + file + '.\n'
        self.xmlFile = file

    def getCastType(self, type):
        castType = ''
        if 'uint' in type:
            castType = '(' + type + ')'
            type = 'int'
        return type, castType


    def generateTestCaseCpp(self, update = False):
        file = os.path.join(self.codePath, self.sourceFile[:-2] + '_test_case.cpp')
        if self.parser.namespace:
            indent = self.TAB_SPACE
        else:
            indent = 0
        if not update:
            lines = []
            lines.extend(self.getHeaders(type = 'cpp', fileName = self.sourceFile[:-2] + '_test_case.cpp'))
            lines.append('#include "' + self.sourceFile[:-2] + '_test_case.h"\n')
            resourcePath = 'resource.h'
            lines.append('#include "' + resourcePath + '"\n')
            if self.parser.namespace:
                lines.append('namespace ' + self.parser.namespace +'\n')
                lines.append('{\n')
                lines.append('}\n')
        else:
            with open(file) as fopen:
                lines = fopen.readlines()
        newLines = []
        newLines.append(' ' * indent + 'TEST_F(' + self.className + 'FT, ' + self.className + 'Test_' + self.functionName + ')\n')
        newLines.append(' ' * indent + '{\n')
        indent += self.TAB_SPACE
        newLines.append(' ' * indent + 'std::string testName = ::testing::UnitTest::GetInstance()->current_test_info()->name();\n')
        newLines.append(' ' * indent + self.className + '_' + self.functionName + '_TestData testData(' + self.className + '_' + self.functionName + ', testName);\n')
        newLines.append(' ' * indent + 'std::vector<std::string> testNameMap = testData.m_readTestData->GetTestName();\n')
        newLines.append(' ' * indent + 'for (size_t i = 0; i < testNameMap.size(); i++)\n')
        newLines.append(' ' * indent + '{\n')
        indent += self.TAB_SPACE
        newLines.append(' ' * indent + 'testData.SetInput(testNameMap[i]);\n')
        newLines.append(' ' * indent + 'testData.SetOutputReference(testNameMap[i]);\n')
        newLines.append(' ' * indent + 'EXPECT_EQ(m_test->' + self.functionName + 'Test(testData), 0);\n')
        indent -= self.TAB_SPACE
        newLines.append(' ' * indent + '}\n')
        indent -= self.TAB_SPACE
        newLines.append(' ' * indent + '}\n')
        if self.parser.namespace:
            lines = lines[:-1] + newLines + lines[-1:]
        else:
            lines.extend(newLines)
        with open(file,'w') as fout:
            fout.writelines(lines)
        print('generate ', file)
        self.log += 'generate ' + file + '.\n'

    def getDefaultValue(self, para):
        if para in self.typeDic:
            return self.typeDic[para]
        else:
            # enum type
            return '0'

    def generateTestCaseH(self, update = False):
        file = os.path.join(self.codePath, self.sourceFile[:-2] + '_test_case.h')
        if self.parser.namespace:
            indent = self.TAB_SPACE
        else:
            indent = 0
        if not update:
            lines = []
            lines.extend(self.getHeaders(type = 'h', fileName = self.sourceFile[:-2] + '_test_case.h'))
            define = '__' + (self.sourceFile[:-2] + '_test_case_h').upper() + '__'
            lines.append('#ifndef ' + define + '\n')
            lines.append('#define ' + define + '\n')
            lines.append('#include "gtest/gtest.h"\n')
            lines.append('#include "gmock/gmock.h"\n')
            lines.append('#include "' + self.sourceFile[:-2] + '_test.h"\n')
            lines.append('using namespace testing;\n')
            if self.parser.namespace:
                lines.append('namespace ' + self.parser.namespace + '\n')
                lines.append('{\n')
                lines.append('}\n')
            lines.append('#endif\n')
        else:
            with open(file, 'r') as fopen:
                lines = fopen.readlines()
        newLines = []
        newLines.append(' ' * indent + 'class ' + self.className + 'FT : public ' + self.TestBaseClass + '\n')
        newLines.append(' ' * indent + '{\n')
        newLines.append(' ' * indent + 'protected:\n')
        indent += self.TAB_SPACE
        newLines.append(' ' * indent + '//!\n')
        newLines.append(' ' * indent + '//! \\brief   Initialization work before executing a unit test\n')
        newLines.append(' ' * indent + '//!\n')
        newLines.append(' ' * indent + 'virtual void SetUp()\n')
        newLines.append(' ' * indent + '{\n')
        indent += self.TAB_SPACE
        if self.TestBaseClass != 'testing::Test':
            newLines.append(' ' * indent + self.TestBaseClass + '::SetUp();\n')
        newLines.append(' ' * indent + 'm_test = MOS_New(' + self.className + 'Test')
        construct_id = self.getMethodIndex(self.className)
        if construct_id >= 0:
            construct = self.parser.methods_info[construct_id]
            for i, para in enumerate(construct['parameters']):
                newLines.append(', ')
                newLines.append(self.getDefaultValue(para['name']))
        newLines.append(');\n')
        indent -= self.TAB_SPACE
        newLines.append(' ' * indent + '}\n')
        newLines.append('\n')
        newLines.append(' ' * indent + '//!\n')
        newLines.append(' ' * indent + '//! \\brief   Uninitializaiton and exception handling after the unit test done\n')
        newLines.append(' ' * indent + '//!\n')
        newLines.append(' ' * indent + 'virtual void TearDown()\n')
        newLines.append(' ' * indent + '{\n')
        indent += self.TAB_SPACE
        if self.TestBaseClass != 'testing::Test':
            newLines.append(' ' * indent + self.TestBaseClass + '::TearDown();\n')
        newLines.append(' ' * indent + 'MOS_Delete(m_test);\n')
        indent -= self.TAB_SPACE
        newLines.append(' ' * indent + '}\n')
        newLines.append(' ' * indent + self.className + 'Test *m_test = nullptr;\n')
        indent -= self.TAB_SPACE
        newLines.append(' ' * indent + '};\n')
        if self.parser.namespace:
            lines = lines[:-2] + newLines + lines[-2:]
        else:
            lines = lines[:-1] + newLines + lines[-1:]
        with open(file,'w') as fout:
            fout.writelines(lines)
        print('generate ', file)
        self.log += 'generate ' + file + '.\n'

    def getMethodIndex(self, name):
        for i, method in enumerate(self.parser.methods_info):
            if method['method_name'] == name:
                return i
        return -1

    def generateTestH(self, update = False, sameClass = False):
        file = os.path.join(self.codePath, self.sourceFile[:-2] + '_test.h')
        if self.parser.namespace:
            indent = self.TAB_SPACE
        else:
            indent = 0
        if not update:
            lines = []
            lines.extend(self.getHeaders(type = 'h', fileName = self.sourceFile[:-2] + '_test.h'))
            lines.append('#include "' + self.sourceFile[:-2] + '_test_data.h"\n')
            lines.append('#include "' + self.sourceFile + '"\n')
            lines.append('\n')
            if self.parser.namespace:
                lines.append('namespace ' + self.parser.namespace +'\n')
                lines.append('{\n')
                lines.append('}\n')
        else:
            with open(file, 'r') as fopen:
                lines = fopen.readlines()
        if sameClass:
            insertLine = ' ' * (indent + self.TAB_SPACE) + 'MOS_STATUS ' + self.functionName + 'Test(' + self.className + '_' + self.functionName + '_TestData &testData);\n'
            for idx, line in enumerate(lines):
                if line.find('class ' + self.className + 'Test : ') >= 0:
                    classIdx = idx
                    break
            for idx in range(classIdx, len(lines)):
                if lines[idx].strip() == '};':
                    insertIdx = idx - 1
                    break
            lines.insert(insertIdx, insertLine)
        else:
            insertLines = []
            insertLines.append(' ' * indent + 'class ' + self.className + 'Test : public ' + self.className + '\n')
            insertLines.append(' ' * indent + '{\n')
            insertLines.append(' ' * indent + 'public:\n')
            indent += self.TAB_SPACE
            construct_id = self.getMethodIndex(self.className)
            if construct_id < 0:
                print('ERROR: no construct function')
            else:
                insertLines.append(' ' * indent + self.className + 'Test(')
                construct = self.parser.methods_info[construct_id]
                for i, para in enumerate(construct['parameters']):
                    insertLines.append(para['type'] + ' ' + para['name'])
                    if i != len(construct['parameters']) - 1:
                        insertLines.append(' ,')
                insertLines.append(') : ' + self.className + '(')
                for i, para in enumerate(construct['parameters']):
                    insertLines.append(para['name'].lstrip('*').lstrip('&'))
                    if i != len(construct['parameters']) - 1:
                        insertLines.append(' ,')
                insertLines.append('){};\n')
            insertLines.append(' ' * indent + 'virtual ~' + self.className + 'Test(){};\n')
            insertLines.append('\n')
            insertLines.append(' ' * indent + '//!\n')
            insertLines.append(' ' * indent + '//! \\brief  Add focus test for ActivateVdencVideoPackets\n')
            insertLines.append(' ' * indent + '//! \\param  [in] &testData\n')
            insertLines.append(' ' * indent + '//!         reference to TestData\n')
            insertLines.append(' ' * indent + '//! \\return MOS_STATUS\n')
            insertLines.append(' ' * indent + '//!         MOS_STATUS_SUCCESS if success, else fail reason\n')
            insertLines.append(' ' * indent + '//!\n')
            insertLines.append(' ' * indent + 'MOS_STATUS '+ self.functionName + 'Test(' + self.className + '_' + self.functionName + '_TestData &testData);\n')
            indent -= self.TAB_SPACE
            insertLines.append(' ' * indent + '};\n')
            if self.parser.namespace:
                lines = lines[:-1] + insertLines + lines[-1:]
            else:
                lines.extend(insertLines)
        with open(file,'w') as fout:
            fout.writelines(lines)
        print('generate ', file)
        self.log += 'generate ' + file + '.\n'

    def generateTestCpp(self, update = False):
        file = os.path.join(self.codePath, self.sourceFile[:-2] + '_test.cpp')
        if self.parser.namespace:
            indent = self.TAB_SPACE
        else:
            indent = 0
        if not update:
            lines = []
            lines.extend(self.getHeaders(type = 'cpp', fileName = self.sourceFile[:-2] + '_test.cpp'))
            lines.append('#include "' + self.sourceFile[:-2] + '_test.h"\n')
            lines.append('\n')
            if self.parser.namespace:
                lines.append('namespace ' + self.parser.namespace + '\n')
                lines.append('{\n')
                lines.append('}\n')
        else:
            with open(file, 'r') as fopen:
                lines = fopen.readlines()
        insertLines = []
        insertLines.append(' ' * indent + 'MOS_STATUS ' + self.className + 'Test::' + self.functionName + 'Test(' + self.className + '_' + self.functionName + '_TestData &testData)\n')
        insertLines.append(' ' * indent + '{\n')
        indent += self.TAB_SPACE
        insertLines.append(' ' * indent + '//RunTest\n')
        insertLines.append(' ' * indent + '//EXPECT_EQ(' + self.functionName + '(), testData.m_returnValue);\n')
        insertLines.append(' ' * indent + 'return MOS_STATUS_SUCCESS;\n')
        indent -= self.TAB_SPACE
        insertLines.append(' ' * indent + '}\n')
        if self.parser.namespace:
            lines = lines[:-1] + insertLines + lines[-1:]
        else:
            lines.extend(insertLines)
        with open(file,'w') as fout:
            fout.writelines(lines)
        print('generate ', file)
        self.log += 'generate ' + file + '.\n'

    def checkCMake(self):
        path = self.workspace[:self.workspace.rfind('\\')]
        file = os.path.join(path, 'ult_srcs.cmake')
        with open(file, 'r') as fopen:
            lines = fopen.readlines()
        insertIndex = 0
        line = 'PRIVATE ${CMAKE_CURRENT_LIST_DIR}/test_data'
        for idx, line in enumerate(lines):
            if line.find(line) >= 0:
                return
            if line.find('PRIVATE ${') >= 0:
                insertIndex = idx
        lines.insert(insertIndex + 1, '        ' + line + '\n')
        with open(file, 'w') as fopen:
            fopen.writelines(lines)

    def generateResourceH(self):
        self.checkCMake()
        file = os.path.join(self.workspace, 'resource.h')
        resource = self.className + '_' + self.functionName
        insertLine = '#define ' + resource + ' ' * (self.BLANK_NUM - len(resource))
        if os.path.exists(file):
            with open(file, 'r') as fopen:
                lines = fopen.readlines()
            for i in reversed(range(len(lines))):
                line_str = lines[i].strip()
                if line_str:
                    insertLine += str(int(line_str.split()[-1]) + 1) + '\n'
                    break
        else:
            insertLine += '100\n'
            lines = []
        lines.append(insertLine)
        with open(file, 'w') as fopen:
            fopen.writelines(lines)
        print('generate ', file)
        self.log += 'generate ' + file + '.\n'
        return ''

    def generateUltRc(self):
        file = os.path.join(self.workspace, 'media_driver_' + self.tag +'_ult.rc')
        if not os.path.exists(file):
            with open(file, 'w') as fopen:
                fopen.write('#include "resource.h"\n')
        with open(file, 'a') as fopen:
            resource = self.className + '_' + self.functionName
            fopen.write(resource + ' ' * (self.BLANK_NUM - len(resource)) + 'TEST_DATA     "' + self.referencePath + self.functionName + '.xml"\n')
        print('generate ', file)
        self.log += 'generate ' + file + '.\n'


    def getHeaders(self, type, fileName = ''):
        if type == 'cmake':
            lines = []
            lines.append('# Copyright (c) 2020 - 2021, Intel Corporation\n')
            lines.append('#\n')
            lines.append('# Permission is hereby granted, free of charge, to any person obtaining a\n')
            lines.append('# copy of this software and associated documentation files (the "Software"),\n')
            lines.append('# to deal in the Software without restriction, including without limitation\n')
            lines.append('# the rights to use, copy, modify, merge, publish, distribute, sublicense,\n')
            lines.append('# and/or sell copies of the Software, and to permit persons to whom the\n')
            lines.append('# Software is furnished to do so, subject to the following conditions:\n')
            lines.append('#\n')
            lines.append('# The above copyright notice and this permission notice shall be included\n')
            lines.append('# in all copies or substantial portions of the Software.\n')
            lines.append('#\n')
            lines.append('# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS\n')
            lines.append('# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,\n')
            lines.append('# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL\n')
            lines.append('# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR\n')
            lines.append('# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,\n')
            lines.append('# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR\n')
            lines.append('# OTHER DEALINGS IN THE SOFTWARE.\n')
            lines.append('\n')
            return lines
        else:
            lines = []
            lines.append('/*===================== begin_copyright_notice ==================================\n')
            lines.append('\n')
            lines.append('INTEL CONFIDENTIAL\n')
            lines.append('Copyright 2020\n')
            lines.append('Intel Corporation All Rights Reserved.\n')
            lines.append('\n')
            lines.append('The source code contained or described herein and all documents related to the\n')
            lines.append('source code ("Material") are owned by Intel Corporation or its suppliers or\n')
            lines.append('licensors. Title to the Material remains with Intel Corporation or its suppliers\n')
            lines.append('and licensors. The Material contains trade secrets and proprietary and confidential\n')
            lines.append('information of Intel or its suppliers and licensors. The Material is protected by\n')
            lines.append('worldwide copyright and trade secret laws and treaty provisions. No part of the\n')
            lines.append('Material may be used, copied, reproduced, modified, published, uploaded, posted,\n')
            lines.append("transmitted, distributed, or disclosed in any way without Intel's prior express\n")
            lines.append('written permission.\n')
            lines.append('\n')
            lines.append('No license under any patent, copyright, trade secret or other intellectual\n')
            lines.append('property right is granted to or conferred upon you by disclosure or delivery\n')
            lines.append('of the Materials, either expressly, by implication, inducement, estoppel\n')
            lines.append('or otherwise. Any license under such intellectual property rights must be\n')
            lines.append('express and approved by Intel in writing.\n')
            lines.append('\n')
            lines.append('======================= end_copyright_notice ==================================*/\n')
            lines.append('//!\n')
            lines.append('//! \\file     ' + fileName + '\n')
            if type == 'h':
                lines.append('//! \\brief    header file of ' + self.className + ' class\n')
            else:
                lines.append('//! \\brief    implementation file of ' + self.className + ' class\n')
            lines.append('//! \\details\n')
            lines.append('//!\n')
            return lines