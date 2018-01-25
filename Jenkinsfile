node {
  stage('Clone repository') {
    checkout scm
  }

  def image

  stage('Build Docker image') {
    image = docker.build("johan1a/syncer:${env.BUILD_ID}")
  }

  /* stage('Push to Docker Hub') { */
  /*    docker.withRegistry('https://registry.hub.docker.com', 'docker-hub-credentials') { */
  /*       image.push() */
  /*       image.push('latest') */
  /*    } */
  /* } */

  stage('Deploy to staging') {
    sh 'ls -lah'
    sh 'ls -lah /var/jenkins_home/workspace/Syncer@2/ansible'
    sh 'ls -lah /var/jenkins_home/workspace/Syncer@2'
    sh 'pwd'
    sh 'docker run --rm --net host -v ~/.ssh:/ansible/.host_ssh -v $(pwd)/ansible:/ansible/playbooks philm/ansible_playbook deploy.yml -i staging.ini'
  }
}
