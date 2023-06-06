FROM python:3.10-alpine3.18

RUN apk add --no-cache -u gcc g++ autoconf make libffi-dev openssl-dev dumb-init libgit2 libgit2-dev

ADD saltinit.py /usr/local/bin/saltinit

RUN addgroup -g 450 -S salt && adduser -u 450 -s /bin/sh -SD -G salt salt \
    && mkdir -p /etc/pki /etc/salt/pki /etc/salt/minion.d/ /etc/salt/master.d /etc/salt/autosign_grains /etc/salt/proxy.d /var/cache/salt /var/log/salt /var/run/salt \
    && chmod -R 2775 /etc/pki /etc/salt /var/cache/salt /var/log/salt /var/run/salt \
    && chgrp -R salt /etc/pki /etc/salt /var/cache/salt /var/log/salt /var/run/salt \
    && chmod 755 /usr/local/bin/saltinit

ENTRYPOINT ["/usr/bin/dumb-init"]
CMD ["/usr/local/bin/saltinit"]

EXPOSE 4505 4506 8000
VOLUME /etc/salt/pki/

USER salt
ENV PATH="/home/salt/.local/bin:${PATH}"
RUN USE_STATIC_REQUIREMENTS=1 pip3 install --no-cache-dir --user salt==3006.1 pycryptodomex CherryPy pyOpenSSL 'pygit2<1.12'

RUN salt-run salt.cmd tls.create_self_signed_cert
