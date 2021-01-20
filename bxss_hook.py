import os
import traceback
import logging

def loadscripts(zap):
    ## Load Custom Blind XSS scripts
    try:
        zap.script.load('bxss.js', 'active', 'Oracle Nashorn', '/home/zap/.ZAP_D/scripts/scripts/active/bxss.js')
        zap.script.enable('bxss.js')
        zap.ascan.set_option_target_params_injectable(31)
    except:
        logging.error("error in zap_started loading custom script: %s", traceback.print_exc())
        os._exit(1)

def zap_started(zap, target):
    loadscripts(zap)
    return zap, target