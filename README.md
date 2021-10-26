# Automatic Authentication for OWASP ZAP Docker
This project adds support to perform authenticated scans using the OWASP ZAP Docker [scanscripts](https://www.zaproxy.org/docs/docker/). These main features are available:

- Automatically or manually filling and completing loginforms.
- Records the sessiontoken (a cookie or Authorization header) and adds it to all spider and scanning requests.
- Exclude URL's to prevent termination of the session (such as /logout).
- Include additional URL's such as api.web.com which will also be spidered and scanned with the recorded sessiontoken.

# Docker

You can find the Docker image on [ictu/zap2docker-weekly](https://hub.docker.com/r/ictu/zap2docker-weekly)

# Examples using authentication

1. Running a passive scan with automatic authentication.
```
docker run --rm -v $(pwd):/zap/wrk/:rw -t ictu/zap2docker-weekly zap-baseline.py -I -j \
  -t https://demo.website.net \
  -r testreport.html \
   --hook=/zap/auth_hook.py \
  -z "auth.loginurl=https://demo.website.net/login/index.php \
      auth.username="admin" \
      auth.password="sandbox""
```

2. Running a full scan (max 10 mins spider and max 60 min scanning) with manual authentication and including an additional URL in the scope.
```
docker run --rm -v $(pwd):/zap/wrk/:rw -t ictu/zap2docker-weekly zap-full-scan.py -I -j -m 10 -T 60 \
  -t https://demo.website.net \
  -r testreport.html \
   --hook=/zap/auth_hook.py \
  -z "auth.loginurl=https://demo.website.net/login/index.php \
      auth.username="admin" \
      auth.password="sandbox" \
      auth.username_field="j_username" \
      auth.password_field="j_password" \
      auth.submit_field="submit" \
      auth.exclude=".*logout.*,http://url.com/somepath.*" \
      auth.include="https://api.website.net.*"
```

Note: exclude and include URL's are comma separated regular expressions. Examples:
```
.*logout.*,http://url.com/logout.*
```

Note: 
`-j` enable the AJAX spider (in addition to the default spider)
`-m 60` limits the spider to 60 minutes. 
`-T 60` limits the scanner to 60 minutes.
`-I` do not return an errorcode as exitcode if there are issues found.

For more info on the different scantypes and parameters take a look at: https://www.zaproxy.org/docs/docker/

# Extra authentication parameters

```
auth.loginurl             The URL to the login page. Required.
auth.username             A valid username. Required.
auth.password             A valid password. Required.
auth.otpsecret            The OTP secret.
auth.username_field       The HTML name or id attribute of the username field.
auth.password_field       The HTML name or id attribute of the password field.
auth.submit_field         The HTML name or id attribute of the submit field.
auth.otp_field            The HTML name or id attribute of the OTP field.
auth.first_submit_field   The HTML name or id attribute of the first submit field (in case of username -> next page -> password -> submit).
auth.submitaction         "Click" or "Submit" to click the login button or submit the form.
auth.display              True or False, indicate if the the webdriver should run in Headless mode.
auth.exclude              Comma separated list of excluded URL's (regex). Default: (logout|uitloggen|afmelden|signout)
auth.include              Comma separated list of included URL's (regex). Default: only the target URL and everything below it.
auth.check_delay          How long to wait after submitting the form.
auth.check_element        Element to look for to verify login completed.
```

# Blind XSS Payloads

This hook supports injecting Blind XSS payloads. You need to provide your callback URL which the XSS payload should trigger. This hook will automatically inject your payload in all possible locations like input fields, headers and cookies. (thanks to @greckko)

The below example uses [XSSHunter](https://xsshunter.com/) as a callback:

```
docker run --rm -v $(pwd):/zap/wrk/:rw -t ictu/zap2docker-weekly zap-full-scan.py -I -j -m 10 -T 60 \
  -t https://demo.website.net \
  -r testreport.html \
  --hook=/zap/auth_hook.py \
  -z "xss.collector=xsshunter.xss.ht"
```

# Limitations
1. Since this authentication solution uses a webdriver a [custom image](https://hub.docker.com/repository/docker/ictu/zap2docker-weekly) is needed to meet these requirements.
2. Cookies that are automatically set by this script will not add flags like HttpOnly, Secure and SameSite. ZAP does not support setting these cookies using the API. This will result in false-positives in the report regarding these flags.
