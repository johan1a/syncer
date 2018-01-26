#!/bin/sh
echo whyyyy1
ssh -i /var/lib/jenkins_home/.ssh_host/id_rsa johan@urdatorn 'mkdir -p ~/syncer/data/'
echo whyyyy2
scp -i /var/lib/jenkins_home/.ssh_host/id_rsa docker-compose.yml johan@urdatorn:syncer/
echo whyyyy3
ssh -i /var/lib/jenkins_home/.ssh_host/id_rsa johan@urdatorn 'cd ~/syncer/ && docker-compose up'
echo whyyyy4!!!!!!!!!!!

