In this file, I will explain how you should execute this application step by step:

1) Download Ngrok from https://ngrok.com/download
2) Install python virtual environment by running "python3 -m venv virtual-env"
3) Activate the virtual environment by running " source virtual-env/bin/activate"
4) Go to directory you install virtual-env
5) Copy this python package in the current directory (the one having virtual-env)
5) install the requirement packages for running the code by running " pip install -r requirements.txt"
6) Execute the python code by running "python3 main.py". After executing the main.py, you should get a message like
   "Running on http://127.0.0.1:8080/".
7) Open a new terminal and run "./ngrok http 8080" (8080 is the port your application is running)
8) It generates a https url for your application like "https://6c0239b0734f.ngrok.io/". Copy the url on your clipboard.
9) Go to https://dialogflow.cloud.google.com/
10) Create a new agent for your self
11) Click on the gear icon and then click on "Export and Import" tab
12) Import the "cooking-assistant.zip"
13) Go to Fulfillment tab and replace the URL with "[the https URL you got from ngrok]/webhook"
14) Save the agent
15) You can run the application of the Dialogflow Console
16) If you like to test it on the Google Assistant simulator do the following steps
17) Click on Integration tab
18) Click on "integration"
19) Click on "Test"
20) You will be redirected to the Google Assistant simulation environment and you can test the code their