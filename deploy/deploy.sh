#!/bin/sh
echo whyyyy1
SYNCER_HOSTS=archlinux
ssh -i /var/jenkins_home/.ssh_host/id_rsa johan@urdatorn 'mkdir -p ~/syncer/data/'
echo whyyyy2
scp -i /var/jenkins_home/.ssh_host/id_rsa docker-compose.yml johan@urdatorn:syncer/
echo whyyyy3
ssh -i /var/jenkins_home/.ssh_host/id_rsa johan@urdatorn 'cd ~/syncer/ && docker-compose up'
echo whyyyy4!!!!!!!!!!!

