#!/usr/bin/env python3
# -*- coding:utf-8 -*-
__author__ = 'ktulhy'

test_types = []


class Test():
    def __init__(self,string, func):
        self.string = string
        self.func = func

    def __call__(self, test, num):
        return self.func(self, test, num)

    def __str__(self):
        return self.string


def generator(conf, file, tests):
    code = """
  FILE *f = fopen("%s","wt");
  if (NULL == f)
    return 1488;\n""" % (conf["test_result_file_prefix"] + file['name'])

    num = 0
    for test in tests:
        _code, variable = test['type'](test, num)
        code = variable + code + _code
        num += 1
    code += "\n  fclose(f);\n  return 0;\n}"

    code = """\n\n#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <inttypes.h>
#include <string.h>\n
int main(void) {\n""" + code

    return code

# ================= IS_EQ_D =================
def _func(self, test, num):
    variables = "  int64_t t%d;\n" % num
    str = """
  t%d = %s(%s);
  if (%s == t%d)
    fprintf(f,"OK:");
  else
    fprintf(f,"WR:");
  fprintf(f,"%%" PRId64 "\\n",t%d);
  fflush(f);
""" % (num, test['func'], ",".join(test['variables']), test['result'], num, num)

    return str, variables

test_types.append(Test("IS_EQ_D", _func))
# ================= IS_NOT_EQ_D =================
def _func(self, test, num):
    variables = "  int64_t t%d;\n" % num
    str = """
  t%d = %s(%s);
  if (%s != t%d)
    fprintf(f,"OK:");
  else
    fprintf(f,"WR:");
  fprintf(f,"%%" PRId64 "\\n",t%d);
  fflush(f);
""" % (num, test['func'], ",".join(test['variables']), test['result'], num, num)

    return str, variables

test_types.append(Test("IS_NOT_EQ_D", _func))
# ================= IS_EQ_S =================
def _func(self, test, num):
    variables = "  char *t%d;\n" % num
    str = """
  t%d = %s(%s);
  if (0 == strcmp(%s,t%d))
    fprintf(f,"OK:");
  else
    fprintf(f,"WR:");
  fprintf(f,"%%s\\n",t%d);
  fflush(f);
""" % (num, test['func'], ",".join(test['variables']), test['result'], num, num)

    return str, variables

test_types.append(Test("IS_EQ_S", _func))
# ================= IS_NOT_EQ_S =================
def _func(self, test, num):
    variables = "  char *t%d;\n" % num
    str = """
  t%d = %s(%s);
  if (0 != strcmp(%s,t%d))
    fprintf(f,"OK:");
  else
    fprintf(f,"WR:");
  fprintf(f,"%%s\\n",t%d);
  fflush(f);
""" % (num, test['func'], ",".join(test['variables']), test['result'], num, num)

    return str, variables

test_types.append(Test("IS_NOT_EQ_S", _func))
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
