#! /bin/bash

# Install memoir in development mode inside a virtual environment.
# https://setuptools.pypa.io/en/latest/userguide/development_mode.html#development-mode

set -Eeuxo pipefail

VIRTUALENV_DIR=$(mktemp -d --suffix="_virtualenv")

virtualenv "${VIRTUALENV_DIR}"
source "${VIRTUALENV_DIR}/bin/activate"

pip install -e .

echo "Now run:"
echo "source $VIRTUALENV_DIR/bin/activate" 
