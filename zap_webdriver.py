import logging
import os
import time
import urllib
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from pyvirtualdisplay import Display

class ZapWebdriver:
    def __init__(self):
        self.auth_auto = False
        self.auth_display = False
        self.auth_loginUrl = ''
        self.auth_username = ''
        self.auth_password = ''
        self.auth_username_field_name = ''
        self.auth_password_field_name = ''
        self.auth_submit_field_name = ''
        self.auth_first_submit_field_name = ''
        self.auth_excludeUrls = []
        self.zap_ip = 'localhost'
        self.zap_port = 8081
        self.driver = None
        self.display = None

    def load_from_environment_vars(self):
        self.auth_auto = self._get_environ_boolean('AUTH_AUTO')
        self.auth_display = self._get_environ_boolean('AUTH_DISPLAY')
        self.auth_loginUrl = self._get_environ_string('AUTH_LOGINURL')
        self.auth_username = self._get_environ_string('AUTH_USERNAME')
        self.auth_password = self._get_environ_string('AUTH_PASSWORD')
        self.auth_username_field_name = self._get_environ_string('AUTH_USERNAME_FIELD')
        self.auth_password_field_name = self._get_environ_string('AUTH_PASSSWORD_FIELD')
        self.auth_submit_field_name = self._get_environ_string('AUTH_SUBMIT_FIELD')
        self.auth_first_submit_field_name = self._get_environ_string('AUTH_FIRST_SUBMIT_FIELD')
        self.auth_excludeUrls = self._get_environ_string('AUTH_EXCLUDE').split(',')

    def setup_zap_context(self, zap, target):
        logging.debug('Setup a new context')

        # create a new context
        contextId = zap.context.new_context('auth')

        # include everything below the target
        zap.context.include_in_context('auth', "\\Q" + target + "\\E.*")
        logging.debug('Context - included ' + target + ".*")

        # exclude all urls that end the authenticated session
        if len(self.auth_excludeUrls) == 0:
            self.auth_excludeUrls.append('(logout|uitloggen|afmelden)')

        for exclude in self.auth_excludeUrls:
            zap.context.exclude_from_context('auth', exclude)
            logging.debug ('Context - excluded ' + exclude)

        # set the context in scope
        zap.context.set_context_in_scope('auth', True)
        zap.context.set_context_in_scope('Default Context', False)

    def setup_webdriver(self, zap, target):
        logging.debug ('Setup proxy for webdriver')

        PROXY = self.zap_ip + ':' + str(self.zap_port)
        logging.debug ('PROXY: ' + PROXY)
        webdriver.DesiredCapabilities.FIREFOX['proxy'] = {
            "httpProxy":PROXY,
            "ftpProxy":PROXY,
            "sslProxy":PROXY,
            "noProxy":None,
            "proxyType":"MANUAL",
            "class":"org.openqa.selenium.Proxy",
            "autodetect":False
        }

        profile = webdriver.FirefoxProfile()
        profile.accept_untrusted_certs = True
        profile.set_preference("browser.startup.homepage_override.mstone", "ignore")
        profile.set_preference("startup.homepage_welcome_url.additional", "about:blank")

        self.display = Display(visible=self.auth_display, size=(1024, 768))
        self.display.start()

        logging.debug ('Start webdriver')
        self.driver = webdriver.Firefox(profile)
        self.driver.implicitly_wait(30)

    def login(self, zap, target):
        logging.getLogger().setLevel(logging.DEBUG)

        logging.debug('Authenticate using webdriver ' + self.auth_loginUrl)

        self.driver.get(self.auth_loginUrl)

        if self.auth_username_field_name:
            userField = find_element(self.auth_username_field_name, None)
            userField.clear()
            userField.send_keys(self.auth_username)

        if self.auth_first_submit_field_name:
            find_element(self.auth_first_submit_field_name, "//input[@type='submit']").click()

        if self.auth_password_field_name:
            passwordField = find_element(self.auth_password_field_name, None)
            passwordField.clear()
            passwordField.send_keys(self.auth_password)

        if self.auth_submit_field_name:
            find_element(self.auth_submit_field_name, "//input[@type='submit']").click()

        # Wait for all requests to finish - not needed?
        # time.sleep(30)

        logging.debug('Create an authenticated session')

        # Create a new session using the aquired cookies from the authentication
        zap.httpsessions.create_empty_session(target, 'auth-session')

        # add all found cookies as session cookies
        for cookie in self.driver.get_cookies():
            zap.httpsessions.set_session_token_value(target, 'auth-session', cookie['name'], cookie['value'])
            logging.debug('Cookie found: ' + cookie['name'] + ' - Value: ' + cookie['value'])

        # Mark the session as active
        zap.httpsessions.set_active_session(target, 'auth-session')

        logging.debug('Active session: ' + zap.httpsessions.active_session(target))

    def find_element(self, name, xpath):
        element = None
        try:
            element = self.driver.find_element_by_id(name)
        except NoSuchElementException:
            try:
                element = self.driver.find_element_by_name(name)
            except NoSuchElementException:
                if xpath is None:
                    raise

                element = self.driver.find_element_by_xpath(xpath)

        return element

    def cleanup(self):
        self.driver.quit()
        self.display.stop()

    def _get_environ_string(self, key):
        try:
            return os.environ[key]
        except KeyError:
            return ''

    def _get_environ_boolean(self, key):
        return self._get_environ_string(key) in ['True', 'true']
