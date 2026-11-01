pipeline {
    agent any

    options {
        skipDefaultCheckout(true)
    }

    stages {
        stage('Checkout') {
            steps {
                deleteDir()
                checkout scm
                echo 'GitHub checkout successful!'
            }
        }

        stage('Python Environment') {
            steps {
                dir('backend') {
                    sh '''
                        python3 --version
                        python3 -m venv .venv
                        ./.venv/bin/python -m pip install -r requirements.txt
                    '''
                }
            }
        }

        stage('Run Backend Tests') {
            steps {
                dir('backend') {
                    sh '''
                        ./.venv/bin/python -m pytest -v
                    '''
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                    docker version
                    docker build -t devopsforge-api:${BUILD_NUMBER} -f backend/Dockerfile backend
                '''
            }
        }
    }

    post {
        success {
            echo 'DevOpsForge CI pipeline completed successfully!'
        }
        failure {
            echo 'CI pipeline failed. Check the test logs.'
        }
    }
}