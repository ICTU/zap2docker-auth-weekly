#!/usr/bin/python

import getopt
import sys
import logging
import subprocess

def main(argv):
    logging.warning('Your version of ICTU/zap-baseline is deprecated and no longer supported. Please upgrade: https://github.com/ICTU/zap-baseline/')

    try:
        opts, args = getopt.getopt(argv,'t:c:u:g:m:r:w:x:l:daijsz:', ['auth_display', 'auth_loginurl=', 'auth_username=', 'auth_auto', 'auth_password=', 'auth_usernamefield=', 'auth_passwordfield=', 'auth_firstsubmitfield=', 'auth_submitfield=', 'auth_exclude=', 'active_scan'])
    except getopt.GetoptError as exc:
        logging.warning('Invalid option ' + exc.opt + ' : ' + exc.msg)
        #usage()
        sys.exit(3)

    scanmode = 'zap-baseline.py'
    mins = '10'
    report_html = ''
    report_xml = ''
    target = ''

    auth_auto = '0'
    auth_loginUrl = ''
    auth_username = ''
    auth_password = ''
    auth_username_field_name = ''
    auth_password_field_name = ''
    auth_submit_field_name = ''
    auth_first_submit_field_name = ''
    auth_excludeUrls = ''
    auth_display = False

    for opt, arg in opts:
        if opt == '-t':
            target = arg
        elif opt == '-m':
            mins = arg
        elif opt == '-r':
            report_html = arg
        elif opt == '-x':
            report_xml = '-x ' + arg
        elif opt == '--auth_auto':
            auth_auto = '1'
        elif opt == '--auth_display':
            auth_display = True
        elif opt == '--auth_username':
            auth_username = arg
        elif opt == '--auth_password':
            auth_password = arg
        elif opt == '--auth_loginurl':
            auth_loginUrl = arg
        elif opt == '--auth_usernamefield':
            auth_username_field_name = arg
        elif opt == '--auth_passwordfield':
            auth_password_field_name = arg
        elif opt == '--auth_submitfield':
            auth_submit_field_name = arg
        elif opt == '--auth_firstsubmitfield':
            auth_first_submit_field_name = arg
        elif opt == '--auth_exclude':
            auth_excludeUrls = arg
        elif opt == '--active_scan':
            scanmode = 'zap-full-scan.py'

    optionalargs = '"auth.loginurl="{}" auth.username="{}" auth.password="{}" auth.auto={} auth.username_field="{}" auth.password_field="{}" auth.submit_field="{}" auth.first_submit_field="{}" auth.exclude="{}" auth.display="{}""' \
                   .format(auth_loginUrl, auth_username, auth_password, auth_auto, auth_username_field_name, auth_password_field_name, auth_submit_field_name, auth_first_submit_field_name, auth_excludeUrls, auth_display)
    command = './{} -t {} -r {} {} -m {} -z {} -d --hook=/zap/auth_hook.py'.format(scanmode, target, report_html, report_xml, mins, optionalargs)

    logging.info('Starting: ' + command)
    subprocess.call(command, shell=True)

if __name__ == '__main__':
    main(sys.argv[1:])
