#!/usr/bin/python

import logging
import zap_config
import zap_auth

target = "http://example.org/"
config = zap_config.ZapConfig()
config.auth_display = True
config.auth_login_url = 'http://example.org/login'
config.auth_username = 'admin'
config.auth_password = 'Password123'
config.auth_otp_secret = ''
config.auth_submitaction = 'click'
config.auth_token_endpoint = ''
config.auth_username_field_name = 'username'
config.auth_password_field_name = 'password'
config.auth_otp_field_name = ''
config.auth_submit_field_name = 'login'
config.auth_first_submit_field_name = 'next'
config.auth_exclude_urls = list()
config.auth_include_urls = list()
config.check_delay = 5
config.check_element = ''
config.xss_collector = ''

logging.basicConfig(level=logging.INFO)

zap_common = None

auth = zap_auth.ZapAuth(config)

if config.auth_token_endpoint:
    auth.login_from_token_endpoint(None)
else:
    auth.setup_webdriver()
    auth.login()
    auth.set_authentication(None, target)
