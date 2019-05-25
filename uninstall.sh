#!/bin/bash

# Copyright (c) 2018 Michail Topaloudis
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

# Ansible artifacts

ANSIBLE_ETC='/etc/ansible'
ANSIBLE_DIR='/usr/lib/python2.7/dist-packages/ansible'

rm -f "${ANSIBLE_ETC}/inventory.py"
rm -f "${ANSIBLE_ETC}/config/mikrotik"
rm -f "${ANSIBLE_ETC}/playbooks/mikrotik"

rm -f "${ANSIBLE_DIR}/modules/network/mikrotik"
rm -f "${ANSIBLE_DIR}/module_utils/network/mikrotik"

rm -f "${ANSIBLE_DIR}/modules/utilities/yama"
rm -f "${ANSIBLE_DIR}/module_utils/yama"
