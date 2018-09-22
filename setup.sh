#!/bin/bash

# Copyright (c) 2018 Michail Topaloudis
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

ANSIBLE_ETC='/etc/ansible'
ANSIBLE_DIR='/usr/lib/python2.7/dist-packages/ansible'
PROJECT_DIR='/usr/local/src/ansible-mikrotik'

mkdir -p "${ANSIBLE_ETC}/playbooks"
ln    -s "${PROJECT_DIR}/playbooks"    "${ANSIBLE_ETC}/playbooks/mikrotik"
ln    -s "${PROJECT_DIR}/inventory.py" "${ANSIBLE_ETC}/inventory.py"

mkdir -p "${ANSIBLE_ETC}/config"
ln    -s "${PROJECT_DIR}/config"       "${ANSIBLE_ETC}/config/mikrotik"

ln    -s "${PROJECT_DIR}/modules"      "${ANSIBLE_DIR}/modules/network/mikrotik"
ln    -s "${PROJECT_DIR}/module_utils" "${ANSIBLE_DIR}/module_utils/network/mikrotik"
