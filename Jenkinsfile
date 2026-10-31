
pipeline {
    agent any

    stages {

        // Stage 1: Checkout source code from GitHub
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        // Stage 2: Verify project source code
        stage('Verify Source Code') {
            steps {
                sh '''
                    echo "Checking project directory..."
                    pwd

                    echo "Listing project files..."
                    ls -la

                    echo "Checking backend directory..."
                    ls -la backend
                '''
            }
        }

        // Stage 3: Verify Python installation
        stage('Python Environment Check') {
            steps {
                sh '''
                    echo "Checking Python installation..."

                    python3 --version

                    echo "Checking pip installation..."
                    python3 -m pip --version

                    echo "Testing Python execution..."
                    python3 -c "print('Python execution successful!')"

                    echo "Python environment verification completed!"
                '''
            }
        }

    }
}
