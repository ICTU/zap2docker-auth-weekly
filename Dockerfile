# Customized Owasp ZAP Dockerfile with support for authentication

FROM owasp/zap2docker-weekly
LABEL maintainer="Dick Snel <dick.snel@ictu.nl>"

USER root

# Install Selenium compatible firefox
RUN apt-get -y remove firefox

RUN cd /opt && \
	wget -qO- -O geckodriver.tar.gz https://github.com/mozilla/geckodriver/releases/download/v0.20.1/geckodriver-v0.20.1-linux64.tar.gz && \
	tar -xvzf geckodriver.tar.gz && \
	chmod +x geckodriver && \
	ln -s /opt/geckodriver /usr/bin/geckodriver && \
	export PATH=$PATH:/usr/bin/geckodriver

RUN cd /opt && \
	wget -qO- -O firefox.tar.bz2 http://ftp.mozilla.org/pub/firefox/releases/62.0.3/linux-x86_64/en-US/firefox-62.0.3.tar.bz2 && \
	bunzip2 firefox.tar.bz2 && \
	tar xvf firefox.tar && \
	ln -s /opt/firefox/firefox /usr/bin/firefox

RUN pip install selenium
RUN pip install pyvirtualdisplay

# Support for using the deprecated version
COPY zap-baseline-custom.py /zap/
COPY auth_hook.py /zap/
COPY zap_webdriver.py /zap/

RUN chown zap:zap /zap/zap-baseline-custom.py  && \
		chown zap:zap /zap/auth_hook.py && \
		chown zap:zap /zap/zap_webdriver.py && \
		chmod +x /zap/zap-baseline-custom.py

WORKDIR /zap

USER zap
