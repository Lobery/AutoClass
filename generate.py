import os
import copy
class ClassContent(object):

    def __init__(self):
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

    def generateCmake(self, type, path, source = ''):
        file = os.path.join(path, 'ult_srcs.cmake')
        if type == '':
            lines = []
            lines.extend(self.getHeaders(type = 'cmake'))
            lines.append('ult_add_curr_to_include_path()\n')
        elif type == 'code':
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
            lines.append('    ${CMAKE_CURRENT_LIST_DIR}/media_driver_codec_ult.rc\n')
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
            lines.append('source_group("Sources" FILES ${TMP_HEADERS_})\n')
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
        ultPath = path[:path.find('media')] + 'media\\media_embargo\\media_driver_next\\ult\\'
        separatePath = path.split('\\')
        separatePath = separatePath[separatePath.index('media_driver_next') + 1: ]
        del separatePath[-1]
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
        cmakeFile = path[:path.find('media')] + 'media\\media_embargo\\media_driver_next\\ult\\windows\\test\\' + self.tag + '\\ult_srcs.cmake'
        if not os.path.exists(cmakeFile):
            return 'missing cmake file. Platform not supported!'
        self.workspace = path[:path.find('media')] + 'media\\media_embargo\\media_driver_next\\ult\\windows\\test\\' + self.tag + '\\test_data'
        if not os.path.exists(self.workspace):
            os.makedirs(self.workspace)
            cmakeFile = path[:path.find('media')] + 'media\\media_embargo\\media_driver_next\\ult\\windows\\test\\' + self.tag + '\\ult_srcs.cmake'
            with open(cmakeFile, 'r') as fopen:
                lines = fopen.readlines()
            for idx, line in enumerate(lines):
                if line.find('ult_include_subdirectory') >= 0:
                    lines.insert(idx, '    ult_include_subdirectory(test_data)\n')
                    break
            with open(cmakeFile, 'w') as fopen:
                fopen.writelines(lines)
            self.generateCmake('resource', self.workspace)
        ultPath = ultPath + '\\'.join(separatePath[:4])
        midPath = separatePath[4:]
        if not os.path.exists(ultPath):
            os.makedirs(ultPath)
        while midPath:
            if not os.path.exists(ultPath + '\\ult_srcs.cmake'):
                self.generateCmake('', ultPath)
            if not os.path.exists(ultPath + '\\' + midPath[0]):
                self.generateCmake(midPath[0], ultPath)
                os.mkdir(ultPath + '\\' + midPath[0])
            ultPath = ultPath + '\\' + midPath[0]
            del midPath[0]
        source = separatePath[:3]
        if 'encode' in separatePath:
            source.append('encode')
        elif 'decode' in separatePath:
            source.append('decode')
        else:
            source.append(separatePath[4])
        self.generateCmake('code', ultPath, '\\\\'.join(source))
        self.codePath = ultPath
        return ''
            
    # append if exists
    def generateTestDataH(self, update = False):
        file = os.path.join(self.codePath, self.sourceFile[:-2] + '_test_data.h')
        removeHead, removeTail = -1, -1
        if self.parser.namespace:
            indent = 3
        else:
            indent = 0
        if not update:
            lines = []
            lines.extend(self.getHeaders(type = 'h', fileName = self.sourceFile[:-2] + '_test_data.h'))
            define = '__' + (self.sourceFile[:-2] + '_test_data_h').upper() + '__'
            lines.append('#ifndef ' + define + '\n')
            lines.append('#define ' + define + '\n')
            lines.append('#include "read_test_data.h"\n')
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
        insertLines.append(' ' * indent + 'class ' + self.className + '_' + self.functionName + '_TestData : public TestData\n')
        insertLines.append(' ' * indent + '{\n')
        insertLines.append(' ' * indent + 'public:\n')
        indent += 3
        insertLines.append(' ' * indent + self.className + '_' + self.functionName + '_TestData(uint32_t inputRcId, std::string &testName)\n')
        insertLines.append(' ' * indent + '{\n')
        indent += 3
        insertLines.append(' ' * indent + 'm_readTestData = MOS_New(ReadTestData, inputRcId, testName);\n')
        indent -= 3
        insertLines.append(' ' * indent + '}\n')
        insertLines.append('\n')
        insertLines.append(' ' * indent + 'int m_returnValue = 0;\n')  #m_readTestData->GetInputParams("returnValue", "returnValue", 0);\n')
        insertLines.append('\n')
        insertLines.append(' ' * indent + 'struct _inputParameters\n')
        insertLines.append(' ' * indent + '{\n')
        indent += 3
        for item in self.inputPara:
            insertLines.append(' ' * indent + item + ';\n')
        indent -= 3
        insertLines.append(' ' * indent + '} inputParameters;\n')
        insertLines.append('\n')
        insertLines.append(' ' * indent + 'struct _outputParameters\n')
        insertLines.append(' ' * indent + '{\n')
        indent += 3
        for item in self.outputPara:
            insertLines.append(' ' * indent + item + ';\n')
        indent -= 3
        insertLines.append(' ' * indent + '} outputParameters;\n')
        insertLines.append('\n')
        insertLines.append(' ' * indent + 'void SetInput(std::string &caseName)\n')
        insertLines.append(' ' * indent + '{\n')
        indent += 3
        for index, item in enumerate(self.inputName):
            if self.inputType[index].find('vector') >= 0:
                insertLines.append(' ' * indent + 'for (uint32_t i = 0; i < m_readTestData->GetInputParams(caseName, "' + item + '_count", 0); i++)\n')
                insertLines.append(' ' * indent + '{\n')
                indent += 3
                insertLines.append(' ' * indent + 'inputParameters.' + item + '.push_back(m_readTestData->GetInputParams(caseName, "' + item + '_"+std::to_string(i), "")); \n')
                indent -= 3
                insertLines.append(' ' * indent + '}\n')
            else:
                insertLines.append(' ' * indent + 'inputParameters.' + item + ' = ' + self.getCastType(self.inputType[index]) + 'm_readTestData->GetInputParams(caseName, "' + item + '", ' + self.getParaValue(self.inputType[index]) + ');\n')
        indent -= 3
        insertLines.append(' ' * indent + '}\n')
        insertLines.append('\n')
        insertLines.append(' ' * indent + 'void SetOutputReference(std::string &caseName)\n')
        insertLines.append(' ' * indent + '{\n')
        indent += 3
        insertLines.append(' ' * indent + 'm_returnValue = m_readTestData->GetInputParams(caseName, "returnValue", 0);\n')
        for index, item in enumerate(self.outputName):
            if self.outputType[index].find('vector') >= 0:
                insertLines.append(' ' * indent + 'for (uint32_t i = 0; i < m_readTestData->GetInputParams(caseName, "' + item + '_count", 0); i++)\n')
                insertLines.append(' ' * indent + '{\n')
                indent += 3
                insertLines.append(' ' * indent + 'outputParameters.' + item + '.push_back(m_readTestData->GetInputParams(caseName, "' + item + '_"+std::to_string(i), "")); \n')
                indent -= 3
                insertLines.append(' ' * indent + '}\n')
            else:
                insertLines.append(' ' * indent + 'outputParameters.' + item + ' = ' + self.getCastType(self.outputType[index]) + 'm_readTestData->GetInputParams(caseName, "' + item + '", ' + self.getParaValue(self.outputType[index]) + ');\n')
        indent -= 3
        insertLines.append(' ' * indent + '}\n')
        indent -= 3
        insertLines.append(' ' * indent + '};\n')
        
        if removeHead >= 0:
            lines = lines[:removeHead] + lines[removeTail + 1:len(lines)-2] + insertLines + lines[len(lines)-2:]
        else:
            lines = lines[:len(lines)-2] + insertLines + lines[len(lines)-2:]

        with open(file,'w') as fout:
            fout.writelines(lines)
        print('generate ', file)

    def changeBool(self, s):
        if s.lower() == 'true':
            return '1'
        if s.lower() == 'false':
            return '0'
        return s

    def generateVector(self, name, value):
        value = value.strip().strip('}').strip('{').strip()
        value = value.split(',')
        value_list = []
        for v in value:
            if v:
                value_list.append(v)
        lines = []
        lines.append(name + '_count = ' + str(len(value_list)) + '\n')
        for idx, value in enumerate(value_list):
            lines.append(name + '_' + str(idx + 1) + ' = ' + self.changeBool(value) + '\n')
        return lines


    def generateDat(self, update = False, append = True):
        path = self.workspace + '\\focus_test\\' + self.className + '\\'
        if not os.path.exists(path):
            os.makedirs(path)
        file = os.path.join(path, self.className + '_' + self.functionName + '.dat')
        if update:
            with open(file, 'r') as fopen:
                lines = fopen.readlines()
        else:
            lines = []
        if update and not append:
            deleteHead, deleteTail = -1, -1
            for idx, line in enumerate(lines):
                if line.find('<' + self.caseName + '>') >= 0:
                    deleteHead = idx
                    break
            for idx in range(deleteHead + 1, len(lines)):
                if lines[idx].find('<') >= 0:
                    deleteTail = idx
                    break
            if deleteTail > 0:
                lines = lines[:deleteHead] + lines[deleteTail:]
            else:
                liens = lines[:deleteHead]

        if lines and lines[-1].strip():
            lines.append('\n')
        lines.append('<' + self.caseName + '>\n')
        lines.append('#Input\n')
        for index in range(len(self.inputName)):
            if self.inputType[index].find('vector') >= 0:
                lines.extend(self.generateVector(self.inputName[index], self.inputValue[index]))
            else:
                lines.append(self.inputName[index] + ' = ' + self.changeBool(self.inputValue[index]) + '\n')
        lines.append('\n')
        lines.append('#ReturnValue\n')
        lines.append('returnValue = ' + self.returnValue + '\n')
        lines.append('\n')
        lines.append('#Output\n')
        for index in range(len(self.outputName)):
            if self.outputType[index].find('vector') >= 0:
                lines.extend(self.generateVector(self.outputName[index], self.outputValue[index]))
            else:
                lines.append(self.outputName[index] + ' = ' + self.changeBool(self.outputValue[index]) + '\n')
        with open(file,'w') as fout:
            fout.writelines(lines)
        print('generate ', file)

    def getCastType(self, type):
        if 'int' in type and type != 'int':
            return '(' + type + ')'
        return ''

    def getParaValue(self, type):
        if 'vector' in type:
            return 'null'
        if any([i in type for i in ['int', 'short', 'long', 'double', 'float', 'size']]):
            return '0'
        elif type == 'float':
            return '2.0'
        elif type == 'char':
            return "''"
        elif type == 'bool':
            return 'false'
        elif type == 'selfDefined':
            return '0'
        else:
            return 'null'


    def generateTestCaseCpp(self, update = False, addCase = False):
        file = os.path.join(self.codePath, self.sourceFile[:-2] + '_test_case.cpp')
        if self.parser.namespace:
            indent = 3
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
                lines.append('}  // namespace encode\n')
        else:
            with open(file) as fopen:
                lines = fopen.readlines()
        if addCase:
            for idx, line in enumerate(lines):
                if line.find('TEST_F(' + self.className + 'FT, ' + self.className + 'Test_' + self.functionName) >= 0:
                    idx += 2
                    while idx < len(lines):
                        if lines[idx].find('}') >= 1:
                            insertIdx = idx
                            break
                        idx += 1
                    newLines = [' ' * indent + '    "' + self.caseName + '",\n']
        else:
            newLines = []
            newLines.append(' ' * indent + 'TEST_F(' + self.className + 'FT, ' + self.className + 'Test_' + self.functionName + ')\n')
            newLines.append(' ' * indent + '{\n')
            indent += 3
            newLines.append(' ' * indent + 'std::string testNameMap[] = {\n')
            newLines.append(' ' * indent + ' "' + self.caseName + '",\n')
            newLines.append(' ' * indent + '};\n')
            newLines.append(' ' * indent + 'std::string testName = ::testing::UnitTest::GetInstance()->current_test_info()->name();\n')
            newLines.append(' ' * indent + self.className + '_' + self.functionName + '_TestData testData(' + self.className + '_' + self.functionName + ', testName);\n')
            newLines.append(' ' * indent + 'for (auto i = 0; i < sizeof(testNameMap) / sizeof(std::string); i++)\n')
            newLines.append(' ' * indent + '{\n')
            newLines.append(' ' * indent + '   testData.SetInput(testNameMap[i]);\n')
            newLines.append(' ' * indent + '   testData.SetOutputReference(testNameMap[i]);\n')
            newLines.append(' ' * indent + '   EXPECT_EQ(m_test->' + self.functionName + 'Test(testData), 0);\n')
            newLines.append(' ' * indent + '}\n')
            indent -= 3
            newLines.append(' ' * indent + '}\n')
            insertIdx = -1
        
        lines = lines[:insertIdx] + newLines + lines[insertIdx:]
        with open(file,'w') as fout:
            fout.writelines(lines)
        print('generate ', file)

    def generateTestCaseH(self, update = False):
        file = os.path.join(self.codePath, self.sourceFile[:-2] + '_test_case.h')
        if self.parser.namespace:
            indent = 3
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
        newLines.append(' ' * indent + 'class ' + self.className + 'FT : public testing::Test\n')
        newLines.append(' ' * indent + '{\n')
        newLines.append(' ' * indent + 'protected:\n')
        indent += 3
        newLines.append(' ' * indent + '//!\n')
        newLines.append(' ' * indent + '//! \\brief   Initialization work before executing a unit test\n')
        newLines.append(' ' * indent + '//!\n')
        newLines.append(' ' * indent + 'virtual void SetUp()\n')
        newLines.append(' ' * indent + '{\n')
        indent += 3
        newLines.append(' ' * indent + 'm_test = MOS_New(' + self.className + 'Test, nullptr, nullptr);\n')
        indent -= 3
        newLines.append(' ' * indent + '}\n')
        newLines.append('\n')
        newLines.append(' ' * indent + '//!\n')
        newLines.append(' ' * indent + '//! \\brief   Uninitializaiton and exception handling after the unit test done\n')
        newLines.append(' ' * indent + '//!\n')
        newLines.append(' ' * indent + 'virtual void TearDown()\n')
        newLines.append(' ' * indent + '{\n')
        indent += 3
        newLines.append(' ' * indent + 'MOS_Delete(m_test);\n')
        indent -= 3
        newLines.append(' ' * indent + '}\n')
        newLines.append(' ' * indent + self.className + 'Test *m_test = nullptr;\n')
        indent -= 3
        newLines.append(' ' * indent + '};\n')
        if self.parser.namespace:
            lines = lines[:-2] + newLines + lines[-2:]
        else:
            lines = lines[:-1] + newLines + lines[-1:]
        with open(file,'w') as fout:
            fout.writelines(lines)
        print('generate ', file)

    def getMethodIndex(self, name):
        for i, method in enumerate(self.parser.methods_info):
            if method['method_name'] == name:
                return i
        return -1

    def generateTestH(self, update = False, sameClass = False):
        file = os.path.join(self.codePath, self.sourceFile[:-2] + '_test.h')
        if self.parser.namespace:
            indent = 3
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
            insertLine = ' ' * (indent + 3) + 'MOS_STATUS ' + self.functionName + 'Test(' + self.className + '_' + self.functionName + '_TestData &testData);\n'
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
            indent += 3
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
            insertLines.append(' ' * indent + 'MOS_STATUS '+ self.functionName + 'Test(' + self.className + '_' + self.functionName + '_TestData &testData);\n')
            indent -= 3
            insertLines.append(' ' * indent + '};\n')
            if self.parser.namespace:
                lines = lines[:-1] + insertLines + lines[-1:]
            else:
                lines.extend(insertLines)
        with open(file,'w') as fout:
            fout.writelines(lines)
        print('generate ', file)

    def generateTestCpp(self, update = False):
        file = os.path.join(self.codePath, self.sourceFile[:-2] + '_test.cpp')
        if self.parser.namespace:
            indent = 3
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
                lines.append('}  // namespace encode\n')
        else:
            with open(file, 'r') as fopen:
                lines = fopen.readlines()
        insertLines = []
        insertLines.append(' ' * indent + 'MOS_STATUS ' + self.className + 'Test::' + self.functionName + 'Test(' + self.className + '_' + self.functionName + '_TestData &testData)\n')
        insertLines.append(' ' * indent + '{\n')
        indent += 3
        insertLines.append(' ' * indent + '//RunTest\n')
        insertLines.append(' ' * indent + '//EXPECT_EQ(' + self.functionName + '(), testData.m_returnValue);\n')
        insertLines.append(' ' * indent + 'return MOS_STATUS_SUCCESS;\n')
        indent -= 3
        insertLines.append(' ' * indent + '}\n')
        if self.parser.namespace:
            lines = lines[:-1] + insertLines + lines[-1:]
        else:
            lines.extend(insertLines)
        with open(file,'w') as fout:
            fout.writelines(lines)
        print('generate ', file)
    
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
        insertLine = '#define ' + resource + ' ' * max(1, 47-len(resource))
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
        return ''

    def generateMediaDriverCodecUlt(self):
        file = os.path.join(self.workspace, 'media_driver_codec_ult.rc')
        if not os.path.exists(file):
            with open(file, 'w') as fopen:
                fopen.write('#include "resource.h"\n')
        with open(file, 'a') as fopen:
            resource = self.className + '_' + self.functionName
            fopen.write(resource + ' ' * max(1, (45 - len(resource))) + 'TEST_DATA     "focus_test/' + self.className + '/' + self.className + '_' + self.functionName + '.dat"\n')
        print('generate ', file)


    def getHeaders(self, type, fileName = ''):
        if type == 'cmake':
            lines = []
            lines.append('# Copyright (c) 2018 - 2019, Intel Corporation\n')
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
            lines.append('Copyright 2019\n')
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
            lines.append('//! \n')
            return lines



