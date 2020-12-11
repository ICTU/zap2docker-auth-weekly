# Customized Owasp ZAP Dockerfile with support for authentication

FROM owasp/zap2docker-weekly
LABEL maintainer="Dick Snel <dick.snel@ictu.nl>"

USER root

RUN mkdir /zap/wrk \
	&& cd /opt \
	&& wget -qO- -O geckodriver.tar.gz https://github.com/mozilla/geckodriver/releases/download/v0.27.0/geckodriver-v0.27.0-linux64.tar.gz \
	&& tar -xvzf geckodriver.tar.gz \
	&& chmod +x geckodriver \
	&& ln -s /opt/geckodriver /usr/bin/geckodriver \
	&& export PATH=$PATH:/usr/bin/geckodriver

ADD . /zap/
RUN pip install -r /zap/requirements.txt \
	&& chown -R zap:zap /zap/ \
	&& chmod +x /zap/zap-baseline-custom.py

USER zap

VOLUME /zap/wrk
WORKDIR /zap