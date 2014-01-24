#!/usr/bin/env python3
# -*- coding:utf-8 -*-
__author__ = 'ktulhy'

test_types = []


class Test():
    def __init__(self, string, libs, func):
        self.string = string
        self.func = func
        self.libs = libs

    def __call__(self, test, num):
        return self.func(self, test, num)

    def __str__(self):
        return self.string


def generator_test_code(conf, file, tests):
    code = """
  FILE *f = fopen("%s","wt");
  if (NULL == f)
    return 1488;\n""" % (conf["test_result_file_prefix"] + file['name'])

    num = 0
    libs_list = []
    for test in tests:
        _code, variable = test['type'](test, num)
        libs_list += test['type'].libs
        code = variable + code + _code
        num += 1
    code += "\n  fclose(f);\n  return 0;\n}"

    code = "\n\n" + "".join(["#include <%s>\n" % lib for lib in set(libs_list)]) + "\nint main(void) {\n" + code

    return code

# ================= IS_EQ_D =================
def _func(self, test, num):
    variables = "  int64_t t%d;\n" % num
    return_code = """
  t%d = %s(%s);
  if (%s == t%d)
    fprintf(f,"OK:");
  else
    fprintf(f,"WR:");
  fprintf(f,"%%" PRId64 "\\n",t%d);
  fflush(f);
""" % (num, test['func'], ",".join(test['variables']), test['result'], num, num)

    return return_code, variables

_libs = ["stdint.h", "inttypes.h", "stdio.h"]

test_types.append(Test("IS_EQ_D", _libs, _func))
# ================= IS_NOT_EQ_D =================
def _func(self, test, num):
    variables = "  int64_t t%d;\n" % num
    return_code = """
  t%d = %s(%s);
  if (%s != t%d)
    fprintf(f,"OK:");
  else
    fprintf(f,"WR:");
  fprintf(f,"%%" PRId64 "\\n",t%d);
  fflush(f);
""" % (num, test['func'], ",".join(test['variables']), test['result'], num, num)

    return return_code, variables

_libs = ["stdint.h", "inttypes.h", "stdio.h"]

test_types.append(Test("IS_NOT_EQ_D", _libs, _func))
# ================= IS_EQ_S =================
def _func(self, test, num):
    variables = "  char *t%d;\n" % num
    return_code = """
  t%d = %s(%s);
  if (0 == strcmp(%s,t%d))
    fprintf(f,"OK:");
  else
    fprintf(f,"WR:");
  fprintf(f,"%%s\\n",t%d);
  fflush(f);
""" % (num, test['func'], ",".join(test['variables']), test['result'], num, num)

    return return_code, variables

_libs = ["string.h", "stdio.h"]

test_types.append(Test("IS_EQ_S", _libs, _func))
# ================= IS_NOT_EQ_S =================
def _func(self, test, num):
    variables = "  char *t%d;\n" % num
    return_code = """
  t%d = %s(%s);
  if (0 != strcmp(%s,t%d))
    fprintf(f,"OK:");
  else
    fprintf(f,"WR:");
  fprintf(f,"%%s\\n",t%d);
  fflush(f);
""" % (num, test['func'], ",".join(test['variables']), test['result'], num, num)

    return return_code, variables

_libs = ["string.h", "stdio.h"]

test_types.append(Test("IS_NOT_EQ_S", _libs, _func))
# =================  =================
# =================  =================
# =================  =================
# =================  =================
# =================  =================
# =================  =================
# =================  =================
# =================  =================
# =================  =================
# =================  =================
# =================  =================
# =================  =================
# =================  =================
_func = None
_libs = None