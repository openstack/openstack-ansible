#!/usr/bin/env python
# Copyright 2014, Rackspace US, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# (c) 2014, Kevin Carter <kevin.carter@rackspace.com>
import argparse
import datetime
import hashlib
import os
import random
import tarfile

from Crypto import Random
try:
    import yaml
except ImportError:
    raise SystemExit('Missing Dependency, "PyYAML"')


class CredentialGenerator(object):
    """Credential generator class.

    This class is simply a method to generate random secrets.  This class will
    NOT encrypt values rather it creates the values which will be used as
    secrets within an application.  The credential generator will return
    strings in various sizes based on the requested secret type.

    There are four secret types that can be used within the class; `password`,
    `token`, 'secret', and `key`. These types return variable lengths of data.

    password: 16 - 64 character string
    secret:  16 - 64 character string
    token: 64 - 72 character string
    key: 24, or 32 character string (Needs to be AES compatible)

    Usage:
    >>> generator = CredentialGenerator()
    >>> token = generator.generator('token')
    """
    def generator(self, pw_type):
        """Generate new secret string.

        The generator method will check for a known method type and if found
        generates a hashed string which is then routed to the appropriate
        method.

        :param pw_type: ``str``  Type of secret to generate.
        :returns: ``str``
        """
        if hasattr(self, '_%s_gen' % pw_type):
            encoded_bytes = self._encode_bytes()
            func = getattr(self, '_%s_gen' % pw_type)
            return func(encoded_bytes=encoded_bytes)
        else:
            raise SystemExit('Unknown secrete type passed. [ %s ]' % pw_type)

    @staticmethod
    def _random_bytes():
        """Returns 1024 random bytes of data."""
        return Random.get_random_bytes(1024)

    def _encode_bytes(self):
        """Builds random strings based on random data.

        `_encode_bytes` will ensure that there's never an opportunity for
        duplicate data. Once the bytes are generated, they are hashed using
        SHA512 and the returned as a **hex** digest.
        """
        random_bytes = self._random_bytes()
        hash_obj = hashlib.sha512(random_bytes)
        return hash_obj.hexdigest()

    def _password_gen(self, encoded_bytes):
        """Returns ``str`` with a length between 16 and 64.

        :param encoded_bytes: ``str`` must be at least 64 charters long
        """
        return encoded_bytes[:random.randrange(16, 64)]

    def _token_gen(self, encoded_bytes):
        """Returns ``str`` with a length between 48 and 64.

        :param encoded_bytes: ``str`` must be at least 72 charters long
        """
        return encoded_bytes[:random.randrange(64, 72)]

    def _key_gen(self, encoded_bytes):
        """Returns ``str`` with a length of 24 or 32.

        Length restriction are required for key type secrets because of
        requirements in AES.

        :param encoded_bytes: ``str`` must be at least 32 charters long
        """
        return encoded_bytes[:random.choice([24, 32])]


def args():
    """Setup argument Parsing."""
    parser = argparse.ArgumentParser(
        usage='%(prog)s',
        description='OpenStack Token Password and Key Generator',
        epilog='Inventory Generator Licensed "Apache 2.0"'
    )
    parser.add_argument(
        '--file',
        help='User defined configuration file',
        required=True,
        default=None
    )
    parser.add_argument(
        '--regen',
        help='Regenerate all passwords',
        action='store_true',
        default=False
    )

    return vars(parser.parse_args())


def main():
    """Run the main Application.

    This will open a file that was specified on the command line. The file
    specified is assumed to be in valid YAML format, which is used in ansible.
    When the YAML file will be processed and any key with a null value that
    ends with 'password', 'token', or 'key' will have a generated password set
    as the value.

    The main function will create a backup of all changes in the file as a
    tarball in the same directory as the file specified.

    Command line usage has one required argument and one optional.  The
    argument ``--file`` is used to specify the file which passwords will be
    generated within. The argument ``--regen`` is used to regenerate all
    secrets within a file even if they were already set.
    """
    all_args = args()
    user_vars_file = all_args['file']
    user_vars_file = os.path.abspath(
        os.path.expanduser(
            user_vars_file
        )
    )

    with open(user_vars_file, 'rb') as f:
        user_vars = yaml.safe_load(f.read())

    if not user_vars:
        raise SystemExit(
            'FAIL: The variable file provided [ %s ] is empty.'
            % user_vars_file
        )

    changed = False
    generator = CredentialGenerator()
    for entry, value in user_vars.iteritems():
        if value is None or all_args['regen'] is True:
            if entry.endswith('password') or entry.endswith('secret'):
                changed = True
                user_vars[entry] = generator.generator(pw_type='password')
            elif entry.endswith('token'):
                changed = True
                user_vars[entry] = generator.generator(pw_type='token')
            elif entry.endswith('key'):
                changed = True
                user_vars[entry] = generator.generator(pw_type='key')
            elif entry.startswith('swift_hash_path'):
                changed = True
                user_vars[entry] = generator.generator(pw_type='key')

    # If changed is set to True, this will archive the old passwords
    if changed is True:
        user_vars_tar_file = '%s.tar' % user_vars_file
        print('Creating backup file [ %s ]' % user_vars_tar_file)
        # Create a tarball if needed
        with tarfile.open(user_vars_tar_file, 'a') as tar:
            basename = os.path.basename(user_vars_file)
            # Time stamp the password file in UTC
            utctime = datetime.datetime.utcnow()
            utctime = utctime.strftime('%Y%m%d_%H%M%S')
            backup_name = '%s-%s' % (basename, utctime)
            tar.add(user_vars_file, arcname=backup_name)

    with open(user_vars_file, 'wb') as f:
        f.write(
            yaml.safe_dump(
                user_vars,
                default_flow_style=False,
                width=1000
            )
        )

    print('Operation Complete, [ %s ] is ready' % user_vars_file)


if __name__ == '__main__':
    main()
