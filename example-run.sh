#!/bin/bash

docker pull ictu/zap2docker-weekly
docker run -v $(pwd):/zap/wrk/:rw -t ictu/zap2docker-weekly /bin/bash -c "wget https://raw.githubusercontent.com/ICTU/zap-baseline/master/zap-baseline.py -O zap-baseline-auth.py;python zap-baseline-auth.py \
-t http://www.website.com -r testreport.html -g gen.conf -d -m 5 \
--auth_loginurl http://www.website.com/login \
--auth_username exampleuser \
--auth_password p@ssw0rd \
--auth_usernamefield j_username \
--auth_passwordfield j_password \
--auth_submitfield submit \
--auth_exclude http://www.website.com/j_spring_security_logout,http://www.website.com/j_spring_security_check.*"
