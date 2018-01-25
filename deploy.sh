#!/bin/sh
docker run --rm -it --net host -v ~/.ssh:/ansible/.host_ssh -v ansible:/ansible/playbooks philm/ansible_playbook  ansible/deploy.yml -i ansible/staging.ini

