#!/usr/bin/python

import logging

class ZapConfig:
    def load_config(self, extra_zap_params):
        logging.info("Extra params passed by ZAP: %s", extra_zap_params)

        self.extra_zap_params = extra_zap_params
        self.auth_auto = self._get_zap_param_boolean('auth.auto') or True
        self.auth_display = self._get_zap_param_boolean('auth.display') or False
        self.auth_loginUrl = self._get_zap_param('auth.loginurl') or ''
        self.auth_username = self._get_zap_param('auth.username') or ''
        self.auth_password = self._get_zap_param('auth.password') or ''
        self.auth_token_endpoint = self._get_zap_param('auth.token_endpoint') or ''
        self.auth_username_field_name = self._get_zap_param('auth.username_field') or 'username'
        self.auth_password_field_name = self._get_zap_param('auth.password_field') or 'password'
        self.auth_submit_field_name = self._get_zap_param('auth.submit_field') or 'login'
        self.auth_first_submit_field_name = self._get_zap_param('auth.first_submit_field') or 'next'
        self.auth_excludeUrls = self._get_zap_param_list('auth.exclude') or list()
        self.auth_includeUrls = self._get_zap_param_list('auth.include') or list()
        self.xss_collector = self._get_zap_param('xss.collector') or ''
        
    def _get_zap_param(self, key):
        for param in self.extra_zap_params:
            if param.find(key) > -1:
                value = param[len(key) + 1:]
                logging.info('_get_zap_param %s: %s', key, value)
                return value

    def _get_zap_param_list(self, key):
        for param in self.extra_zap_params:
            if param.find(key) > -1:
                value = list(filter(None, param[len(key) + 1:].split(',')))
                logging.info('_get_zap_param %s: %s', key, value)
                return value
        
    def _get_zap_param_boolean(self, key):
        for param in self.extra_zap_params:
            if param.find(key) > -1:
                value = param[len(key) + 1:] in ['1', 'True', 'true']
                logging.info('_get_zap_param_boolean %s: %s', key, value)
                return value
