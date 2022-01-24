pipeline {
  agent none
  environment {
    SLACK_CHANNEL = "edge"
    SLACK_TYPE = "RD"
    MAJOR_VERSION = "1"
    MINOR_VERSION = "2"
    NEXUS_REPOSITORY = "HermesGM-Edge"
    NEXUS_ARTIFACT_ID = "HermesGM-Edge"
    NEXUS_FILE_TYPE = "tar.gz"
  }
  stages {
    stage('Testing') {
      when {
        beforeAgent true
        anyOf {
          changeRequest target: 'master'
          changeRequest target: 'release/*'
          branch 'feature/*'
          branch 'bug/*'
        }
      }
      agent {
        label "rd-ci"
      }
      steps {
        container('ci') {
          sh 'make build MAJOR_VERSION=$MAJOR_VERSION MINOR_VERSION=$MINOR_VERSION BUILDNUM=$BUILD_NUMBER -j4'
          sh 'make test -j4'
        }
      }
    }
    stage('Push Snapshot Artifact') {
      when {
        beforeAgent true
        branch 'master'
      }
      agent {
        label "rd-ci"
      }
      steps {
        container('ci') {
          sh 'make clean'
          sh 'make build MAJOR_VERSION=$MAJOR_VERSION MINOR_VERSION=$MINOR_VERSION BUILDNUM=$BUILD_NUMBER -j4'
        }
        nexusUploader("$NEXUS_REPOSITORY", false, "$NEXUS_ARTIFACT_ID", "${env.MAJOR_VERSION}.${env.MINOR_VERSION}.$BUILD_NUMBER", "./output/build.tar.gz.${env.MAJOR_VERSION}.${env.MINOR_VERSION}.$BUILD_NUMBER", "$NEXUS_FILE_TYPE")
      }
    }
    stage('Push Release Artifact') {
      when {
        beforeAgent true
        branch 'release/*'
      }
      agent {
        label "rd-ci"
      }
      steps {
        container('ci') {
          sh 'make clean'
          sh 'make build MAJOR_VERSION=$MAJOR_VERSION MINOR_VERSION=$MINOR_VERSION BUILDNUM=$BUILD_NUMBER -j4'
        }
        nexusUploader("$NEXUS_REPOSITORY", true, "$NEXUS_ARTIFACT_ID", "${env.MAJOR_VERSION}.${env.MINOR_VERSION}.$BUILD_NUMBER", "./output/build.tar.gz.${env.MAJOR_VERSION}.${env.MINOR_VERSION}.$BUILD_NUMBER", "tar.gz")
      }
    }
  }
  post {
    always {
      slackNotification("$SLACK_CHANNEL")
    }
  }
}
