# Copyright 2013 OpenStack Foundation
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import logging
import os

from oslo import i18n


# NOTE(dstanek): i18n.enable_lazy() must be called before
# keystone.i18n._() is called to ensure it has the desired lazy lookup
# behavior. This includes cases, like keystone.exceptions, where
# keystone.i18n._() is called at import time.
i18n.enable_lazy()


from keystone import backends
from keystone.common import dependency
from keystone.common import environment
from keystone.common import sql
from keystone import config
from keystone.openstack.common import log
from keystone import service


CONF = config.CONF

config.configure()
sql.initialize()
config.set_default_for_default_log_levels()

CONF(project='keystone')
config.setup_logging()

environment.use_stdlib()
name = os.path.basename(__file__)

if CONF.debug:
    CONF.log_opt_values(log.getLogger(CONF.prog), logging.DEBUG)


drivers = backends.load_backends()

# NOTE(ldbragst): 'application' is required in this context by WSGI spec.
# The following is a reference to Python Paste Deploy documentation
# http://pythonpaste.org/deploy/
application = service.loadapp('config:%s' % config.find_paste_config(), name)

dependency.resolve_future_dependencies()
