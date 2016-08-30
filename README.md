# Zap Baseline Scan Script with authentication and active scanning

A customized version of the Owasp ZAP Baseline Scan Script (https://github.com/zaproxy/zaproxy/wiki/ZAP-Baseline-Scan) with support for authentication and active scanning.

# Dockerfile

The Dockerfile is based on the owasp/zap2docker-weekly image (https://hub.docker.com/r/owasp/zap2docker-weekly/). The Dockerfile installs some additional applications to support authentication in the Baseline Scan Script.

The Dockerfile is published at: https://hub.docker.com/r/ictu/zap2docker-weekly/

The customized scan script is not included in the container, but instead downloaded from Github when run. Please refer to example-run.sh

# example-run.sh

This is an example shellscript to run the Zap Baseline Scan script in a Docker container on an application with authentication and active scanning.