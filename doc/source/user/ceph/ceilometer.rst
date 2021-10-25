=====================================
Integrate radosgw into your Telemetry
=====================================

The telemetry (and in consequence accounting) for radosgw as object-storage
will not work out of the box. You need to change different parts of your
OpenStack and Ceph setup to get it up and running.


Ceilometer Changes
~~~~~~~~~~~~~~~~~~


Ceilometer needs additional pip packages to talk to Ceph Rados Gateway. To
install it, edit the default ceilometer_pip_packages in your
user_variables.yml file:

.. code-block:: yaml

    ceilometer_pip_packages:
        - ceilometer
        - ceilometermiddleware
        - cryptography
        - gnocchiclient
        - libvirt-python
        - PyMySQL
        - pymongo
        - python-memcached
        - tooz
        - warlock
        - requests-aws>=0.1.4 #https://github.com/openstack/ceilometer/blob/stable/pike/test-requirements.txt


You also have to configure Ceilometer to actually query radosgw. When your
ceilometer isn't configured to poll everything, add these pollsters to your
polling.yml file:

.. code-block:: yaml

    - name: radosgw_pollsters
      interval: 1200
      meters:
        -  radosgw.containers.objects
        -  radosgw.containers.objects.size
        -  radosgw.objects
        -  radosgw.objects.size
        -  radosgw.objects.containers
        -  radosgw.usage


Add them also to your pipeline:

.. code-block:: yaml

    - name: radosgw_source
      interval: 60
      meters:
        - "rgw.objects"
        - "rgw.objects.size"
        - "rgw.objects.containers"
        - "rgw.api.request"
        - "rgw.containers.objects"
        - "rgw.containers.objects.size"
      sinks:
        - meter_sink

Declare Ceph Rados Gateway as object-store in your ceilometer.conf file by
adding this to your user_variables.yml file:

.. code-block:: yaml

    ceilometer_ceilometer_conf_overrides:
      service_types:
        radosgw: object-store
      rgw_admin_credentials:
        access_key: XXX
        secret_key: XXX

The required user and credentials is created by this command:

.. code-block:: bash

    radosgw-admin user create --uid admin --display-name "admin user" --caps "usage=read,write;metadata=read,write;users=read,write;buckets=read,write"

To get your credentials, execute:

.. code-block:: bash

    radosgw-admin user info --uid admin | jq '.keys'

Ceph Changes
~~~~~~~~~~~~

The required changes are described in the documentation of Ceilometer. This is
just a sum up. In your ceph.conf add:

.. code-block:: ini

    [client.radosgw.gateway]
    rgw enable usage log = true
    rgw usage log tick interval = 30
    rgw usage log flush threshold = 1024
    rgw usage max shards = 32
    rgw usage max user shards = 1




