#!/bin/bash

# Copyright (c) 2018 Michail Topaloudis
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

ANSIBLE_ETC='/etc/ansible'
ANSIBLE_DIR='/usr/lib/python2.7/dist-packages/ansible'

rm "${ANSIBLE_ETC}/playbooks/mikrotik"
rm "${ANSIBLE_ETC}/inventory.py"
rm "${ANSIBLE_ETC}/config/mikrotik"
rm "${ANSIBLE_DIR}/modules/network/mikrotik"
rm "${ANSIBLE_DIR}/module_utils/network/mikrotik"
rm "${ANSIBLE_DIR}/modules/utilities/yama"
rm "${ANSIBLE_DIR}/module_utils/yama"
