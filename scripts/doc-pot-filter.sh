#!/bin/bash

set -e

# Extract messages from the deploy-guide
sphinx-build -b gettext \
    doc/source/deploy-guide/source \
    doc/build/gettext/
