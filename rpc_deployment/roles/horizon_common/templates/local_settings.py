import os
from django.utils.translation import ugettext_lazy as _
from openstack_dashboard import exceptions

DEBUG = {{ debug|default('False') }}
TEMPLATE_DEBUG = DEBUG
COMPRESS_ENABLED = True
COMPRESS_ROOT = '{{ install_lib_dir }}/openstack_dashboard/static'

# Required for Django 1.5.
# If horizon is running in production (DEBUG is False), set this
# with the list of host/domain names that the application can serve.
# For more information see:
# https://docs.djangoproject.com/en/dev/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ['*']

# Set SSL proxy settings:
# For Django 1.4+ pass this header from the proxy after terminating the SSL,
# and don't forget to strip it from the client's request.
# For more information see:
# https://docs.djangoproject.com/en/1.4/ref/settings/#secure-proxy-ssl-header
# SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTOCOL', 'https')

# If Horizon is being served through SSL, then uncomment the following two
# settings to better secure the cookies from security exploits
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

# Overrides for OpenStack API versions. Use this setting to force the
# OpenStack dashboard to use a specific API version for a given service API.
# NOTE: The version should be formatted as it appears in the URL for the
# service API. For example, The identity service APIs have inconsistent
# use of the decimal point, so valid options would be "2.0" or "3".
# OPENSTACK_API_VERSIONS = {
#     "identity": 3,
#     "volume": 2
# }

# Set this to True if running on multi-domain model. When this is enabled, it
# will require user to enter the Domain name in addition to username for login.
# OPENSTACK_KEYSTONE_MULTIDOMAIN_SUPPORT = False

# Overrides the default domain used when running on single-domain model
# with Keystone V3. All entities will be created in the default domain.
# OPENSTACK_KEYSTONE_DEFAULT_DOMAIN = 'Default'

# Set Console type:
# valid options would be "AUTO", "VNC", "SPICE" or "RDP"
# CONSOLE_TYPE = "AUTO"

# Default OpenStack Dashboard configuration.
HORIZON_CONFIG = {
    'dashboards': ('project', 'admin', 'settings',),
    'default_dashboard': 'project',
    'user_home': 'openstack_dashboard.views.get_user_home',
    'ajax_queue_limit': 10,
    'auto_fade_alerts': {
        'delay': 3000,
        'fade_duration': 1500,
        'types': ['alert-success', 'alert-info']
    },
    'help_url': "{{ horizon_help_url|default('http://docs.openstack.org') }}",
    'exceptions': {
        'recoverable': exceptions.RECOVERABLE,
        'not_found': exceptions.NOT_FOUND,
        'unauthorized': exceptions.UNAUTHORIZED},
}

# Specify a regular expression to validate user passwords.
# HORIZON_CONFIG["password_validator"] = {
#     "regex": '.*',
#     "help_text": _("Your password does not meet the requirements.")
# }

# Disable simplified floating IP address management for deployments with
# multiple floating IP pools or complex network requirements.
# HORIZON_CONFIG["simple_ip_management"] = False

# Turn off browser autocompletion for the login form if so desired.
# HORIZON_CONFIG["password_autocomplete"] = "off"

LOCAL_PATH = os.path.dirname(os.path.abspath(__file__))

# Set custom secret key:
# You can either set it to a specific value or you can let horizion generate a
# default secret key that is unique on this machine, e.i. regardless of the
# amount of Python WSGI workers (if used behind Apache+mod_wsgi): However, there
# may be situations where you would want to set this explicitly, e.g. when
# multiple dashboard instances are distributed on different machines (usually
# behind a load-balancer). Either you have to make sure that a session gets all
# requests routed to the same dashboard instance or you set the same SECRET_KEY
# for all of them.
from horizon.utils import secret_key
SECRET_KEY = secret_key.generate_or_read_from_file(os.path.join(LOCAL_PATH, '.secret_key_store'))

# We recommend you use memcached for development; otherwise after every reload
# of the django development server, you will have to login again. To use
# memcached set CACHES to something like
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '{{ internal_vip_address }}:{{ memcached_port }}',
    }
}

SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': '{{ mysql_address }}',
        'NAME': '{{ container_database }}',
        'USER': '{{ container_mysql_user }}',
        'PASSWORD': '{{ container_mysql_password }}',
        'default-character-set': 'utf8'
    },
}

# Send email to the console by default
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# Or send them to /dev/null
#EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'

# Configure these for your outgoing email host
# EMAIL_HOST = 'smtp.my-company.com'
# EMAIL_PORT = 25
# EMAIL_HOST_USER = 'djangomail'
# EMAIL_HOST_PASSWORD = 'top-secret!'

# For multiple regions uncomment this configuration, and add (endpoint, title).
# AVAILABLE_REGIONS = [
#     ('http://cluster1.example.com:5000/v2.0', 'cluster1'),
#     ('http://cluster2.example.com:5000/v2.0', 'cluster2'),
# ]

OPENSTACK_HOST = "{{ auth_host }}"
OPENSTACK_KEYSTONE_URL = "{{ auth_identity_uri }}"
OPENSTACK_KEYSTONE_DEFAULT_ROLE = "_member_"

