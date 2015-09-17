Quick Start
===========

All-in-one (AIO) builds are a great way to perform an OpenStack Ansible build
for:

* a development environment
* an overview of how all of the OpenStack services fit together
* a simple lab deployment

Although AIO builds aren't recommended for large production deployments,
they're great for smaller proof-of-concept deployments.

It's strongly recommended to have hardware that meets the following
requirements before starting an AIO build:

* CPU/motherboard that supports `hardware-assisted virtualization`_
* 80GB disk space
* 16GB RAM

It's `possible` to perform AIO builds within a virtual machine but your
virtual machines will perform poorly.

.. _hardware-assisted virtualization: https://en.wikipedia.org/wiki/Hardware-assisted_virtualization

Running an AIO build in one step
--------------------------------

For a one-step build, there is a `convenient script`_ within the
openstack-ansible repository that will run a AIO build with defaults:

.. _convenient script: https://raw.githubusercontent.com/openstack/openstack-ansible/master/scripts/run-aio-build.sh

   .. code-block:: bash

    curl https://raw.githubusercontent.com/openstack/openstack-ansible/master/scripts/run-aio-build.sh | sudo bash

It's advised to run this build within a terminal muxer, like tmux or screen,
so that you don't lose your progress if you're disconnected from your terminal
session.

Running a customized AIO build
------------------------------

There are four main steps for running a customized AIO build:

* Configuration *(this step is optional)*
* Initial bootstrap
* Install and bootstrap Ansible
* Run playbooks

Start by cloning the openstack-ansible repository:

   .. code-block:: bash

       $ git clone https://github.com/openstack/openstack/ansible \
           /opt/openstack-ansible
       $ cd /opt/openstack-ansible

At this point, you can adjust which services are deployed within your AIO
build.  Look at the top of ``scripts/bootstrap-aio.sh`` for several examples.
If you'd like to skip the deployment of ceilometer, you could run the
following:

   .. code-block:: bash

       $ export DEPLOY_CEILOMETER="no"

Now you're ready to complete the bootstraps and run the playbooks:

   .. code-block:: bash

       $ scripts/bootstrap-aio.sh
       $ scripts/bootstrap-ansible.sh
       $ scripts/run-playbooks.sh

The installation process will take a while to complete, but here are some
general estimates:

* Bare metal systems with SSD storage: ~ 30-50 minutes
* Virtual machines with SSD storage: ~ 45-60 minutes
* Systems with traditional hard disks: ~ 90-120 minutes

Quick AIO build on Rackspace Cloud
----------------------------------

You can automate the AIO build process with a virtual machine from the
Rackspace Cloud.

First, we will need a cloud-config file that will allow us to run the build as
soon as the instance starts.  Save this file as ``user_data.yml``:

   .. code-block:: yaml

    #cloud-config
    apt_mirror: http://mirror.rackspace.com/ubuntu/
    package_upgrade: true
    packages:
      - git-core
    runcmd:
      - export ANSIBLE_FORCE_COLOR=true
      - export PYTHONUNBUFFERED=1
      - export REPO=https://github.com/openstack/openstack-ansible
      - git clone ${REPO} /opt/os-ansible
      - export DEPLOY_CEILOMETER="no"
      - cd /opt/os-ansible && scripts/bootstrap-aio.sh
      - cd /opt/os-ansible && scripts/bootstrap-ansible.sh
      - cd /opt/os-ansible && scripts/run-playbooks.sh
    output: { all: '| tee -a /var/log/cloud-init-output.log' }

Feel free to customize the YAML file to meet your requirements.  As an example
above, the deployment of ceilometer will be skipped due to the
``DEPLOY_CEILOMETER`` export line.

We can pass this YAML file to nova and build a Cloud Server at Rackspace:

   .. code-block:: bash

    nova boot \
        --flavor general1-8 \
        --image 09de0a66-3156-48b4-90a5-1cf25a905207 \
        --key-name=public_key_name \
        --config-drive=true \
        --user-data user_data.yml
        --poll
        openstack-ansible-aio-build

Be sure to replace ``public_key_name`` with the name of the public key that
you prefer to use with your instance.  Within a minute or so, your instance
should be running and the OpenStack Ansible installation will be in progress.

To follow along with the progress, ssh to your running instance and run:

   .. code-block:: bash

    tail -F /var/log/cloud-init-output.log
