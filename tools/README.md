# Ansible-LXC-RPC Tools

## install.py

Installs or updates an Ansible-LXC-RPC installation. Does not install or verify pre-requisites. It is (intended to be) 100% idempotent and appears to be so. Can be used for production or testing environments.

### Usage

```
Usage: install.py [OPTIONS]

Options:
  --haproxy / --no-haproxy  Should we install Haproxy? Defaults to no.
  --galera / --no-galera    Should we install Galera? Defaults to no.
  --rabbit / --no-rabbit    Should we install RabbitMQ? Defaults to no.
  --retries INTEGER         Number of retries to attempt on an Ansible
                            playbook before giving up.
  --help                    Show this message and exit.
```

  Please note that the --haproxy option is for development/testing environments only. Our haproxy installation is __NOT__ intended for production use.
