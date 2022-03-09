#! /bin/bash

# Install memoir in development mode inside a virtual environment and launch it.
# https://setuptools.pypa.io/en/latest/userguide/development_mode.html#development-mode

set -Eeuxo pipefail

VIRTUALENV_DIR=$(mktemp -d --suffix="_virtualenv")
trap "rm ${VIRTUALENV_DIR} -rf" EXIT

virtualenv --system-site-packages "${VIRTUALENV_DIR}"
source "${VIRTUALENV_DIR}/bin/activate"

pip install -e .
memoir "$@"
