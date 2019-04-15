# Customized Owasp ZAP Dockerfile with support for authentication

FROM owasp/zap2docker-weekly
LABEL maintainer="Dick Snel <dick.snel@ictu.nl>"

USER root

# Install Selenium compatible firefox
RUN apt-get -y remove firefox

RUN cd /opt && \
	wget https://github.com/mozilla/geckodriver/releases/download/v0.20.1/geckodriver-v0.20.1-linux64.tar.gz && \
	tar -xvzf geckodriver-v0.20.1-linux64.tar.gz && \
	chmod +x geckodriver && \
	ln -s /opt/geckodriver /usr/bin/geckodriver && \
	export PATH=$PATH:/usr/bin/geckodriver

RUN cd /opt && \
	wget http://ftp.mozilla.org/pub/firefox/releases/55.0/linux-x86_64/en-US/firefox-55.0.tar.bz2 && \
	bunzip2 firefox-55.0.tar.bz2 && \
	tar xvf firefox-55.0.tar && \
	ln -s /opt/firefox/firefox /usr/bin/firefox

RUN pip install selenium
RUN pip install pyvirtualdisplay

# Warn for the usage of the deprecated version which does not use the hook mechanism
COPY zap-baseline-custom.py /zap/

COPY auth_hook.py /zap/
COPY zap_webdriver.py /zap/

USER root
