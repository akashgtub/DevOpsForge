pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm

                echo 'GitHub repository cloned successfully!'
            }
        }

        stage('Verify Source Code') {
            steps {
                sh 'pwd'
                sh 'ls -la'
                sh 'ls -la backend'
            }
        }
    }
}