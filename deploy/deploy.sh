#!/bin/sh
ssh -i /var/jenkins_home/.ssh_host/id_rsa johan@urdatorn 'mkdir -p ~/syncer/data/'
scp -i /var/jenkins_home/.ssh_host/id_rsa docker-compose.yml johan@urdatorn:syncer/
ssh -i /var/jenkins_home/.ssh_host/id_rsa johan@urdatorn 'cd syncer/ && docker-compose pull'
ssh -i /var/jenkins_home/.ssh_host/id_rsa johan@urdatorn 'cd && cd syncer/ && SYNCER_HOSTS=archlinux docker-compose up -d'

