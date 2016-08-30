# Customized Owasp ZAP Dockerfile with support for authentication

FROM owasp/zap2docker-weekly
MAINTAINER Dick Snel <dick.snel@ictu.nl>

USER root

# Required for running headless webdriver
RUN apt-get install xvfb
RUN apt-get install firefox
RUN pip install selenium
RUN pip install pyvirtualdisplay

COPY zap-baseline-custom.py /zap/

RUN chown zap:zap /zap/zap-baseline-custom.py

USER zap