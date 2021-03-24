# Customized Owasp ZAP Dockerfile with support for authentication

FROM owasp/zap2docker-weekly
LABEL maintainer="Dick Snel <dick.snel@ictu.nl>"

USER root

RUN mkdir /zap/wrk \
    && mkdir -p /home/zap/.cache/pip \
	&& cd /opt \
	&& wget -qO- -O geckodriver.tar.gz https://github.com/mozilla/geckodriver/releases/download/v0.29.0/geckodriver-v0.29.0-linux64.tar.gz \
	&& tar -xvzf geckodriver.tar.gz \
	&& chmod +x geckodriver \
	&& ln -s /opt/geckodriver /usr/bin/geckodriver \
	&& export PATH=$PATH:/usr/bin/geckodriver

ADD *.py /zap/
ADD requirements.txt /zap/
ADD scripts/* /zap/scripts/

ADD scripts /home/zap/.ZAP_D/scripts/scripts/active/
RUN chmod 777 /home/zap/.ZAP_D/scripts/scripts/active/

RUN pip install -r /zap/requirements.txt \
	&& chown -R zap:zap /zap/ \
	&& chmod +x /zap/zap-baseline-custom.py

RUN chgrp -R 0 /zap
RUN chmod -R g=u /zap 
RUN chown -R zap:zap /home/zap/.cache
RUN chgrp -R 0 /home/zap
RUN chmod -R g=u /home/zap

USER zap

VOLUME /zap/wrk
WORKDIR /zap