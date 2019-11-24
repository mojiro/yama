# yama
Yet Another Mikrotik module for Ansible

## Introduction
I created this project to provide support for Mikrotik using SSH. Some
advantages are:
- SSH Private keys
- SFTP Upload/Downloads
- Always encrypted
- Using common libraries like paramiko
- Commands with live output (ex. Ping)

The real drawback, is that I have to handle carefully all the requests,
acting like an API.

## Supported Operations
- Command Execution with tracking (changed, failed)
- SFTP Recursive Upload/Download

## Documentation
Documentation, currently is limited in the example playbooks. At some point, I
will try to write some examples with cases studies.

## Issues
For any problem please create an [issue](https://github.com/mojiro/yama/issues/new)

## Related projects
- https://github.com/CFSworks/ansible-routeros
- https://github.com/zahodi/ansible-mikrotik
