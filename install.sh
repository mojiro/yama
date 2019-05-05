#!/bin/bash

# Copyright (c) 2018 Michail Topaloudis
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

# Ansible artifacts

ANSIBLE_ETC='/etc/ansible'
ANSIBLE_DIR='/usr/lib/python2.7/dist-packages/ansible'
PROJECT_DIR=`pwd`

mkdir -p "${ANSIBLE_ETC}/config"
mkdir -p "${ANSIBLE_ETC}/playbooks"

ln -s "${PROJECT_DIR}/mikrotik/inventory.py" "${ANSIBLE_ETC}/inventory.py"
ln -s "${PROJECT_DIR}/mikrotik/config"       "${ANSIBLE_ETC}/config/mikrotik"
ln -s "${PROJECT_DIR}/mikrotik/playbooks"    "${ANSIBLE_ETC}/playbooks/mikrotik"

ln -s "${PROJECT_DIR}/mikrotik/modules"      "${ANSIBLE_DIR}/modules/network/mikrotik"
ln -s "${PROJECT_DIR}/mikrotik/module_utils" "${ANSIBLE_DIR}/module_utils/network/mikrotik"

ln -s "${PROJECT_DIR}/yama/modules"          "${ANSIBLE_DIR}/modules/utilities/yama"
ln -s "${PROJECT_DIR}/yama/module_utils"     "${ANSIBLE_DIR}/module_utils/yama"
