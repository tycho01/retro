#!/usr/bin/env python
import getpass
import io
import os
import requests
import retro.data
import subprocess
import sys
import tarfile
import zipfile
import tempfile
import zipfile


def main():
    username = input('Steam Username: ')
    password = getpass.getpass('Steam Password (leave blank if cached): ')

    if password:
        password = password + '\n'

        authcode = input('Steam Guard code: ')
        if authcode:
            password = password + authcode + '\n'
        else:
            password = password + '\r\n'
    else:
        password = '\r\n'

    with tempfile.TemporaryDirectory() as dir:
        if sys.platform.startswith('linux'):
            r = requests.get('https://steamcdn-a.akamaihd.net/client/installer/steamcmd_linux.tar.gz')
            steamcmd = 'steamcmd.sh'
        elif sys.platform.startswith('darwin'):
            r = requests.get('https://steamcdn-a.akamaihd.net/client/installer/steamcmd_osx.tar.gz')
        elif sys.platform.startswith('win32'):
            r = requests.get('https://steamcdn-a.akamaihd.net/client/installer/steamcmd.zip')
        else:
            raise RuntimeError('Unknown platform %s' % sys.platform)

        if sys.platform.startswith('win32'):
            zfile = zipfile.ZipFile(io.BytesIO(r.content))
            zfile.extractall(dir)
            executable = 'steamcmd'
        else:
            tarball = tarfile.open(fileobj=io.BytesIO(r.content))
            tarball.extractall(dir)
            executable = 'steamcmd.sh'

        command = [os.path.join(dir, executable),
                   '+login', username,
                   '+force_install_dir', dir,
                   '+@sSteamCmdForcePlatformType', 'windows',
                   '+app_update', '34270', 'validate',
                   '+quit']

        print('Installing games...')
        output = subprocess.run(command, input=password.encode('utf-8'), stdout=subprocess.PIPE)
        if output.returncode != 0:
            stdout = output.stdout.decode('utf-8').split('\n')
            print(*stdout[-3:-1], sep='\n')
            sys.exit(1)
        romdir = os.path.join(dir, 'uncompressed ROMs')
        roms = [os.path.join(romdir, rom) for rom in os.listdir(romdir)]
        retro.data.merge(*roms, quiet=False)


if __name__ == '__main__':
    main()
