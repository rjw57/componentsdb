import logging
import os
import shutil
import subprocess
import tempfile
from contextlib import contextmanager

_LOG = logging.getLogger(__name__)

@contextmanager
def _temp_dir():
    """Context manager which creates termporary directory and clears up
    after."""
    d = tempfile.mkdtemp(prefix='self-signed-cert-')
    yield d
    shutil.rmtree(d)

def gen_self_signed_cert():
    with _temp_dir() as d:
        key_fn = os.path.join(d, 'key.pem')
        crt_fn = os.path.join(d, 'cert.pem')

        _LOG.info('Generating X509 self-signed certificate.')

        output = subprocess.check_output(
            'openssl req -sha256 -batch -new -newkey rsa:2048 -days 365 -nodes -x509'.split() +
            ['-keyout', key_fn, '-out', crt_fn],
            stderr=subprocess.STDOUT, cwd=d
        )

        for l in output.splitlines():
            _LOG.info(l.decode('utf8'))

        with open(key_fn) as k, open(crt_fn) as c:
            return c.read(), k.read()

def main():
    logging.basicConfig(level=logging.INFO)

    cert, key = gen_self_signed_cert()
    print('Certificate:')
    print(cert)
    print('Key:')
    print(key)

if __name__ == '__main__':
    main()
