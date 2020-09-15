import zap_webdriver
import os
import traceback
import logging

webdriver = zap_webdriver.ZapWebdriver()

# Triggered when running a script directly (ex. python zap-baseline.py ...)
def start_docker_zap(docker_image, port, extra_zap_params, mount_dir):
    try:
        webdriver.load_from_extra_zap_params(port, extra_zap_params)
    except:
        logging.error("error in start_docker_zap: %s", traceback.print_exc())
        os._exit(1)

# Triggered when running from the Docker image
def start_zap(port, extra_zap_params):
    try:
        webdriver.load_from_extra_zap_params(port, extra_zap_params)
    except:
        logging.error("error in start_zap: %s", traceback.print_exc())
        os._exit(1)

def zap_access_target(zap, target):
    try:
        # ZAP Docker scripts reset the target to the root URL
        if target.count('/') > 2:
            # The url can include a valid path, but always reset to spider the host
            target = target[0:target.index('/', 8)+1]

        webdriver.login(zap, target)
    except:
        logging.error("error in zap_access_target: %s", traceback.print_exc())
        os._exit(1)

    return zap, target