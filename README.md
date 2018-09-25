# Owasp ZAP with support for authentication
With the new [hook mechanism](https://github.com/zaproxy/zaproxy/issues/4925) in the ZAP Docker images authentication can implemented more easily compared to the original [implementation](https://github.com/ICTU/zap-baseline/blob/master/zap-baseline-custom.py)

# Examples
```
docker run -v $(pwd):/zap/wrk/:rw \
  -e AUTH_LOGINURL="http://www.website.com/login" \
  -e AUTH_USERNAME="exampleuser" \
  -e AUTH_PASSWORD="p@ssw0rd" \
  -e AUTH_USERNAME_FIELD="j_username" \
  -e AUTH_PASSSWORD_FIELD="j_password" \
  -e AUTH_SUBMIT_FIELD="submit" \
  -e AUTH_EXCLUDE="http://www.website.com/j_spring_security_logout,http://www.website.com/j_spring_security_check.*" \
  -t ictu/zap2docker-weekly:Rebase-From-Fork zap-baseline.py \
  -P 8081 \
  -t https://www.website.com \
  -g gen.conf -r testreport.html \
  --hook=/zap/auth_hook.py
```

# Limitations
Since this authentication solution uses webdriver solution a browser and webdriver itself are needed this custom image with is needed to meet these requirements.

The auth_hook.py script does not have a nice way to get the random ZAP port running in the container, port 8081 is therefor hardcoded.

Another limitation is the passing of commandline parameters to the authentication hook. Since the ZAP options parser doesn't accept unknown parameters and there is no way to update the supported options via the hook mechanism.

# Todo
* Backwards compatibility commandline parameters before merging to master
* Extract the port number used from the ZAP configuration in one of the [hooks](https://github.com/zaproxy/zaproxy/blob/develop/docker/docs/scan-hooks.md) runtime
* Update webdriver and firefox to latest version in Dockerfile
