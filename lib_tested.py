#!/usr/bin/env python3
# -*- coding:utf-8 -*-
__author__ = 'ktulhy'

# TODO: убрать дублирование кода
ERROR =         "\x1b[31m[---ERROR--] \x1b[0m"
SYSTEM =        "\x1b[34m[--SYSTEM--] \x1b[0m"
INFO =          "[---INFO---] "
WARNING =       "\x1b[33m[--WARNING-] \x1b[0m"

test_types = []

from lxml import etree


def parse_inp(var):
    attrib = var.attrib
    v_type = attrib.get('type', None)

    text = var.text
    if None is v_type:
        v_type = ""
        typecast = ""
    else:
        typecast = "(" + v_type + ") "

    if "char" in v_type:
        text = '"' + text + '"'
    return typecast + text

def parse_out(var):
    return parse_inp(var)


def parse_file(conf, file):
    includes = []
    test_file = conf['folder'] + "tests/" + conf["test_file_prefix"] + file['name']
    try:
        f = open(test_file)
    except FileNotFoundError:
        print(ERROR + "Test file for '%s' not found , terminate" % file['name'])
        return None, None

    try:
        xml_doc = etree.parse(f)
    except etree.XMLSyntaxError:
        print(ERROR + "Error parsing file '%s', terminate" % file['name'])
        return None, None

    xml_root = xml_doc.getroot()

    xml_libraries = xml_root.find("libraries")

    if (None != xml_libraries) and (None != xml_libraries.text):
        for lib in xml_libraries.text.split(','):
            includes.append(lib.rstrip().lstrip())

    xml_tests = xml_root.find("tests")

    if None == xml_tests:
        print(WARNING + "Tests for file '%s' not written, please, check test file '%s'" % (file['name'], test_file))
        print(ERROR + "Terminate")
        return None, None

    tests = []

    for test in xml_tests.getiterator("test"):
        t_attrib = test.attrib
        t_type = t_attrib.get('type', None)
        if t_type == 'IS_EQ_INT64':
            pass
        t_func = t_attrib.get('func', None)

        if t_func is None:
            print(WARNING + "In file '%s': Func does not contains, continue" % test_file)
            continue

        if t_type not in test_types:
            print(WARNING + "In file '%s': Test type '%s' is not recognized, continue" % (test_file, t_type))
            continue

        _t_variables = test.find('variables')

        if _t_variables is not None:
            t_variables = _t_variables.text

        if t_variables == None:
            t_variables = ''

        t_input = []

        for inp in test.getiterator("inp"):
            t_input.append(parse_inp(inp))

        _t_output = test.find("out")
        if _t_output is None:
            print(WARNING + "Test for file '%s' has not output" % file['name'])

        t_output = parse_out(_t_output)

        tests.append({"type": t_type, "func": t_func, "variables": t_variables, "input": t_input, "output": t_output})

    return tests, includes


class Test():
    def __init__(self, string, libs, get_vars, get_test, get_out):
        self.string = string
        self.libs = "\n".join(["#include <" + lib + ">" for lib in libs])
        self._get_vars = get_vars
        self._get_test = get_test
        self._get_out = get_out

    def __str__(self):
        return self.string

    def get_vars(self, t_index):
        return self._get_vars(self, t_index)

    def get_test(self, output):
        return self._get_test(self, output)

    def get_out(self):
        return self._get_out(self)

test_types = {}


# ================== IS_EQ_INT ==================
def _get_vars(self, t_index):
    self.var = "tFuncOut%d" % t_index
    return "int %s;" % self.var, t_index + 1


def _get_test(self, output):
    return "(%s == %s)" % (output, self.var)


def _get_out(self):
    return '"%%d\\n", %s' % self.var


IS_EQ_INT = Test("IS_EQ_INT", ["inttypes.h", "stdlib.h"], _get_vars, _get_test, _get_out)
test_types[str(IS_EQ_INT)] = IS_EQ_INT
# ===============================================

# ================== IS_NOT_EQ_INT ==================
def _get_vars(self, t_index):
    self.var = "tFuncOut%d" % t_index
    return "int %s;" % self.var, t_index + 1


