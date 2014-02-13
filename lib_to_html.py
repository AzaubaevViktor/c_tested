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

def processing_info_to_html(test_results, conf):
    html = """<html>
    <head>
        <style type="text/css">
            h1,h2,h3,h4,h5,h6,h7 {
                margin:0;
                padding:0;
            }
            h1 {
                margin-top: 8px;
                margin-bottom: 8px;
            }
            .spoiler {
                background: #DDD;
                border: 1px solid #333;
                height: auto;
                width: 90%;
                padding: 1px 5px;
                margin-bottom: 2px;
            }
            .spoiler a {
                text-decoration: none;
                font-color: blue;
            }
            .spoiler .hidetext {
                border-top: solid 1px black;
            }
        </style>
        <script type="text/javascript">
            function show(id){
                document.getElementById(id).style.display == 'none' ?
                    document.getElementById(id).style.display = '' : document.getElementById(id).style.display = 'none';
            }
        </script>
    </head>
<body style='font-family: "Ubuntu Mono";'>
"""
    html += "<h2>Compile time %s; project \"%s\"</h2>" % (strftime("%A, %d.%m.%Y, %H:%M:%S, %Z"), conf['folder'])

    file_index = 0

    for file_name, result in sorted(test_results.items()):

        n_passed_tests = 0
        for t_result in result.tests_results:
            n_passed_tests += TEST_PASSED == t_result[0]

        n_all_tests = len(result.tests)

        style = ""
        if n_all_tests == n_passed_tests:
            style = "display:none"

        html += "<div class='spoiler'>" + \
                 "<a onclick=\"show('spf%d')\">" % file_index + \
                  "<h1>%s (<font style='color:green'>%d</font>/%d)</h1>\n" % (file_name, n_passed_tests, n_all_tests) + \
                 "</a>" + \
                "<div class='hidetext' id='spf%d' style='%s'>" % (file_index, style) + \
                 "<h2>Compiling:</h2>\n" + \
                 "<b>Exit code:</b> %d<br>\n" % result.compile_exit_code + \
                 "<b>Messages:</b><br>\n%s\n" % result.compile_message.replace(" ","&nbsp;") + \
                 "<h2>Tests:</h2>\n" + \
                 "<b>Exit code:</b> %d<br>\n" % result.program_exit_code

        n_tests = 0
        for test in result.tests:
            func_name = test['func']
            test_type = test['type']
            input = test['input']
            waiting_result = test['output']

            status, output = TEST_UNKNOWN, "Ø"
            if len(result.tests_results) > n_tests:
                status, output = result.tests_results[n_tests]

            if TEST_TERMINATE == status:
                output = "Ø"

            style = ""
            if status == TEST_PASSED:
                style = "display:none"

            text_t_status = _get_status(status)

            html += "<div class='spoiler'>" + \
                    "<a onclick=\"show('spf%dt%d')\">" % (file_index, n_tests) + \
                     "<h3>Test #%d, %s</h3>" % (n_tests, text_t_status) + \
                    "</a>" + \
                    "<div class='hidetext' id='spf%dt%d' style=\"%s\" >" % (file_index, n_tests, style) + \
                    "<b>Status:</b> %s<br>\n" % text_t_status + \
                    "<b>Type:</b> %s<br>\n" % test_type + \
                    "<b>%s</b>(%s) = %s, wait: %s<br>\n" % (func_name, ", ".join(input), output, waiting_result) + \
                    "</div></div>"

            if TEST_TERMINATE == status:
                html += "<font style='color:red'>Program terminate with exit code %d</font><br>\n" % result.program_exit_code

            n_tests += 1

        html += "</div></div>"
        file_index += 1

    html += """
</body>
</html>
"""
    return html