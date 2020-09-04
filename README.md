# Owasp ZAP with support for authentication
With the new [hook mechanism](https://github.com/zaproxy/zaproxy/issues/4925) in the ZAP Docker images authentication can implemented more easily compared to the original [implementation](https://github.com/ICTU/zap-baseline/blob/master/zap-baseline-custom.py).

# Docker

Please find the Docker container here:

https://hub.docker.com/r/ictu/zap2docker-weekly

# Examples

1. Running a baseline scan (passive) and automatic authentication
```
docker run --rm -v $(pwd):/zap/wrk/:rw -t ictu/zap2docker-weekly zap-baseline.py -j -d -I \
  -t https://demo.website.net \
  -r testreport.html \
   --hook=/zap/auth_hook.py \ 
  -z "auth.loginurl=https://demo.website.net/login/index.php \
      auth.username="admin" \
      auth.password="sandbox" \
      auth.auto=1"
```

2. Running a full scan (active & max 60 minutes duration) with manual authentication
```
docker run --rm -v $(pwd):/zap/wrk/:rw -t ictu/zap2docker-weekly zap-full-scan.py -j -d -I -T 60 \
  -t https://demo.website.net \
  -r testreport.html \
   --hook=/zap/auth_hook.py \
  -z "auth.loginurl=https://demo.website.net/login/index.php \
      auth.username="admin" \
      auth.password="sandbox" \
      auth.username_field="j_username" \
      auth.password_field="j_password" \
      auth.submit_field="submit" \
      auth.exclude=".*logout.*,\Qhttp://url.com/logout\E.*"
      auth.include="https://api.website.net/"
```

Note: exclude URL's are comma separated regular expressions. Examples:
```
.*logout.*,\Qhttp://url.com/logout\E.*
```

# Parameters

```
auth.auto                 Automatically try to find the login fields (username, password, submit)
auth.loginurl             The URL to the login page
auth.username             A valid username
auth.password             A valid password
auth.username_field       The HTML name or id attribute of the username field
auth.password_field       The HTML name or id attribute of the password field
auth.submit_field         The HTML name or id attribute of the submit field
auth.first_submit_field   The HTML name or id attribute of the first submit field (in case of username -> next page -> password -> submit)
auth.exclude              Comma separated list of excluded URL's. Default: (logout|uitloggen|afmelden)
auth.include              Comma separated list of included URL's. The target URL is always included by default
```

# Limitations
1. Since this authentication solution uses webdriver and a browser a [custom image](https://hub.docker.com/repository/docker/ictu/zap2docker-weekly) is needed to meet these requirements.
2. Cookies that are automatically set by this script will not add flags like HttpOnly, Secure and SameSite. ZAP doest not support setting these cookies using the API. This will result in false-positives in the report regarding these flags.
