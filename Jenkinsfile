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
    sh 'docker run --rm --net host -v ~/.ssh:/ansible/.host_ssh -v ansible:/ansible/playbooks philm/ansible_playbook  ansible/deploy.yml -i ansible/staging.ini'
  }
}
