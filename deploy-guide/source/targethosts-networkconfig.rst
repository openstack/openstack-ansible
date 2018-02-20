=====================
Network configuration
=====================

The following table shows bridges that are to be configured on hosts.

+-------------+-----------------------+-------------------------------------+
| Bridge name | Best configured on    | With a static IP                    |
+=============+=======================+=====================================+
| br-mgmt     | On every node         | Always                              |
+-------------+-----------------------+-------------------------------------+
|             | On every storage node | When component is deployed on metal |
+ br-storage  +-----------------------+-------------------------------------+
|             | On every compute node | Always                              |
+-------------+-----------------------+-------------------------------------+
|             | On every network node | When component is deployed on metal |
+ br-vxlan    +-----------------------+-------------------------------------+
|             | On every compute node | Always                              |
+-------------+-----------------------+-------------------------------------+
|             | On every network node | Never                               |
+ br-vlan     +-----------------------+-------------------------------------+
|             | On every compute node | Never                               |
+-------------+-----------------------+-------------------------------------+

For a detailed reference of how the host and container networking is
implemented, refer to
:dev_docs:`OpenStack-Ansible Reference Architecture, section Container
Networking <reference/architecture/index.html>`.

For use case examples, refer to
:dev_docs:`User Guides <user/index.html>`.
