import zap_webdriver

def zap_access_target(zap, target):
    webdriver = zap_webdriver.ZapWebdriver()
    webdriver.load_from_environment_vars()
    webdriver.setup_zap_context(zap, target)
    webdriver.setup_webdriver(zap, target)
    webdriver.login(zap, target)
    webdriver.cleanup()