def _get_test(self, output):
    return "(%s != %s)" % (output, self.var)


def _get_out(self):
    return '"%%d\\n", %s' % self.var


IS_NOT_EQ_INT = Test("IS_NOT_EQ_INT", ["inttypes.h", "stdlib.h"], _get_vars, _get_test, _get_out)
test_types[str(IS_NOT_EQ_INT)] = IS_NOT_EQ_INT
# ===============================================

# ================== IS_EQ_LONG_INT ==================
def _get_vars(self, t_index):
    self.var = "tFuncOut%d" % t_index
    return "long int %s;" % self.var, t_index + 1


def _get_test(self, output):
    return "(%s == %s)" % (output, self.var)


def _get_out(self):
    return '"%%d\\n", %s' % self.var


IS_EQ_LONG_INT = Test("IS_EQ_LONG_INT", ["inttypes.h", "stdlib.h"], _get_vars, _get_test, _get_out)
test_types[str(IS_EQ_LONG_INT)] = IS_EQ_LONG_INT
# ===============================================

# ================== IS_EQ_INT64 ==================
def _get_vars(self, t_index):
    self.var = "tFuncOut%d" % t_index
    return "int64_t %s;" % self.var, t_index + 1


def _get_test(self, output):
    return "(%s == %s)" % (output, self.var)


def _get_out(self):
    return '"%%\"PRId64\"\\n", %s' % self.var


IS_EQ_INT64 = Test("IS_EQ_INT64", ["inttypes.h", "stdlib.h"], _get_vars, _get_test, _get_out)
test_types[str(IS_EQ_INT64)] = IS_EQ_INT64
# ===============================================

# ================== IS_EQ_STR ==================
def _get_vars(self, t_index):
    self.var = "tFuncOut%d" % t_index
    return "char *%s;" % self.var, t_index + 1


def _get_test(self, output):
    return "(0 == strcmp(%s, %s))" % (output, self.var)


def _get_out(self):
    return '"%%s\\n", %s' % self.var


IS_EQ_STR = Test("IS_EQ_STR", ["string.h"], _get_vars, _get_test, _get_out)
test_types[str(IS_EQ_STR)] = IS_EQ_STR
# ===============================================

# ================== IS_NOT_EQ_STR ==================
def _get_vars(self, t_index):
    self.var = "tFuncOut%d" % t_index
    return "char *%s;" % self.var, t_index + 1


def _get_test(self, output):
    return "(0 != strcmp(%s, %s))" % (output, self.var)


def _get_out(self):
    return '"%%s\\n", %s' % self.var


IS_NOT_EQ_STR = Test("IS_NOT_EQ_STR", ["string.h"], _get_vars, _get_test, _get_out)
test_types[str(IS_NOT_EQ_STR)] = IS_NOT_EQ_STR
# ===============================================



def generate_test_code(conf, file, tests, includes):
    code = """
  FILE *f = fopen("%s","wt");
  if (NULL == f)
    return 1488;\n""" % ("./" + conf["test_result_file_prefix"] + file['name'])

    variables = ""

    t_index = 0

    for test in tests:
        t_type = test_types.get(test['type'], None)
        if None is t_type:
            continue

        _var_init, t_index = t_type.get_vars(t_index)
        var_name = t_type.var

        variables += "  " + test['variables'].rstrip().lstrip().lstrip() + "\n"
        variables += "  " + _var_init + "\n"

        code += """
/* TEST #%d for func '%s'*/
  %s = %s(%s);
  if %s
    fprintf(f,"OK:");
  else
    fprintf(f,"WR:");
  fprintf(f,%s);
  fflush(f);
""" % (t_index, test['func'],
       var_name, test['func'], ", ".join(test['input']),
       t_type.get_test(test['output']),
       t_type.get_out())

    includes.append("stdio.h")

    return "\n\n/* === TESTED === */\n" +\
           "\n".join(["#include <" + lib + ">" for lib in includes]) +\
           "\n\nint main(void) {\n" +\
           variables +\
           code +\
           "\n  fclose(f);\n  return 0;\n}"



