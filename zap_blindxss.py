import os
import traceback
import logging
import zap_config
import random

def load(config: zap_config.ZapConfig, zap):
    # Load Custom Blind XSS scripts if a collector URI was provided
    if config.xss_collector:
        xss_script_path = replaceCollectorURI(config.xss_collector)
        
        try:
            logging.info(f"Loading custom script: {xss_script_path}")
            zap.script.load('blindxss', 'active', 'Oracle Nashorn', xss_script_path)
            zap.script.enable('blindxss')
            zap.ascan.set_option_target_params_injectable(31)
        except:
            logging.error("error in zap_blindxss.load loading custom script: %s", traceback.print_exc())
            os._exit(1)

def replaceCollectorURI(uri):
    template_script_path = '/home/zap/.ZAP_D/scripts/scripts/active/blindxss.js'

    with open(template_script_path, 'r') as file:
        filedata = file.read()

    filedata = filedata.replace('callbackdomain.com', uri)

    random_suffix = random.randint(1000,9999)
    script_path = f'/home/zap/.ZAP_D/scripts/scripts/active/bxxs_{random_suffix}.js'
    with open(script_path, 'w') as file:
        file.write(filedata)
    return script_path
