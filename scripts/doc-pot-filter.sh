#!/bin/bash

set -e

# Extract messages from the deploy-guide
sphinx-build -b gettext \
    doc/source/deploy-guide/source \
    doc/build/gettext-deploy-guide/

# Concatenate all deploy-guide pot files into a single one
# and store in doc/source/locale/
msgcat --use-first --sort-by-file doc/build/gettext-deploy-guide/*.pot \
    > doc/build/gettext/deploy-guide.pot

# Remove the temp directory so its individual pot files
# are not picked up and pushed to Zanata
rm -rf doc/build/gettext-deploy-guide/