# Disable SSL certificate checks (useful for self-signed certificates):
{% if horizon_self_signed == true %}
OPENSTACK_SSL_NO_VERIFY = True
{% else %}
OPENSTACK_SSL_NO_VERIFY = False
OPENSTACK_SSL_CACERT = "{{ horizon_cacert_pem }}"
{% endif %}

# The CA certificate to use to verify SSL connections
# OPENSTACK_SSL_CACERT = '/path/to/cacert.pem'

# The OPENSTACK_KEYSTONE_BACKEND settings can be used to identify the
# capabilities of the auth backend for Keystone.
# If Keystone has been configured to use LDAP as the auth backend then set
# can_edit_user to False and name to 'ldap'.
#
# TODO(tres): Remove these once Keystone has an API to identify auth backend.
OPENSTACK_KEYSTONE_BACKEND = {
    'name': 'native',
    'can_edit_user': True,
    'can_edit_group': True,
    'can_edit_project': True,
    'can_edit_domain': True,
    'can_edit_role': True
}

#Setting this to True, will add a new "Retrieve Password" action on instance,
#allowing Admin session password retrieval/decryption.
#OPENSTACK_ENABLE_PASSWORD_RETRIEVE = False

# The Xen Hypervisor has the ability to set the mount point for volumes
# attached to instances (other Hypervisors currently do not). Setting
# can_set_mount_point to True will add the option to set the mount point
# from the UI.
OPENSTACK_HYPERVISOR_FEATURES = {
    'can_set_mount_point': False,
    'can_set_password': False,
}

# The OPENSTACK_NEUTRON_NETWORK settings can be used to enable optional
# services provided by neutron. Options currently available are load
# balancer service, security groups, quotas, VPN service.
OPENSTACK_NEUTRON_NETWORK = {
    'enable_lb': False,
    'enable_firewall': False,
    'enable_quotas': True,
    'enable_vpn': False,
    # The profile_support option is used to detect if an external router can be
    # configured via the dashboard. When using specific plugins the
    # profile_support can be turned on if needed.
    'profile_support': None,
    #'profile_support': 'cisco',
}

# The OPENSTACK_IMAGE_BACKEND settings can be used to customize features
# in the OpenStack Dashboard related to the Image service, such as the list
# of supported image formats.
OPENSTACK_IMAGE_BACKEND = {
    'image_formats': [
        ('', ''),
        ('aki', _('AKI - Amazon Kernel Image')),
        ('ami', _('AMI - Amazon Machine Image')),
        ('ari', _('ARI - Amazon Ramdisk Image')),
        ('iso', _('ISO - Optical Disk Image')),
        ('qcow2', _('QCOW2 - QEMU Emulator')),
        ('raw', _('Raw')),
        ('vdi', _('VDI')),
        ('vhd', _('VHD')),
        ('vmdk', _('VMDK'))
    ]
}

# The IMAGE_CUSTOM_PROPERTY_TITLES settings is used to customize the titles for
# image custom property attributes that appear on image detail pages.
IMAGE_CUSTOM_PROPERTY_TITLES = {
    "architecture": _("Architecture"),
    "kernel_id": _("Kernel ID"),
    "ramdisk_id": _("Ramdisk ID"),
    "image_state": _("Euca2ools state"),
    "project_id": _("Project ID"),
    "image_type": _("Image Type")
}

# OPENSTACK_ENDPOINT_TYPE specifies the endpoint type to use for the endpoints
# in the Keystone service catalog. Use this setting when Horizon is running
# external to the OpenStack environment. The default is 'publicURL'.
OPENSTACK_ENDPOINT_TYPE = '{{ horizon_endpoint_type }}'

# SECONDARY_ENDPOINT_TYPE specifies the fallback endpoint type to use in the
# case that OPENSTACK_ENDPOINT_TYPE is not present in the endpoints
# in the Keystone service catalog. Use this setting when Horizon is running
# external to the OpenStack environment. The default is None.  This
# value should differ from OPENSTACK_ENDPOINT_TYPE if used.
#SECONDARY_ENDPOINT_TYPE = "publicURL"

# The number of objects (Swift containers/objects or images) to display
# on a single page before providing a paging element (a "more" link)
# to paginate results.
API_RESULT_LIMIT = 1000
API_RESULT_PAGE_SIZE = 20

# The timezone of the server. This should correspond with the timezone
# of your entire OpenStack installation, and hopefully be in UTC.
TIME_ZONE = "UTC"

# When launching an instance, the menu of available flavors is
# sorted by RAM usage, ascending. If you would like a different sort order,
# you can provide another flavor attribute as sorting key. Alternatively, you
# can provide a custom callback method to use for sorting. You can also provide
# a flag for reverse sort. For more info, see
# http://docs.python.org/2/library/functions.html#sorted
# CREATE_INSTANCE_FLAVOR_SORT = {
#     'key': 'name',
#      # or
#     'key': my_awesome_callback_method,
#     'reverse': False,
# }

