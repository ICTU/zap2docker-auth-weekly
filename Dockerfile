# Customized Owasp ZAP Dockerfile with support for authentication

FROM owasp/zap2docker-weekly
LABEL maintainer="Dick Snel <dick.snel@ictu.nl>"

RUN pip install selenium
RUN pip install pyvirtualdisplay

USER root

RUN mkdir /zap/wrk && chown zap:zap /zap/wrk 

RUN cd /opt && \
	wget -qO- -O geckodriver.tar.gz https://github.com/mozilla/geckodriver/releases/download/v0.27.0/geckodriver-v0.27.0-linux64.tar.gz && \
	tar -xvzf geckodriver.tar.gz && \
	chmod +x geckodriver && \
	ln -s /opt/geckodriver /usr/bin/geckodriver && \
	export PATH=$PATH:/usr/bin/geckodriver

# Support for using the deprecated version
COPY zap-baseline-custom.py /zap/
COPY auth_hook.py /zap/
COPY zap_webdriver.py /zap/
COPY localstorage.py /zap/

RUN chown zap:zap /zap/zap-baseline-custom.py  && \
		chown zap:zap /zap/auth_hook.py && \
		chown zap:zap /zap/zap_webdriver.py && \
		chmod +x /zap/zap-baseline-custom.py

USER zap

WORKDIR /zap