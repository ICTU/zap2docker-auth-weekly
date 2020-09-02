import logging
import string
import os
import time
import urllib
import time
import re
import traceback
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from pyvirtualdisplay import Display
import localstorage

class ZapWebdriver:
    def load_from_extra_zap_params(self, port, extra_zap_params):
        self.zap_ip = 'localhost'
        self.extra_zap_params = extra_zap_params
        self.zap_port = port
        self.auth_auto = self._get_zap_param_boolean('auth.auto') or True
        self.auth_display = self._get_zap_param_boolean('auth.display') or False
        self.auth_loginUrl = self._get_zap_param('auth.loginurl') or ''
        self.auth_username = self._get_zap_param('auth.username') or ''
        self.auth_password = self._get_zap_param('auth.password') or ''
        self.auth_username_field_name = self._get_zap_param('auth.username_field') or 'username'
        self.auth_password_field_name = self._get_zap_param('auth.password_field') or 'password'
        self.auth_submit_field_name = self._get_zap_param('auth.submit_field') or 'login'
        self.auth_first_submit_field_name = self._get_zap_param('auth.first_submit_field') or 'next'
        self.auth_excludeUrls = self._get_zap_param_list('auth.exclude') or list()
        self.auth_includeUrls = self._get_zap_param_list('auth.include') or list()
        
    def setup_zap_context(self, zap, target):
        logging.info('Setup a new context for target %s', target)
        
        # create a new context
        contextName = 'auth'
        zap.context.new_context(contextName)
        
        # include everything below the target
        self.auth_includeUrls.append(target)
        
        # include additional url's
        for include in self.auth_includeUrls:
            zap.context.include_in_context(contextName, "\\Q" + include + "\\E.*")
            logging.info('Context - included %s.*', include)

        # exclude all urls that end the authenticated session
        if len(self.auth_excludeUrls) == 0:
            self.auth_excludeUrls.append('.*logout.*')
            self.auth_excludeUrls.append('.*uitloggen.*')
            self.auth_excludeUrls.append('.*afmelden.*')
            self.auth_excludeUrls.append('.*signout.*')

        for exclude in self.auth_excludeUrls:
            zap.spider.exclude_from_scan(exclude)
            zap.context.exclude_from_context(contextName, exclude)
            logging.info('Context - excluded %s', exclude)

        # set the context in scope
        zap.context.set_context_in_scope(contextName, True)
        zap.context.set_context_in_scope('Default Context', False)

    def setup_webdriver(self):
        logging.info('Setup proxy for webdriver')

        profile = webdriver.FirefoxProfile()
        profile.accept_untrusted_certs = True
        profile.set_preference('network.proxy.http', self.zap_ip)
        profile.set_preference('network.proxy.http_port', self.zap_port)
        profile.set_preference('network.proxy.ssl', self.zap_ip)
        profile.set_preference('network.proxy.ssl_port', self.zap_port)
        profile.set_preference('browser.startup.homepage_override.mstone', 'ignore')
        profile.set_preference('startup.homepage_welcome_url.additional', 'about:blank')

        self.display = Display(visible=self.auth_display, size=(1024, 768))
        self.display.start()

        logging.info('Start webdriver')
        self.driver = webdriver.Firefox(profile)

    def login(self, zap, target):
        if not self.auth_loginUrl:
            logging.info('No login URL provided - skipping authentication')
            return

        try:
            # setup the zap context
            self.setup_zap_context(zap, target)

            # setup the webdriver
            self.setup_webdriver()

            # login to the application
            self.auto_login(self.auth_loginUrl)
            
            logging.info('Finding authentication cookies')

            # add all found cookies as session cookies
            for cookie in self.driver.get_cookies():
                zap.replacer.add_rule(description = 'Cookie_' + cookie['name'], enabled = True, matchtype = 'REQ_HEADER', matchregex = False, matchstring = 'Cookie', replacement = cookie['name'] + '=' + cookie['value'])
                logging.info('Cookie added: %s - Value: %s', cookie['name'], cookie['value'])

            logging.info('Finding authentication headers')

            # try to find JWT tokens in LocalStorage and add them as Authorization header
            storage = localstorage.LocalStorage(self.driver)
            for key in storage.items():
                logging.info("Found storage item: %s: %s", key, storage.get(key))
                match = re.search('(eyJ[^"]*)', storage.get(key))
                if match:
                    auth_header = "Bearer " + match.group()
                    zap.replacer.add_rule(description = 'AuthHeader', enabled = True, matchtype = 'REQ_HEADER', matchregex = False, matchstring = 'Authorization', replacement = auth_header)
                    logging.info("Authorization header added: %s", auth_header)

        except:
            logging.error("error in login: %s", traceback.print_exc())
        finally:
            self.cleanup()

    def auto_login(self, login_url):
        logging.info('authenticate using webdriver against URL: %s', login_url)

        self.driver.get(login_url)

        # wait for the page to load
        time.sleep(5)

        logging.info('automatically finding login elements')

        # fill out the username field
        if self.auth_username:
            self.find_and_fill_element(self.auth_username, 
                                        self.auth_username_field_name,
                                        "(//input[(@type='text' and contains(@name,'ser')) or @type='text'])[1]")

        # fill out the password field
        if self.auth_password:
            try:
                self.find_and_fill_element(self.auth_password, 
                                            self.auth_password_field_name,
                                            "//input[@type='password' or contains(@name,'ass')]")
            except:
                logging.warning('Did not find the password field - clicking Next button and trying again')

                # if the password field was not found, we probably need to submit to go to the password page 
                # login flow: username -> next -> password -> submit
                self.find_and_click_element(self.auth_submit_field_name, "//*[@type='submit' or @type='button']")

                self.find_and_fill_element(self.auth_password, 
                                            self.auth_password_field_name,
                                            "//input[@type='password' or contains(@name,'ass')]")
        
        # submit
        self.find_and_click_element(self.auth_submit_field_name, "//*[@type='submit' or @type='button']")
        
        # wait for the page to load
        time.sleep(5)
        
    def find_and_click_element(self, name, xpath):
        element = self.find_element(name, xpath)
        element.click()
        logging.info('Clicked the %s element', name)
        
    def find_and_fill_element(self, value, name, xpath):
        element = self.find_element(name, xpath)
        element.clear()
        element.send_keys(value)
        logging.info('Filled the %s element', name)

    # 1. Find by ID attribute (case insensitive)
    # 2. Find by Name attribute (case insensitive)
    # 3. Find by xpath as fallback
    def find_element(self, name, xpath):
        element = None
        logging.info('Trying to find element %s', name)

        if name:
            try:
                element = self.driver.find_element_by_xpath("//*[(translate(@id, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz')='{0}')]".format(name))
                logging.info('Found element %s by id', name)
            except NoSuchElementException:
                try:
                    element = self.driver.find_element_by_xpath("//*[(translate(@name, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz')='{0}')]".format(name))
                    logging.info('Found element %s by name', name)
                except NoSuchElementException:
                    logging.warning('Could not find element %s by name or id', name)
        
        if xpath and not element:
            element = self.driver.find_element_by_xpath(xpath)
            logging.info('Found element %s by xpath', name)

        return element

    def cleanup(self):
        if self.driver:
            self.driver.quit()
        if self.display:
            self.display.stop()

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
