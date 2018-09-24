#!/bin/bash

docker pull ictu/zap2docker-weekly
docker run --rm -v $(pwd):/zap/wrk/:rw \
-e auth_loginurl="http://www.website.com/login" \
-e auth_username=exampleuser \
-e auth_password=p@ssw0rd \
-e auth_usernamefield=j_username \
-e auth_passwordfield=j_password \
-e auth_submitfield=submit \
-e auth_exclude="http://www.website.com/j_spring_security_logout,http://www.website.com/j_spring_security_check.*" \
-t ictu/zap2docker-weekly zap-baseline.py -r testreport.html -g gen.conf -d -m 5 \
-t http://www.website.com \
