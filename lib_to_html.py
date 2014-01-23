#!/usr/bin/env python3
# -*- coding:utf-8 -*-
__author__ = 'ktulhy'

TEST_UNKNOWN = 0
TEST_PASSED = 1
TEST_WRONG = 2
TEST_FILE_FAIL = 3
TEST_TERMINATE = 4

from time import strftime

def _get_status(st):
    if 0 == st:
        return "<font style='color:yellow'>Unknown</font>"
    elif 1 == st:
        return "<font style='color:green'>Passed</font>"
    elif 2 == st:
        return "<font style='color:red'>Wrong</font>"
    elif 3 == st:
        return "<font style='color:red'>Result file not found</font>"
    elif 4 == st:
        return "<font style='color:red'>Program terminate</font>"

def processing_info_to_html(test_results):
    html = """<html>
<head>
<style type="text/css">
h1,h2,h3,h4,h5,h6,h7 {
margin:0;
padding:0;
}
h1 {
margin-top: 8px;
}
</style>
</head>
<body style='font-family: "Ubuntu Mono";'>
"""
    html += "<h2>Compile time %s</h2>" % strftime("%A, %d.%m.%Y, %H:%M:%S, %Z")
    for file_name, result in sorted(test_results.items()):
        html += "<h1>%s</h1>\n" % file_name + \
                "<h2>Compiling:</h2>\n" + \
                "<b>Exit code:</b> %d<br>\n" % result.compile_exit_code + \
                "<b>Messages:</b><br>\n%s\n" % result.compile_message.replace(" ","&nbsp;") + \
                "<h2>Tests:</h2>\n" + \
                "<b>Exit code:</b> %d<br>\n" % result.program_exit_code
        n_tests = 0
        for test in result.tests:
            func_name = test['func']
            test_type = test['type']
            variables = test['variables']
            waiting_result = test['result']

            status, output = TEST_UNKNOWN, "Ø"
            if len(result.tests_result) > n_tests:
                status, output = result.tests_result[n_tests]

            if TEST_TERMINATE == status:
                output = "Ø"

            html += "<h3>Test #%d</h3>" % n_tests + \
                    "<b>Status:</b> %s<br>\n" % _get_status(status) + \
                    "<b>Type:</b> %s<br>\n" % test_type + \
                    "<b>%s</b>(%s) = %s, wait: %s<br>\n" %(func_name, ",".join(variables), output, waiting_result)

            if TEST_TERMINATE == status:
                html += "<font style='color:red'>Program terminate with exit code %d</font><br>\n" % result.program_exit_code

            n_tests += 1

    html += """
</body>
</html>
"""
    return html