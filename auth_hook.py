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

class DotDict(dict):
    def __getattr__(self, key):
        return self[key]
    def __setattr__(self, key, val):
        if key in self.__dict__:
            self.__dict__[key] = val
        else:
            self[key] = val


zap_auth_options = DotDict()
zap_auth_options.auth_auto = False
zap_auth_options.auth_display = False
zap_auth_options.auth_loginUrl = ''
zap_auth_options.auth_username = ''
zap_auth_options.auth_password = ''
zap_auth_options.auth_username_field_name = ''
zap_auth_options.auth_password_field_name = ''
zap_auth_options.auth_submit_field_name = ''
zap_auth_options.auth_first_submit_field_name = ''
zap_auth_options.auth_excludeUrls = []
zap_auth_options.zap_ip = 'localhost'
zap_auth_options.zap_port = 8081
zap_auth_options.driver = None
zap_auth_options.display = None

def zap_access_target(zap, target):
    global zap_auth_options
    read_auth_environment_vars(zap_auth_options)
    setup_zap_context(zap, target, zap_auth_options)
    setup_webdriver(zap_auth_options)
    login(zap, target, zap_auth_options)
    cleanup(zap_auth_options)

def read_auth_environment_vars(options):
    options.auth_auto = get_environ_boolean('AUTH_AUTO')
    options.auth_display = get_environ_boolean('AUTH_DISPLAY')
    options.auth_loginUrl = get_environ_string('AUTH_LOGINURL')
    options.auth_username = get_environ_string('AUTH_USERNAME')
    options.auth_password = get_environ_string('AUTH_PASSWORD')
    options.auth_username_field_name = get_environ_string('AUTH_USERNAME_FIELD')
    options.auth_password_field_name = get_environ_string('AUTH_PASSSWORD_FIELD')
    options.auth_submit_field_name = get_environ_string('AUTH_SUBMIT_FIELD')
    options.auth_first_submit_field_name = get_environ_string('AUTH_FIRST_SUBMIT_FIELD')
    options.auth_excludeUrls = get_environ_string('AUTH_EXCLUDE').split(',');

def setup_zap_context(zap, target, options):
    logging.debug('Setup a new context')

    # create a new context
    contextId = zap.context.new_context('auth')

    # include everything below the target
    zap.context.include_in_context('auth', "\\Q" + target + "\\E.*")
    logging.debug('Context - included ' + target + ".*")

    # exclude all urls that end the authenticated session
    if len(options.auth_excludeUrls) == 0:
        options.auth_excludeUrls.append('(logout|uitloggen|afmelden)')

    for exclude in options.auth_excludeUrls:
        zap.context.exclude_from_context('auth', exclude)
        logging.debug ('Context - excluded ' + exclude)

    # set the context in scope
    zap.context.set_context_in_scope('auth', True)
    zap.context.set_context_in_scope('Default Context', False)

def setup_webdriver(options):
    logging.debug ('Setup proxy for webdriver')

    PROXY = options.zap_ip + ':' + str(options.zap_port)
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

    options.display = Display(visible=options.auth_display, size=(1024, 768))
    options.display.start()

    logging.debug ('Start webdriver')
    options.driver = webdriver.Firefox(profile)
    options.driver.implicitly_wait(30)


def get_environ_string(key):
    try:
        return os.environ[key]
    except KeyError:
        return ''

def get_environ_boolean(key):
    return get_environ_string(key) in ['True', 'true']

def find_element(name, xpath):
    element = None
    try:
        element = driver.find_element_by_id(name)
    except NoSuchElementException:
        try:
            element = driver.find_element_by_name(name)
        except NoSuchElementException:
            if xpath is None:
                raise

            element = driver.find_element_by_xpath(xpath)

    return element

def login(zap, target, options):
    logging.getLogger().setLevel(logging.DEBUG)


    logging.debug('Authenticate using webdriver ' + options.auth_loginUrl)
    logging.debug('TEST:' + get_environ_string('AUTH_LOGINURL') + ':TEST')

    options.driver.get(options.auth_loginUrl)

    if options.auth_username_field_name:
        userField = find_element(options.auth_username_field_name, None)
        userField.clear()
        userField.send_keys(options.auth_username)

    if options.auth_first_submit_field_name:
        find_element(options.auth_first_submit_field_name, "//input[@type='submit']").click()

    if options.auth_password_field_name:
        passwordField = find_element(options.auth_password_field_name, None)
        passwordField.clear()
        passwordField.send_keys(options.auth_password)

    if options.auth_submit_field_name:
        find_element(options.auth_submit_field_name, "//input[@type='submit']").click()

    # Wait for all requests to finish - not needed?
    time.sleep(30)

    logging.debug('Create an authenticated session')

    # Create a new session using the aquired cookies from the authentication
    zap.httpsessions.create_empty_session(target, 'auth-session')

    # add all found cookies as session cookies
    for cookie in driver.get_cookies():
        zap.httpsessions.set_session_token_value(target, 'auth-session', cookie['name'], cookie['value'])
        logging.debug('Cookie found: ' + cookie['name'] + ' - Value: ' + cookie['value'])

    # Mark the session as active
    zap.httpsessions.set_active_session(target, 'auth-session')

    logging.debug('Active session: ' + zap.httpsessions.active_session(target))


def cleanup(options):
    options.driver.quit()
    options.display.stop()
