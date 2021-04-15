In this file, I will explain how you should execute this application step by step:

0) Install python3 on your system.
1) Download Ngrok from https://ngrok.com/download.
2) Create a directory and call it "cooking-assistant". Then navigate to that directory.
3) Install python virtual environment by running "python3 -m venv virtual-env".
4) Activate the virtual environment by running "source virtual-env/bin/activate".
5) Copy all the files form the "python-code" directory to the "cooking-assistant" directory.
6) install the required packages by running "pip3 install -r requirements.txt"
6) Execute the python code by running "python3 main.py". After execution, you should get a message like
   "Running on http://127.0.0.1:8080/".
7) Open a new terminal and run "./ngrok http 8080" (8080 is the port number your got by running main.py).
8) A https url is generated for your application like "https://6c0239b0734f.ngrok.io/". Copy this url on your clipboard.
9) Go to https://dialogflow.cloud.google.com/
10) Create a new agent for yourself.
11) Click on the gear icon and then click on "Export and Import" tab.
12) Import the "cooking-assistant.zip" file.
13) Go to Fulfillment tab and replace the URL with "[the url on your clipboard]/webhook".
14) Save the agent.
15) You can test the application in the Dialogflow console.
16) If you like to test it on the Google Assistant simulator, do the following steps:
17) Click on Integration tab.
18) Click on "integration".
19) Click on "Test".
20) You will be redirected to the Google Assistant simulation environment and you can test the code their.
21) If you get an error message on Google Assistant simulator saying the app is not responding right now, go to the Develop tab -> Invocation and type "my app" for Display name. Save it and try again