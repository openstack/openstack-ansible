Running as non-root user
========================

Deployers do not have to use ``root`` user accounts on deploy or target hosts.
This approach works out of the box by leveraging `Ansible privilege escalation`_.


Deploment hosts
~~~~~~~~~~~~~~~

You can avoid usage of the ``root`` user on a deployment by following these
guidelines:

#. Clone OpenStack-Ansible repository to home user directory. It means, that
   instead of ``/opt/openstack-ansible`` repository will be in
   ``~/openstack-ansible``.

#. Use custom path for ``/etc/openstack_deploy`` directory. You can place
   OpenStack-Ansible configuration directory inside user home directory.
   For that you will need to define the following environment variable:

   .. code-block:: shell-session

      export OSA_CONFIG_DIR="${HOME}/openstack_deploy"

#. If you want to keep basic ansible logging, you need either to create
   ``/openstack/log/ansible-logging/`` directory and allow user to write there,
   or define the following environment variable:

    .. code-block:: shell-session

      export ANSIBLE_LOG_PATH="${HOME}/ansible-logging/ansible.log"

    .. note::

        You can also add the environment variable to ``user.rc`` file inside
        openstack_deploy folder (``${OSA_CONFIG_DIR}/user.rc``). ``user.rc`` file
        is sourced each time you run ``openstack-ansible`` binary.

#. Initial bootstrap of OpenStack-Ansible using ./scripts/bootstrap-ansible.sh
   script still should be done either as the ``root`` user or escalate
   privileges using ``sudo`` or ``su``.


Destination hosts
~~~~~~~~~~~~~~~~~

It is also possible to use non-root user for Ansible authentication on
destination hosts. However, this user must be able to escalate privileges
using `Ansible privilege escalation`_.

.. note::

    You can add environment variables from that section to ``user.rc`` file
    inside openstack_deploy folder (``${OSA_CONFIG_DIR}/user.rc``). ``user.rc``
    file is sourced each time you run ``openstack-ansible`` binary.

There are also couple of additional things which you might want to consider:

#. Provide ``--become`` flag each time your run a playbook or ad-hoc command.
   Alternatively, you can define the following environment variable:

    .. code-block:: shell-session

      export ANSIBLE_BECOME="True"


#. Override Ansible temporary path if LXC containers are used. The ansible
   connection from the physical host to the LXC container passes
   environment variables from the host. This means that Ansible attempts to
   use the same temporary folder in the LXC container as it would on the host,
   relative to the non-root user ${HOME} directory. This will not exist inside
   the container and another path must be used instead.

   You can do that following in multiple ways:

   a. Define ``ansible_remote_tmp: /tmp`` in user_variables.yml
   b. Define the following environment variable:

    .. code-block:: shell-session

      export ANSIBLE_LOCAL_TEMP="/tmp"

#. Define the user that will be used for for connections from the deploy
   host to the ansible target hosts. In case the user is the same for all
   hosts in your deployment, you can do it in one of following ways:

   a. Define ``ansible_user: <USER>`` in user_variables.yml
   b. Define the following environment variable:

    .. code-block:: shell-session

      export ANSIBLE_REMOTE_USER="<USER>"

    If the user differs from host to host, you can leverage group_vars or
    host_vars. More information on how to use that can be found in the
    :doc:`overrides guide </reference/configuration/using-overrides>`

.. _Ansible privilege escalation: https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_privilege_escalation.html
