import zap_webdriver

webdriver = zap_webdriver.ZapWebdriver()

# Triggered when running a script directly (ex. python zap-baseline.py ...)
def start_docker_zap(docker_image, port, extra_zap_params, mount_dir):
    webdriver.load_from_extra_zap_params(port, extra_zap_params)

# Triggered when running from the Docker image
def start_zap(port, extra_zap_params):
    webdriver.load_from_extra_zap_params(port, extra_zap_params)

def zap_access_target(zap, target):
    if webdriver.auth_loginUrl:
        webdriver.setup_zap_context(zap, target)
        webdriver.setup_webdriver(zap, target)
        webdriver.login(zap, target)
        webdriver.cleanup()
