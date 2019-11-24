#!/bin/bash

# Copyright (c) 2018 Michail Topaloudis
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

# Ansible artifacts

ANSIBLE_ETC='/etc/ansible'
ANSIBLE_DIR='/usr/lib/python2.7/dist-packages/ansible'
PROJECT_DIR=`pwd`

mkdir -p "${ANSIBLE_ETC}/config"
mkdir -p "${ANSIBLE_ETC}/playbooks"

ln -s "${PROJECT_DIR}/ansible/config"       "${ANSIBLE_ETC}/config/yama"
ln -s "${PROJECT_DIR}/ansible/playbooks"    "${ANSIBLE_ETC}/playbooks/yama"

ln -s "${PROJECT_DIR}/ansible/modules"      "${ANSIBLE_DIR}/modules/remote_management/yama"
ln -s "${PROJECT_DIR}/ansible/module_utils" "${ANSIBLE_DIR}/module_utils/remote_management/yama"
