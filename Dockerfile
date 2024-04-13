# Customized Owasp ZAP Dockerfile with support for authentication

FROM --platform=linux/amd64 softwaresecurityproject/zap-stable
LABEL maintainer="Ernst Noorlander <ernst.noorlander@ictu.nl>"

USER root

# Install and update all add-ons
RUN ./zap.sh -cmd -silent -addoninstallall
RUN ./zap.sh -cmd -silent -addonupdate
RUN cp /root/.ZAP/plugin/*.zap plugin/ || :

RUN mkdir /zap/wrk \
	&& cd /opt \
	&& wget -qO- -O geckodriver.tar.gz https://github.com/mozilla/geckodriver/releases/download/v0.30.0/geckodriver-v0.30.0-linux64.tar.gz \
	&& tar -xvzf geckodriver.tar.gz \
	&& chmod +x geckodriver \
	&& ln -s /opt/geckodriver /usr/bin/geckodriver \
	&& export PATH=$PATH:/usr/bin/geckodriver 

# Set up the Chrome PPA
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
	&& echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list

# Update the package list and install chrome
RUN apt-get update -y \
	&& apt-get install -y jq \
	&& apt-get install -y google-chrome-stable

# Download and install Chromedriver
ENV CHROMEDRIVER_DIR /chromedriver
RUN export LATEST_CHROMEDRIVER_RELEASE=$(curl -s https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json | jq '.channels.Stable') \
	&& export LATEST_CHROMEDRIVER_URL=$(echo "$LATEST_CHROMEDRIVER_RELEASE" | jq -r '.downloads.chromedriver[] | select(.platform == "linux64") | .url') \
	&& mkdir $CHROMEDRIVER_DIR \
	&& wget -N "$LATEST_CHROMEDRIVER_URL" -P $CHROMEDRIVER_DIR \
	&& unzip $CHROMEDRIVER_DIR/chromedriver-linux64.zip -d $CHROMEDRIVER_DIR \
	&& mv $CHROMEDRIVER_DIR/chromedriver-linux64/* $CHROMEDRIVER_DIR

# Put Chromedriver into the PATH
ENV PATH $CHROMEDRIVER_DIR:$PATH

ADD . /zap/

ADD scripts /home/zap/.ZAP_D/scripts/scripts/active/
RUN chmod 777 /home/zap/.ZAP_D/scripts/scripts/active/ \
	&& chown -R zap:zap /zap/

USER zap

RUN pip install -r /zap/requirements.txt

VOLUME /zap/wrk
WORKDIR /zap
