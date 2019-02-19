import zap_webdriver

webdriver = zap_webdriver.ZapWebdriver()

def start_zap(port, extra_zap_params):
    webdriver.load_from_extra_zap_params(port, extra_zap_params)

def zap_access_target(zap, target):
    webdriver.setup_zap_context(zap, target)
    webdriver.setup_webdriver(zap, target)
    webdriver.login(zap, target)
    webdriver.cleanup()