# The Horizon Policy Enforcement engine uses these values to load per service
# policy rule files. The content of these files should match the files the
# OpenStack services are using to determine role based access control in the
# target installation.

# Path to directory containing policy.json files
#POLICY_FILES_PATH = os.path.join(ROOT_PATH, "conf")
# Map of local copy of service policy files
#POLICY_FILES = {
#    'identity': 'keystone_policy.json',
#    'compute': 'nova_policy.json',
#    'volume': 'cinder_policy.json',
#    'image': 'glance_policy.json',
#}

# Trove user and database extension support. By default support for
# creating users and databases on database instances is turned on.
# To disable these extensions set the permission here to something
# unusable such as ["!"].
# TROVE_ADD_USER_PERMS = []
# TROVE_ADD_DATABASE_PERMS = []

LOGGING = {
    'version': 1,
    # When set to True this will disable all logging except
    # for loggers specified in this configuration dictionary. Note that
    # if nothing is specified here and disable_existing_loggers is True,
    # django.db.backends will still log unless it is disabled explicitly.
    'disable_existing_loggers': False,
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'django.utils.log.NullHandler',
        },
        'console': {
            # Set the level to "DEBUG" for verbose output logging.
            'level': 'INFO',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        # Logging from django.db.backends is VERY verbose, send to null
        # by default.
        'django.db.backends': {
            'handlers': ['null'],
            'propagate': False,
        },
        'requests': {
            'handlers': ['null'],
            'propagate': False,
        },
        'horizon': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'openstack_dashboard': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'novaclient': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'cinderclient': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'keystoneclient': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'glanceclient': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'neutronclient': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'heatclient': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'ceilometerclient': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'troveclient': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'swiftclient': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'openstack_auth': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'nose.plugins.manager': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'django': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'iso8601': {
            'handlers': ['null'],
            'propagate': False,
        },
    }
}

# 'direction' should not be specified for all_tcp/udp/icmp.
# It is specified in the form.
SECURITY_GROUP_RULES = {
    'all_tcp': {
        'name': 'ALL TCP',
        'ip_protocol': 'tcp',
        'from_port': '1',
        'to_port': '65535',
    },
    'all_udp': {
        'name': 'ALL UDP',
        'ip_protocol': 'udp',
        'from_port': '1',
        'to_port': '65535',
    },
    'all_icmp': {
        'name': 'ALL ICMP',
        'ip_protocol': 'icmp',
        'from_port': '-1',
        'to_port': '-1',
    },
    'ssh': {
        'name': 'SSH',
        'ip_protocol': 'tcp',
        'from_port': '22',
        'to_port': '22',
    },
    'smtp': {
        'name': 'SMTP',
        'ip_protocol': 'tcp',
        'from_port': '25',
        'to_port': '25',
    },
    'dns': {
        'name': 'DNS',
        'ip_protocol': 'tcp',
        'from_port': '53',
        'to_port': '53',
    },
    'http': {
        'name': 'HTTP',
        'ip_protocol': 'tcp',
        'from_port': '80',
        'to_port': '80',
    },
    'pop3': {
        'name': 'POP3',
        'ip_protocol': 'tcp',
        'from_port': '110',
        'to_port': '110',
    },
    'imap': {
        'name': 'IMAP',
        'ip_protocol': 'tcp',
        'from_port': '143',
        'to_port': '143',
    },
    'ldap': {
        'name': 'LDAP',
        'ip_protocol': 'tcp',
        'from_port': '389',
        'to_port': '389',
    },
    'https': {
        'name': 'HTTPS',
        'ip_protocol': 'tcp',
        'from_port': '443',
        'to_port': '443',
    },
    'smtps': {
        'name': 'SMTPS',
        'ip_protocol': 'tcp',
        'from_port': '465',
        'to_port': '465',
    },
    'imaps': {
        'name': 'IMAPS',
        'ip_protocol': 'tcp',
        'from_port': '993',
        'to_port': '993',
    },
    'pop3s': {
        'name': 'POP3S',
        'ip_protocol': 'tcp',
        'from_port': '995',
        'to_port': '995',
    },
    'ms_sql': {
        'name': 'MS SQL',
        'ip_protocol': 'tcp',
        'from_port': '1433',
        'to_port': '1433',
    },
    'mysql': {
        'name': 'MYSQL',
        'ip_protocol': 'tcp',
        'from_port': '3306',
        'to_port': '3306',
    },
    'rdp': {
        'name': 'RDP',
        'ip_protocol': 'tcp',
        'from_port': '3389',
        'to_port': '3389',
    },
}

FLAVOR_EXTRA_KEYS = {
    'flavor_keys': [
        ('quota:read_bytes_sec', _('Quota: Read bytes')),
        ('quota:write_bytes_sec', _('Quota: Write bytes')),
        ('quota:cpu_quota', _('Quota: CPU')),
        ('quota:cpu_period', _('Quota: CPU period')),
        ('quota:inbound_average', _('Quota: Inbound average')),
        ('quota:outbound_average', _('Quota: Outbound average')),
    ]
}
