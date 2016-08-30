# ZAP Baseline Scan Script with authentication and active scanning

A customized version of the Owasp ZAP Baseline Scan Script (https://github.com/zaproxy/zaproxy/wiki/ZAP-Baseline-Scan) with support for authentication and active scanning.

The script performs the following steps:

1. Perform authentication (if required)
2. Spider the webapplication
3. Perform a passive scan on the spidered URL's
4. Perform an active scan (if required)
5. Output findings to an HTML report

```
Usage: zap-baseline.py -t <target> [options]
    -t target         target URL including the protocol, eg https://www.example.com
Options:
    -c config_file    config file to use to INFO, IGNORE or FAIL warnings
    -u config_url     URL of config file to use to INFO, IGNORE or FAIL warnings
    -g gen_file       generate default config file (all rules set to WARN)
    -m mins           the number of minutes to spider for (default 1)
    -r report_html    file to write the full ZAP HTML report
    -x report_xml     file to write the full ZAP XML report
    -a                include the alpha passive scan rules as well
    -d                show debug messages
    -i                default rules not in the config file to INFO
    -l level          minimum level to show: PASS, IGNORE, INFO, WARN or FAIL, use with -s to hide example URLs
    -s                short output format - dont show PASSes or example URLs
    --active_scan     after passive scan, perform active scan
Authentication:
    --auth_username        username
    --auth_password        password
    --auth_loginurl        login form URL ex. http://www.website.com/login
    --auth_usernamefield   username inputfield name
    --auth_passwordfield   password inputfield name
    --auth_submitfield     submit button name
    --auth_exclude         comma separated list of URLs to exclude, supply all URLs causing logout
```

# Dockerfile

The Dockerfile is based on the owasp/zap2docker-weekly image (https://hub.docker.com/r/owasp/zap2docker-weekly/). The Dockerfile installs some additional applications to support authentication in the Baseline Scan Script.

The Dockerfile is published at: https://hub.docker.com/r/ictu/zap2docker-weekly/

The customized scan script is not included in the container, but instead downloaded from Github when run. Please refer to example-run.sh

# example-run.sh

This is an example shellscript to run the Zap Baseline Scan script in a Docker container on an application with authentication and active scanning.