#!/usr/bin/env python3
import asyncio
import json
import os
import signal


async def main():
    futures = []
    if 'SALT_MINION_CONFIG' in os.environ:
        with open('/etc/salt/minion.d/minion.conf', 'w') as minion_file:
            json.dump(json.loads(os.environ['SALT_MINION_CONFIG']), minion_file)
        futures.append(await asyncio.create_subprocess_exec('salt-minion'))
    elif 'SALT_PROXY_ID' in os.environ or 'SALT_PROXY_CONFIG' in os.environ:
        if 'SALT_PROXY_CONFIG' in os.environ:
            with open('/etc/salt/proxy.d/proxy.conf', 'w') as proxy_file:
                json.dump(json.loads(os.environ['SALT_PROXY_CONFIG']), proxy_file)
        if 'SALT_PROXY_ID' in os.environ:
            futures.append(await asyncio.create_subprocess_exec('salt-proxy',
                                                                f'--proxyid={os.environ["SALT_PROXY_ID"]}'))
        else:
            futures.append(await asyncio.create_subprocess_exec('salt-proxy'))
    else:
        if not os.path.exists('/etc/salt/master.d/api.conf'):
            with open('/etc/salt/master.d/api.conf', 'w') as apifile:
                if 'SALT_API_CONFIG' in os.environ:
                    json.dump(json.loads(os.environ['SALT_API_CONFIG']), apifile)
                else:
                    json.dump({
                        'rest_cherrypy': {
                            'port': 8000,
                            'ssl_crt': '/etc/pki/tls/certs/localhost.crt',
                            'ssl_key': '/etc/pki/tls/certs/localhost.key',
                        },
                        'external_auth': {
                            'sharedsecret': {
                                'salt': ['.*', '@wheel', '@jobs', '@runner'],
                            },
                        },
                        'sharedsecret': os.environ.get('SALT_SHARED_SECRET', 'supersecret'),
                    }, apifile)

        if 'SALT_MASTER_CONFIG' in os.environ:
            with open('/etc/salt/master.d/master.conf', 'w') as masterfile:
                json.dump(json.loads(os.environ['SALT_MASTER_CONFIG']), masterfile)

            if 'SALT_AUTOSIGN_GRAINS' in os.environ:
                for k, v in json.loads(os.environ['SALT_AUTOSIGN_GRAINS']).items():
                    with open (f'/etc/salt/autosign_grains/{k}', 'w') as autosignfile:
                        for i in v:
                            autosignfile.write(f'{i}\n')

        with open('/etc/salt/master.d/user.conf', 'w') as userfile:
            json.dump({'user': 'salt'}, userfile)
        futures.append(await asyncio.create_subprocess_exec('salt-api'))
        futures.append(await asyncio.create_subprocess_exec('salt-master'))

    await asyncio.gather(*[future.communicate() for future in futures])


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    for signame in {'SIGINT', 'SIGTERM'}:
        loop.add_signal_handler(getattr(signal, signame), loop.stop)

    try:
        loop.run_until_complete(main())
    finally:
        loop.close()