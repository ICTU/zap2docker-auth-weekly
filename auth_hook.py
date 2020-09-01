import zap_webdriver
import os

webdriver = zap_webdriver.ZapWebdriver()

# Triggered when running a script directly (ex. python zap-baseline.py ...)
def start_docker_zap(docker_image, port, extra_zap_params, mount_dir):
    try:
        webdriver.load_from_extra_zap_params(port, extra_zap_params)
    except Exception as e:
        print("error in start_docker_zap: {0}".format(e))
        os._exit(1)

# Triggered when running from the Docker image
def start_zap(port, extra_zap_params):
    try:
        webdriver.load_from_extra_zap_params(port, extra_zap_params)
    except Exception as e:
        print("error in start_zap: {0}".format(e))
        os._exit(1)

def zap_access_target(zap, target):
    try:
        if webdriver.auth_loginUrl:
            webdriver.setup_zap_context(zap, target)
            webdriver.setup_webdriver(zap, target)
            webdriver.login(zap, target)
            webdriver.cleanup()
    except Exception as e:
        print("error in zap_access_target: {0}".format(e))
        os._exit(1)
