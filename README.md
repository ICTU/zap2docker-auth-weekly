# Owasp ZAP with support for authentication
With the new [hook mechanism](https://github.com/zaproxy/zaproxy/issues/4925) in the ZAP Docker images authentication can implemented more easily compared to the original [implementation](https://github.com/ICTU/zap-baseline/blob/master/zap-baseline-custom.py).

# Examples

1. Running a baseline scan (passive) and automatic authentication
```
docker run --rm -v $(pwd):/zap/wrk/:rw -t ictu/zap2docker-weekly zap-baseline.py \
  -t https://demo.website.net \
  -r testreport.html \
   --hook=/zap/auth_hook.py \ 
  -z "auth.loginurl=https://demo.website.net/login/index.php \
      auth.username="admin" \
      auth.password="sandbox" \
      auth.auto=1"
```

2. Running a full scan (active) with manual authentication
```
docker run --rm -v $(pwd):/zap/wrk/:rw -t ictu/zap2docker-weekly zap-full-scan.py \
  -t https://demo.website.net \
  -r testreport.html \
   --hook=/zap/auth_hook.py \
  -z "auth.loginurl=https://demo.website.net/login/index.php \
      auth.username="admin" \
      auth.password="sandbox" \
      auth.username_field="j_username" \
      auth.password_field="j_password" \
      auth.submit_field="submit" \
      auth.exclude="\Qhttp://www.website.com/j_spring_security_logout\E,\Qhttp://www.website.com/j_spring_security_check\E.*""
```

Note: exclude URL's are comma separated regular expressions.

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
```

# Limitations
Since this authentication solution uses webdriver and a browser a custom image is needed to meet these requirements.
