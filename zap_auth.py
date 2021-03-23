#!/usr/bin/python

import logging
import time
import time
import re
import traceback
import requests
import zap_config
import zap_common
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from pyvirtualdisplay import Display
import localstorage

class ZapAuth:
    driver = None
    display = None

    def setup_context(self, config: zap_config.ZapConfig, zap, target):
        # Set an X-Scanner header so requests can be identified in logs
        zap.replacer.add_rule(description = 'Scanner', enabled = True, matchtype = 'REQ_HEADER', matchregex = False, matchstring = 'X-Scanner', replacement = "ZAP")

        context_name = 'ctx-zap-docker'
        context_id = zap.context.new_context(context_name)

        zap_common.context_name = context_name
        zap_common.context_id = context_id
        
        # include everything below the target
        config.auth_includeUrls.append(target + '.*')
       
        # include additional url's
        for include in config.auth_includeUrls:
            zap.context.include_in_context(context_name, include)
            logging.info('Included %s', include)

        # exclude all urls that end the authenticated session
        if len(config.auth_excludeUrls) == 0:
            config.auth_excludeUrls.append('.*logout.*')
            config.auth_excludeUrls.append('.*uitloggen.*')
            config.auth_excludeUrls.append('.*afmelden.*')
            config.auth_excludeUrls.append('.*signout.*')

        for exclude in config.auth_excludeUrls:
            zap.context.exclude_from_context(context_name, exclude)
            logging.info('Excluded %s', exclude)

    def setup_webdriver(self, config: zap_config.ZapConfig):
        logging.info('Start display')

        self.display = Display(visible=config.auth_display, size=(1024, 768))
        self.display.start()

        logging.info('Start webdriver')

        profile = webdriver.FirefoxProfile()
        profile.accept_untrusted_certs = True
        self.driver = webdriver.Firefox(profile)

    def login(self, config: zap_config.ZapConfig, zap, target):
        try:
            # setup the zap context
            self.setup_context(config, zap, target)
            
            if not config.auth_loginUrl:
                logging.warning('No login URL provided - skipping authentication')
                return

            # setup the webdriver
            self.setup_webdriver(config)

            # login to the application
            self.auto_login(config)
            
            logging.info('Finding authentication cookies')

            # Create an empty session for session cookies
            zap.httpsessions.add_session_token(target, 'session_token')
            zap.httpsessions.create_empty_session(target, 'auth-session')

            # add all found cookies as session cookies
            for cookie in self.driver.get_cookies():
                zap.httpsessions.set_session_token_value(target, 'auth-session', cookie['name'], cookie['value'])
                logging.info('Cookie added: %s=%s', cookie['name'], cookie['value'])

            # Mark the session as active
            zap.httpsessions.set_active_session(target, 'auth-session')
            logging.info('Active session: %s', zap.httpsessions.active_session(target))

            if config.auth_token_endpoint:
                logging.info('Fetching authentication token from endpoint')

                auth_header = self.fetch_oauth_token(config.auth_token_endpoint, config.username, config.password)
                zap.replacer.add_rule(description = 'AuthHeader', enabled = True, matchtype = 'REQ_HEADER', matchregex = False, matchstring = 'Authorization', replacement = auth_header)
            else:
                logging.info('Finding authentication headers')

                # try to find JWT tokens in LocalStorage and add them as Authorization header
                storage = localstorage.LocalStorage(self.driver)
                for key in storage.items():
                    logging.info("Found storage item: %s: %s", key, storage.get(key)[:50])
                    match = re.search('(eyJ[^"]*)', storage.get(key))
                    if match:
                        auth_header = "Bearer " + match.group()
                        zap.replacer.add_rule(description = 'AuthHeader', enabled = True, matchtype = 'REQ_HEADER', matchregex = False, matchstring = 'Authorization', replacement = auth_header)
                        logging.info("Authorization header added: %s", auth_header)

        except:
            logging.error("error in login: %s", traceback.print_exc())
        finally:
            self.cleanup()

    def fetch_oauth_token(self, token_endpoint, username, password):
        response = requests.post(url = token_endpoint, params = { 'username': username, 'password': password }) 
        data = response.json() 
        token = data['access_token']
        token_type = data['token_type']
        auth_header = '{} {}'.format(token, token_type)
        return auth_header

    def auto_login(self, config: zap_config.ZapConfig):
        logging.info('authenticate using webdriver against URL: %s', config.auth_loginUrl)

        self.driver.get(config.auth_loginUrl)

        # wait for the page to load
        time.sleep(5)

        logging.info('automatically finding login elements')

        username_element = None

        # fill out the username field
        if config.auth_username:
            username_element = self.find_and_fill_element(config.auth_username, 
                                            config.auth_username_field_name,
                                            "input",
                                            "(//input[((@type='text' or @type='email') and contains(@name,'ser')) or (@type='text' or @type='email')])[1]")

        # fill out the password field
        if config.auth_password:
            try:
                self.find_and_fill_element(config.auth_password, 
                                            config.auth_password_field_name,
                                            "password",
                                            "//input[@type='password' or contains(@name,'ass')]")
            except:
                logging.warning('Did not find the password field - clicking Next button and trying again')

                # if the password field was not found, we probably need to submit to go to the password page 
                # login flow: username -> next -> password -> submit
                self.submit_form(config.auth_submitaction, config.auth_submit_field_name, username_element)
                self.find_and_fill_element(config.auth_password, 
                                            config.auth_password_field_name,
                                            "password"
                                            "//input[@type='password' or contains(@name,'ass')]")
        
        # submit
        self.submit_form(config.auth_submitaction, config.auth_submit_field_name, username_element)
        
        # wait for the page to load
        time.sleep(5)
        
    def submit_form(self, submit_action, submit_field_name, username_element):
        if submit_action == "click":
            element = self.find_element(submit_field_name, "submit", "//*[@type='submit' or @type='button' or button]")
            element.click()
            logging.info('Clicked the %s element', submit_field_name)
        elif username_element:
            username_element.submit()
            logging.info('Submitted the form')
        
    def find_and_fill_element(self, value, name, element_type, xpath):
        element = self.find_element(name, element_type, xpath)
        element.clear()
        element.send_keys(value)
        logging.info('Filled the %s element', name)

        return element

    # 1. Find by ID attribute (case insensitive)
    # 2. Find by Name attribute (case insensitive)
    # 3. Find by xpath
    # 4. Find by the default xpath if all above fail
    def find_element(self, name_or_xpath, element_type, default_xpath):
        element = None
        logging.info('Trying to find element %s', name_or_xpath)

        if name_or_xpath:
            try:
                path = self.build_xpath(name_or_xpath, "id", element_type)
                element = self.driver.find_element_by_xpath(path)
                logging.info('Found element %s by id', name_or_xpath)
            except NoSuchElementException:
                try:
                    path = self.build_xpath(name_or_xpath, "name", element_type)
                    element = self.driver.find_element_by_xpath(path)
                    logging.info('Found element %s by name', name_or_xpath)
                except NoSuchElementException:
                    try:
                        element = self.driver.find_element_by_xpath(name_or_xpath)
                        logging.info('Found element %s by xpath (name)', name_or_xpath)
                    except NoSuchElementException:
                        try:
                            element = self.driver.find_element_by_xpath(default_xpath)
                            logging.info('Found element %s by default xpath', default_xpath)
                        except NoSuchElementException:
                            logging.warning('Failed to find the element %s', name_or_xpath)
        
        return element

    def build_xpath(self, name, find_by, element_type):
        xpath = "translate(@{0}, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz')='{1}'".format(find_by, name.lower())

        if element_type == 'input':
            xpath = "//input[({0}) and ({1})]".format(xpath, "@type='text' or @type='email' or not(@type)")
        elif element_type == 'password':
            xpath = "//input[({0}) and ({1})]".format(xpath, "@type='text' or @type='password' or not(@type)")
        elif element_type == 'submit':
            xpath ="//*[({0}) and ({1})]".format(xpath, "@type='submit' or @type='button' or button")
        else:
            xpath = "//*[{0}]".format(xpath)

        logging.info('Built xpath: %s', xpath)

        return xpath

    def cleanup(self):
        if self.driver:
            self.driver.quit()
        if self.display:
            self.display.stop()
