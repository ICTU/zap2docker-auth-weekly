#!/usr/bin/python

import logging
import zap_config
import zap_auth

config = zap_config.ZapConfig()
config.auth_display = True
config.auth_login_url = 'https://example.nl/login'
config.auth_username = 'test@ictu.nl'
config.auth_password = 'test123'
config.auth_otp_secret = '234567845243234534'
config.auth_submitaction = 'click'
config.auth_token_endpoint = ''
config.auth_username_field_name = 'username'
config.auth_password_field_name = 'password'
config.auth_otp_field_name = 'loginTOTP'
config.auth_submit_field_name = 'loginSubmit'
config.auth_first_submit_field_name = 'next'
config.auth_exclude_urls = list()
config.auth_include_urls = list()
config.xss_collector = ''

logging.basicConfig(level=logging.INFO)

zap_common = None

auth = zap_auth.ZapAuth(config)
auth.login(None, 'https://example.nl/')
