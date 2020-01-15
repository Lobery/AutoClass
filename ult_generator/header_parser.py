import os
class HeaderParser(object):
    """

    """

    def __init__(self, name, path):
        """

        :param name:
        :param path:
        """
        self.name = name
        self.path = path
        self.lines = []
        self.class_name = ''  # not used
        self.className = []
        self.functions_of_class = {}  # key: class    value: list of method name
        self.methods = []
        self.methods_info = []
        self.constructor = []
        self.destructor = []
        self.includes = set()
        self.namespace = ''
        self.super_class = {}   # key: subclass     value: list of super class
        self.basic_type = {'int', 'bool', 'dword', 'uint8_t', 'uint16_t', 'uint32_t', 'uint64_t', 'char'}
        self.keywords = {'static', 'constexpr', 'const', 'unsigned', '*', '&'}
        self.vars = []
        self.enum = []   # [name, [[type,value]],[type,value]]

    #def print_info(self):
    #    print('--------------' + self.name + '-----------------')
    #    #print(self.path)
    #    print('Class Name:       ' + self.class_name)
    #    print('Namespace:        ' + self.namespace)
    #    print('Super Class:      ' + self.super_class + '\n')
    #    print('Methods Info:')
    #    for i in self.methods_info:
    #        print('\nMethod Name:      ' + i['method_name'])
    #        print('Return Type:      ' + i['return_type'])
    #        for j in i['parameters']:
    #            print('Type: ' + j['type'] + '        Name: ' + j['name'])
    #    print('\nVar Info:\n')
    #    print(self.vars)
    #    for i in self.vars:
    #        print('Type: ' + i['type'] + '        Name: ' + i['name'] + '\n')
    #    print('\n\n')

    def read_file(self, name=None, path=None):
        """

        """
        if name:
            self.name = name
        if path:
            self.path = path

        with open(os.path.join(self.path, self.name), 'r') as fin:
            self.lines = fin.readlines()

    @staticmethod
    def get_namespace(line):
        idx = len('namespace ')
        namespace = line[idx:]
        if namespace and namespace[-1] == '{':
            namespace = namespace[:-1]
        while namespace[-1] == ' ':
            namespace = namespace[:-1]

        return namespace

    @staticmethod
    def get_class(line):
        #key word 'class' has 5 characters
        idx1 = 6
        idx2 = line.find(':')
        super_class = []
        class_name = ''
        if idx2 == -1:
            class_name = line[idx1:].strip()
        else:
            class_name = line[idx1:idx2].strip()
            idx2 = line.find('public') + 7
            super_classes = line[idx2:].strip().split(',')
            for item in super_classes:
                item = item.split(' ')[-1]
                if item.endswith('{'):
                    item = item[:-1].strip()
                super_class.append(item)
        return class_name, super_class

    def parse_method_info(self, lines):
        method_info = {
            'return_type': '',
            'method_name': '',
            'parameters': [],
            'virtual': False,
            'static' : False,
        }
        s = lines[0].strip()

        if len(lines) > 1:
            for i in lines[1:]:
                s = s + ' ' + i.strip()

        if s.startswith('static'):
            method_info['static'] = True
            s = s[7:].strip()

        if s.startswith('virtual'):
            method_info['virtual'] = True
            s = s[8:].strip()

        idx0 = s.find(' ')
        if s[:idx0].find('(') == -1:
            method_info['return_type'] = s[:idx0].strip()
        else:
            method_info['return_type'] = 'Constructor'

        idx1 = s.find('(')
        idx2 = s.find(')')
        if method_info['return_type'] == 'Constructor':
            method_info['method_name'] = s[:idx1].strip()
        else:
            method_info['method_name'] = s[idx0 + 1:idx1].strip()
        s_para = s[idx1 + 1:idx2]
        paras = s_para.split(',')
        for i in paras:
            tmp = i.strip().split(' ')
            tmp = [i for i in tmp if i != '']
            for t in range(len(tmp)):
                if (tmp[t] == '*' or tmp[t] == '&') and t+1 < len(tmp) and tmp[t+1]:
                    tmp[t+1] = tmp[t] + tmp[t+1]
            tmp = list(filter(lambda x: x not in self.keywords, tmp))
            if len(tmp) == 2:
                para = {'type': tmp[0].strip(), 'name': tmp[1].strip()}
                if ((para['type'][-1] == '*') or (para['type'][-1] == '&')):
                    para['name'] = para['type'][-1] + para['name']
                    para['type'] = para['type'][:-1]
                method_info['parameters'].append(para)
        if method_info['method_name'].startswith('*') or method_info['method_name'].startswith('&'):
            method_info['return_type'] = method_info['return_type'] + method_info['method_name'][1:]
            method_info['method_name'] = method_info['method_name'][1:]

        return method_info

    def parse_file_info(self):
        """

        :return:
        """
        if not self.lines:
            print('Please read file first\n')
            return

        f_ignore = False
        method_type = 'private'
        f_method = False
        f_struct = False
        className = None
        f_enum = False

        for line_idx, line in enumerate(self.lines):
            line_clr = line.strip()
            if f_ignore:
                idx = line_clr.find('*/')
                if idx == -1:
                    continue
                else:
                    f_ignore = False
                    line_clr = line_clr[idx+2:]
            if line_clr.find('/*') >= 0:
                f_ignore = True
                continue                   # continue may ignore the content and cause some problem
            if line_clr.find('//') != -1:
                idx = line_clr.find('//')
                line_clr = line_clr[:idx].strip()
            if not line_clr:
                continue
            # lines unfinished
            if line_clr.endswith('\\') and line_idx + 1 < len(self.lines):
                self.lines[line_idx + 1] = line_clr[:-1] + self.lines[line_idx + 1]
                continue
            if line_clr.find('enum') >= 0:
                f_enum = True
                enumName = line_clr.strip('{').strip().split()[-1]
                self.enum.append([enumName,[]])
            if f_enum:
                if line_clr.find('=') >= 0:
                    defines = line_clr.strip(',').strip().split()
                    self.enum[-1][1].append([defines[0], defines[-1]])
                if line_clr.find('}') >= 0:
                    f_enum = False
                continue
            if line_clr.startswith('#ifndef') or line_clr.startswith('#define'):
                continue
            if line_clr.startswith('#include'):
                self.includes.add(line_clr[10:-1])
            if f_method and className:
                self.methods[-1].append(line)
                if line_clr[-1] == ';':
                    self.methods_info.append(self.parse_method_info(self.methods[-1]))
                    self.functions_of_class[className].append(self.methods_info[-1]['method_name'])
                    f_method = False
                #else:
                #   f_method = True
                continue
            if f_struct:
                if line_clr.find('}') != -1:
                    f_struct = False
                continue
            if line_clr.startswith('namespace'):
                self.namespace = self.get_namespace(line_clr)
                continue
            if line_clr.startswith('class'):
                if line_clr.find(';') >= 0:
                    continue
                self.class_name, super_class = self.get_class(line_clr)
                className = self.class_name
                self.super_class[className] = super_class
                self.className.append(className)
                self.functions_of_class[className] = []
                continue
            if line_clr.startswith('struct'):
                if line_clr.find(';') >= 0:
                    continue
                f_struct = True
            if line_clr.startswith('public:'):
                method_type = 'public'
                continue                   # continue may ignore the content and cause some problem
            if line_clr.startswith('protected:'):
                method_type = 'protected'
                continue
            if line_clr.startswith('private:'):
                method_type = 'private'
                continue
            #Todo, add more semantic analysis
            #No '='
            #or has '=':
            #uint32_t x = 256 * sizeof(int32_t)  is not a function
            #void f(s='')  is a function
            if className and not line_clr.startswith('#') and line_clr.find('(') != -1 and (line_clr.find('=') == -1 or (line_clr.find('=') > line_clr.find('('))):
                if line_clr.count(':') == 1:
                        line_clr = line_clr[:line_clr.find(':')] + ';'
                self.methods.append([line_clr])
                if not(line_clr[-1] == ';' or line_clr[-1] == '}'):
                    f_method = True
                else:
                    self.methods_info.append(self.parse_method_info(self.methods[-1]))
                    self.functions_of_class[className].append(self.methods_info[-1]['method_name'])
                continue

            tmp0 = line_clr.split(' ')
            tmp = []
            for t in tmp0:
                if t and t not in self.keywords:
                    tmp.append(t)
            if len(tmp) > 2:
                if tmp[1][-1] == ';':
                    tmp[1] = tmp[1][:-1]
                if tmp[0] in self.basic_type:
                    self.vars.append({'type': tmp[0], 'name': tmp[1]})

