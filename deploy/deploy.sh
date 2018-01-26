#!/bin/sh
ssh -i /var/lib/jenkins_home/.ssh_host/id_rsa johan@urdatorn 'mkdir -p ~/syncer/data/'
scp -i /var/lib/jenkins_home/.ssh_host/id_rsa docker-compose.yml johan@urdatorn:syncer/
ssh -i /var/lib/jenkins_home/.ssh_host/id_rsa johan@urdatorn 'cd ~/syncer/ && docker-compose up'

