#!/usr/bin/env python3
# -*- coding:utf-8 -*-
__author__ = 'ktulhy'

ERROR =         "\x1b[31m[---ERROR--] \x1b[0m"
SYSTEM =        "\x1b[34m[--SYSTEM--] \x1b[0m"
INFO =          "[---INFO---] "
WARNING =       "\x1b[33m[--WARNING-] \x1b[0m"

conf = {"compiler": "gcc",
        "compiler_flags": "",
        "out_file": "results.html",
        "test_file_prefix": "test_",
        "c_file_prefix": "t_source_",
        "exec_file_prefix": "t_exec_",
        "test_result_file_prefix": "t_result_"}

prg_version = "0.1.3b NOT TESTED"


def config(folder):
    if ("/" != folder[0]) and ("./" != folder[:2]):
        folder = "./" + folder
    if "/" != folder[-1]:
        folder += "/"
    try:
        f = open(folder + "tests/tested.conf", "rt")
    except FileNotFoundError:
        print(SYSTEM + "Config file not found. Used default config.")
    else:
        for line in f.readlines():
            line = line.lstrip()

            if (0 < len(line)) and ('#' != line[0]):
                line = line.split(':')
                conf[str(line[0])] = "".join(line[1:]).rstrip().lstrip()
        f.close()
    conf['compiler_flags'] = [flag.rstrip().lstrip() for flag in conf['compiler_flags'].split(" ")]
    conf['compiler_flags'] = [flag for flag in conf['compiler_flags'] if '' != flag]
    conf['folder'] = folder


def _get_file_name(fullname):
    name_ex = fullname.split("/")[-1]
    name = name_ex.split(".")
    if len(name) > 1:
        return ".".join(name[:-1])
    return name[0]


class TestInfo():
    def __init__(self):
        self.tests_results = []
        self.compile_exit_code = 0
        self.compile_message = b''
        self.program_exit_code = 0
        self.tests = []

    def add_test_result(self, type, output=''):
        self.tests_results.append([type,output])


def combine_test(file, code):
    print(INFO + "Generating test file")
    f_test_c = open(file['.c'], "wt")
    f_c = open(file['source'], "rt")

    for line in f_c.readlines():
        f_test_c.write(line)

    f_c.close()

    f_test_c.write(code)
    f_test_c.close()


def compile_test(info, conf, file):
    print(INFO + "Compiling with '%s'" % conf['compiler'])

    exit_code = 0
    call = [conf['compiler'], '-o%s' % file['exec'], file['.c']]
    if '' != conf['compiler_flags']:
        call += conf['compiler_flags']
    try:
        info.compile_message = subprocess.check_output(call, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        exit_code = e.returncode
        info.compile_message = e.output

    info.compile_message = info.compile_message.decode(encoding='utf-8', errors='strict').replace("\n", "<br>\n")

    info.compile_exit_code = exit_code

    os.remove(file['.c'])

    print(INFO + "Compiling complete with exit code %d" % exit_code)

    return exit_code


def execute_test(info, file):
    print(INFO + "Exec the tests...")
    if not os.path.exists(file['exec']):
        print(ERROR + "Execute file '%s' not found. Terminate." % file['exec'])
        return -1

    exit_code = subprocess.call(["./" + file['exec']])

    info.program_exit_code = exit_code

    print(INFO + "Program complete with exit exit_code %d" % exit_code)

    os.remove(file['exec'])

    if 1488 == exit_code:
        print(ERROR + "Program '%s' couldn't open file for write test results, terminate" % file['exec'])


def combine_results(info, file, tests):
    try:
        f = open(file['result_tests'])
    except FileNotFoundError:
        print(ERROR + "File with the test results of '%s' is not found" % file['source'])
        info.add_test_result(TEST_FILE_FAIL)
        return

    print(INFO + "Processing results...")
    for line in f.readlines():
        if "OK" == line[:2]:
            st = TEST_PASSED
        elif "WR" == line[:2]:
            st = TEST_WRONG
        else:
            st = TEST_UNKNOWN

        info.add_test_result(st, line[3:].rstrip())

    if len(tests) != len(info.tests_results):
        info.add_test_result(TEST_TERMINATE, info.program_exit_code)

    info.tests = tests

    f.close()
    os.remove(file['result_tests'])


import glob
import subprocess
import os
import argparse

from lib_to_html import *
from lib_tested import *


parser = argparse.ArgumentParser(add_help=True, description="Utility for testing C-code v%s" % prg_version )
parser.add_argument('-f', '--folder', action='store', default='./', help="Project location for tests")
args = parser.parse_args()

config(args.folder)

test_results = {}

file_names = glob.glob(conf['folder'] + "*.c")

for filename in file_names:
    print(INFO + "Testing '%s'" % filename)
    file = {'source': filename,
            'folder': conf['folder'],
            'name': _get_file_name(filename)}
    file['.c'] = conf['c_file_prefix'] + file['name'] + ".c"
    file['exec'] = conf['exec_file_prefix'] + file['name']
    file['result_tests'] = conf["test_result_file_prefix"] + file['name']

    tests, includes = parse_file(conf, file)
    if None != tests:
        code = generate_test_code(conf, file, tests, includes)

        info = TestInfo()

        test_results[filename] = info

        combine_test(file, code)

        compile_test(info, conf, file)

        if -1 == execute_test(info, file):
            continue

        combine_results(info, file, tests)

        print(INFO + "Complete.")

print(INFO + "Processing info into '%s'" % conf['out_file'])

html = processing_info_to_html(test_results, conf)

open(conf['out_file'],"wt").write(html)
print(INFO + "Program end. Bye!")