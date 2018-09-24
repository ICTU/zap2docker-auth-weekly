# Customized Owasp ZAP Dockerfile with support for authentication

FROM owasp/zap2docker-weekly
MAINTAINER Roderik Eikeboom <roderik.eikeboom@ictu.nl>

USER root

# Install Selenium compatible firefox
RUN apt-get -y remove firefox

RUN cd /opt && \
	wget https://github.com/mozilla/geckodriver/releases/download/v0.11.1/geckodriver-v0.11.1-linux64.tar.gz && \
	tar -xvzf geckodriver-v0.11.1-linux64.tar.gz && \
	chmod +x geckodriver && \
	ln -s /opt/geckodriver /usr/bin/geckodriver && \
	export PATH=$PATH:/usr/bin/geckodriver

RUN cd /opt && \
	wget http://ftp.mozilla.org/pub/firefox/releases/46.0/linux-x86_64/en-US/firefox-46.0.tar.bz2 && \
	bunzip2 firefox-46.0.tar.bz2 && \
	tar xvf firefox-46.0.tar && \
	ln -s /opt/firefox/firefox /usr/bin/firefox

RUN pip install selenium==2.53.6
RUN pip install pyvirtualdisplay

COPY auth_hook.py /zap/

USER root
