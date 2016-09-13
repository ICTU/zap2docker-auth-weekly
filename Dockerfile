# Customized Owasp ZAP Dockerfile with support for authentication

FROM owasp/zap2docker-weekly
MAINTAINER Dick Snel <dick.snel@ictu.nl>

USER root

# Required for running headless webdriver
RUN apt-get install xvfb

RUN apt-get -y remove firefox
RUN cd /opt && \
	wget http://ftp.mozilla.org/pub/firefox/releases/46.0/linux-x86_64/en-US/firefox-46.0.tar.bz2 && \
	bunzip2 firefox-46.0.tar.bz2 && \
	tar xvf firefox-46.0.tar && \
	ln -s /opt/firefox/firefox /usr/bin/firefox
	
#RUN apt-get install firefox
RUN pip install selenium
RUN pip install pyvirtualdisplay

COPY zap-baseline-custom.py /zap/

RUN chown zap:zap /zap/zap-baseline-custom.py && \ 
	chmod +x /zap/zap-baseline-custom.py

USER zap