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
    def __init__(self, string, libs):
        self.string = string
        self.libs = "\n".join(["#include <" + lib + ">" for lib in libs])

    def __str__(self):
        return self.string

    def get_vars(self, t_index, var_index):
        pass

    def get_test(self, output):
        pass

    def get_out(self):
        pass

test_types = {}

# ================ IS_[NOT_]_EQ_[U]INT[Ø,8,16,32,64] =================

class TestInt(Test):
    def __init__(self, string, libs, _int_type, _compare, _print_int_type):
        Test.__init__(self, string, libs)
        self.int_type = _int_type
        self.compare = _compare
        self.print_int_type = _print_int_type

    def get_vars(self, t_index, var_index):
        self.var = "tFuncOutT%dV%d" % (t_index, var_index)
        return "%s %s;" % (self.int_type, self.var), var_index + 1

    def get_test(self, output):
        return "(%s %s %s)" % (output, self.compare, self.var)

    def get_out(self):
        return '"%%%s\\n", %s' % (self.print_int_type, self.var)


for int_bits in ["", "8", "16", "32", "64"]:
    for is_unsigned in [0, 1]:
        for is_not_eq in [0, 1]:
            int_type = "int"

            int_type += (int_bits + "_t") if (int_bits != "") else ""

            int_type = ("unsigned " if ("" == int_bits) else "u") + int_type

            comp = "!=" if is_not_eq else "=="

            print_int_type = "u" if is_unsigned else "d"

            if int_bits != "":
                print_int_type = "\" PRI" + print_int_type + int_bits + " \""

            _is_eq_int = TestInt("IS_%sEQ_%sINT%s" % (
                "NOT_" if is_not_eq else "",
                "U" if is_unsigned else "", int_bits),
                ["inttypes.h", "stdlib.h"],
                int_type,
                comp,
                print_int_type)
            test_types[str(_is_eq_int)] = _is_eq_int

            print_int_type = None
            _is_eq_int = None
            int_type = None

int_bits = None
is_unsigned = None
is_not_eq = None


# ============== IS_[NOT_]_EQ_STR ================
class TestStr(Test):
    def __init__(self, string, libs, compare):
        Test.__init__(self, string, libs)
        self.compare = compare

    def get_vars(self, t_index, var_index):
        self.var = "tFuncOutT%dV%d" % (t_index, var_index)
        return "char *%s;" % self.var, var_index + 1

    def get_test(self, output):
        return "(0 %s strcmp(%s, %s))" % (self.compare, output, self.var)

    def get_out(self):
        return '"%%s\\n", %s' % self.var


for is_not_eq in [0,1]:
    _is_eq_int = TestStr("IS_%sEQ_STR" % ("NOT_" if is_not_eq else ""),
                         ["string.h"],
                         "!=" if is_not_eq else "==")
    test_types[str(_is_eq_int)] = _is_eq_int
    _is_eq_int = None

is_not_eq = None


def generate_test_code(conf, file, tests, includes):
    code = """
  FILE *f = fopen("%s","wt");
  if (NULL == f)
    return 1488;\n""" % ("./" + conf["test_result_file_prefix"] + file['name'])

    variables = ""

    t_index = 0
    var_index = 0

    for test in tests:
        t_type = test_types.get(test['type'], None)
        if None is t_type:
            continue

        var_index = 0

        _var_init, var_index = t_type.get_vars(t_index, var_index)
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

        t_index += 1

    includes.append("stdio.h")

    return "\n\n/* === TESTED === */\n" +\
           "\n".join(["#include <" + lib + ">" for lib in includes]) +\
           "\n\nint main(void) {\n" +\
           "/* Variables */" + \
           variables +\
           "/* Tests */" + \
           code +\
           "\n  fclose(f);\n  return 0;\n}"


