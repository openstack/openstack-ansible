==================================
openstack_user_config.yml examples
==================================

The ``/etc/openstack_deploy/openstack_user_config.yml`` configuration file
contains parameters to configure target host, and target host networking.
Examples are provided below for a test environment and production environment.

Test environment
~~~~~~~~~~~~~~~~

.. literalinclude:: ../../../etc/openstack_deploy/openstack_user_config.yml.aio

Production environment
~~~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../../../etc/openstack_deploy/openstack_user_config.yml.example
   :start-after: # limitations under the License.

Setting an MTU on a default lxc bridge (lxcbr0)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To modify a container MTU, set ``lxc_net_mtu`` to
a value other than 1500 in ``user_variables.yml``.

.. note::

   It is necessary to modify the ``provider_networks`` subsection to
   reflect the change.

This will define the MTU on the lxcbr0 interface. An ifup/ifdown will
be required if the interface is already up for the changes to take effect.
