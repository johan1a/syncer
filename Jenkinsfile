node {
    checkout scm
    def image = docker.build("johan1a/syncer:${env.BUILD_ID}")
    image.push()
    image.push('latest')
}
