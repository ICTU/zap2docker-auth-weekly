#!/usr/bin/python

import logging
import time
import time
import re
import os
import traceback
import requests
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import browserstorage
import pyotp


class ZapAuth:
    driver = None
    config = None

    def __init__(self, config=None):
        self.config = config

    def setup_context(self, zap, target):
        # Set an X-Scanner header so requests can be identified in logs
        zap.replacer.add_rule(description='Scanner', enabled=True, matchtype='REQ_HEADER',
                              matchregex=False, matchstring='X-Scanner', replacement="ZAP")

        context_name = 'ctx-zap-docker'
        context_id = zap.context.new_context(context_name)

        import zap_common
        zap_common.context_name = context_name
        zap_common.context_id = context_id

        # include everything below the target
        self.config.auth_include_urls.append(target + '.*')

        # include additional url's
        for include in self.config.auth_include_urls:
            zap.context.include_in_context(context_name, include)
            logging.info('Included %s', include)

        # exclude all urls that end the authenticated session
        if len(self.config.auth_exclude_urls) == 0:
            self.config.auth_exclude_urls.append('.*logout.*')
            self.config.auth_exclude_urls.append('.*uitloggen.*')
            self.config.auth_exclude_urls.append('.*afmelden.*')
            self.config.auth_exclude_urls.append('.*signout.*')

        for exclude in self.config.auth_exclude_urls:
            zap.context.exclude_from_context(context_name, exclude)
            logging.info('Excluded %s', exclude)

    def setup_webdriver(self):
        logging.info('Start webdriver')

        options = webdriver.ChromeOptions()
        if not self.config.auth_display:
            options.add_argument('--headless')
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        self.driver = webdriver.Chrome(options=options)
        self.driver.set_window_size(1920, 1080)
        self.driver.maximize_window()

    def authenticate(self, zap, target):
        try:
            # setup the zap context
            if zap:
                self.setup_context(zap, target)

            # perform authentication using selenium
            if self.config.auth_login_url:
                # setup the webdriver
                self.setup_webdriver()

                # login to the application
                self.login()

                # find session cookies or tokens and set them in ZAP
                self.set_authentication(zap, target)
            # perform authentication using a provided Bearer token
            elif self.config.auth_bearer_token:
                self.add_authorization_header(
                    zap, f"Bearer {self.config.auth_bearer_token}")
            # perform authentication using a simple token endpoint
            elif self.config.auth_token_endpoint:
                self.login_from_token_endpoint(zap)
            # authentication using API key
            elif self.config.auth_api_key:
                self.add_api_key(zap, self.config.auth_api_key)
            else:
                logging.warning(
                    'No login URL, Token Endpoint or Bearer token provided - skipping authentication')

        except Exception:
            logging.error("error in authenticate: %s", traceback.print_exc())
            if self.auth_fail_on_error:
                logging.error("exiting")
                raise
        finally:
            self.cleanup()

    def set_authentication(self, zap, target):
        logging.info('Finding authentication cookies')

        # Create an empty session for session cookies
        if zap:
            zap.httpsessions.add_session_token(target, 'session_token')
            zap.httpsessions.create_empty_session(target, 'auth-session')

        # add all found cookies as session cookies
        for cookie in self.driver.get_cookies():
            if zap:
                zap.httpsessions.set_session_token_value(
                    target, 'auth-session', cookie['name'], cookie['value'])
            logging.info('Cookie added: %s=%s',
                         cookie['name'], cookie['value'])

        # Mark the session as active
        if zap:
            zap.httpsessions.set_active_session(target, 'auth-session')
            logging.info('Active session: %s',
                         zap.httpsessions.active_session(target))

        logging.info('Finding authentication headers')

        # try to find JWT tokens in Local Storage and Session Storage and add them as Authorization header
        localStorage = browserstorage.BrowserStorage(self.driver, 'localStorage')
        sessionStorage = browserstorage.BrowserStorage(self.driver, 'sessionStorage')

        self.add_token_from_browser_storage(zap, localStorage)
        self.add_token_from_browser_storage(zap, sessionStorage)
                
    def add_token_from_browser_storage(self, zap, browserStorage):
        for key in browserStorage:
            logging.info("Found Local or Session Storage item: %s: %s",
                         key, browserStorage.get(key)[:50])
            match = re.search('(eyJ[^"]*)', browserStorage.get(key))
            if match:
                auth_header = "Bearer " + match.group()
                self.add_authorization_header(zap, auth_header)

    def login_from_token_endpoint(self, zap):
        logging.info('Fetching authentication token from endpoint')

        response = requests.post(self.config.auth_token_endpoint, data={
                                 self.config.auth_username_field_name: self.config.auth_username, self.config.auth_password_field_name: self.config.auth_password})
        data = response.json()

        if "token" in data:
            auth_header = f"Bearer {data['token']}"
        elif "token_type" in data:
            auth_header = f"{data['token_type']} {data['token_type']}"
        elif "access" in data:
            auth_header = f"Bearer {data['access']}"
        else:
            raise Exception("Don't know how to handle auth response: " + str(data))

        if auth_header:
            self.add_authorization_header(zap, auth_header)

    def add_authorization_header(self, zap, auth_token):
        if zap:
            zap.replacer.add_rule(description='AuthHeader', enabled=True, matchtype='REQ_HEADER',
                                  matchregex=False, matchstring='Authorization', replacement=auth_token)
        logging.info(
            "Authorization header added: %s", auth_token)

    # Replacer rule for API key
    def add_api_key(self, zap, api_key):
        if zap:
            zap.replacer.add_rule(description='APIKey', enabled=True, matchtype='REQ_HEADER',
                                  matchregex=False, matchstring='api-key', replacement=api_key)

    def login(self):
        logging.info('authenticate using webdriver against URL: %s',
                     self.config.auth_login_url)

        self.driver.get(self.config.auth_login_url)

        # wait for the page to load
        time.sleep(5)

        logging.info('automatically finding login elements')

        username_element = None

        # fill out the username field
        if self.config.auth_username:
            username_element = self.fill_username()

        # fill out the password field
        if self.config.auth_password:
            try:
                self.fill_password()
            except Exception:
                logging.warning(
                    'Did not find the password field - clicking Next button and trying again')

                # if the password field was not found, we probably need to submit to go to the password page
                # login flow: username -> next -> password -> submit
                self.fill_password()

        # fill out the OTP field
        if self.config.auth_otp_secret:
            try:
                self.fill_otp()
            except Exception:
                logging.warning(
                    'Did not find the OTP field - clicking Next button and trying again')

                # if the OTP field was not found, we probably need to submit to go to the OTP page
                # login flow: username -> next -> password -> next -> otp -> submit
                self.submit_form(self.config.auth_submitaction,
                                 self.config.auth_submit_field_name, username_element)
                self.fill_otp()

        # submit
        self.submit_form(self.config.auth_submitaction,
                         self.config.auth_submit_field_name, username_element)

        # wait for the page to load
        if self.config.auth_check_element:
            try:
                logging.info('Check element')
                WebDriverWait(self.driver, self.config.auth_check_delay).until(
                    EC.presence_of_element_located((By.XPATH, self.config.auth_check_element)))
            except TimeoutException:
                logging.info('Check element timeout')
        else:
            time.sleep(self.config.auth_check_delay)

    def submit_form(self, submit_action, submit_field_name, username_element):
        if submit_action == "click":
            element = self.find_element(
                submit_field_name, "submit", "//*[@type='submit' or @type='button' or button]")
            element.click()
            logging.info('Clicked the %s element', submit_field_name)
        elif username_element:
            username_element.submit()
            logging.info('Submitted the form')

    def fill_username(self):
        return self.find_and_fill_element(self.config.auth_username,
                                          self.config.auth_username_field_name,
                                          "input",
                                          "(//input[((@type='text' or @type='email') and contains(@name,'ser')) or (@type='text' or @type='email')])[1]")

    def fill_password(self):
        return self.find_and_fill_element(self.config.auth_password,
                                          self.config.auth_password_field_name,
                                          "password",
                                          "//input[@type='password' or contains(@name,'ass')]")

    def fill_otp(self):
        totp = pyotp.TOTP(self.config.auth_otp_secret)
        otp = totp.now()

        logging.info('Generated OTP: %s', otp)

        return self.find_and_fill_element(otp,
                                          self.config.auth_otp_field_name,
                                          "input",
                                          "//input[@type='text' and (contains(@id,'otp') or contains(@name,'otp'))]")

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
    def find_element(self, name_or_id_or_xpath, element_type, default_xpath):
        element = None
        logging.info('Trying to find element %s', name_or_id_or_xpath)

        if name_or_id_or_xpath:
            try:
                path = self.build_xpath(
                    name_or_id_or_xpath, "id", element_type)
                element = self.driver.find_element_by_xpath(path)
                logging.info('Found element %s by id', name_or_id_or_xpath)
            except NoSuchElementException:
                try:
                    path = self.build_xpath(
                        name_or_id_or_xpath, "name", element_type)
                    element = self.driver.find_element_by_xpath(path)
                    logging.info('Found element %s by name',
                                 name_or_id_or_xpath)
                except NoSuchElementException:
                    try:
                        element = self.driver.find_element_by_xpath(
                            name_or_id_or_xpath)
                        logging.info(
                            'Found element %s by xpath (name)', name_or_id_or_xpath)
                    except NoSuchElementException:
                        try:
                            element = self.driver.find_element_by_xpath(
                                default_xpath)
                            logging.info(
                                'Found element %s by default xpath', default_xpath)
                        except NoSuchElementException:
                            logging.warning(
                                'Failed to find the element %s', name_or_id_or_xpath)

        return element

    def build_xpath(self, name, find_by, element_type):
        xpath = "translate(@{0}, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz')='{1}'".format(
            find_by, name.lower())

        if element_type == 'input':
            xpath = "//input[({0}) and ({1})]".format(xpath,
                                                      "@type='text' or @type='email' or @type='number' or not(@type)")
        elif element_type == 'password':
            xpath = "//input[({0}) and ({1})]".format(xpath,
                                                      "@type='text' or @type='password' or not(@type)")
        elif element_type == 'submit':
            xpath = "//*[({0}) and ({1})]".format(xpath,
                                                  "@type='submit' or @type='button' or button")
        else:
            xpath = "//*[{0}]".format(xpath)

        logging.info('Built xpath: %s', xpath)

        return xpath

    def cleanup(self):
        if self.driver:
            self.driver.quit()
