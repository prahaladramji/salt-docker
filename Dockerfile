FROM python:3.8-alpine3.12

RUN echo $(grep '^[^#].\+alpine/.\+/main\>' /etc/apk/repositories) >> /etc/apk/repositories \
 && apk add -u gcc g++ autoconf make libffi-dev libgit2-dev openssl-dev \
 && apk add dumb-init 

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
RUN pip3 install --no-cache-dir --user salt==3001 pycryptodomex CherryPy pyOpenSSL pygit2

RUN salt-run salt.cmd tls.create_self_signed_cert
