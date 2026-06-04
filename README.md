# cloud-cost-optimizer
aws and azure resource optimizer utility

creating python virtual environment follow these steps

python -m venv ovenv

activate virtual environment

C:\cloud-cost-optimizer\ovenv\Scripts\activate

Starting the server with below commands.

install the required packages with below command

pip install -r requirements.txt

run the server app with below command

uvicorn main:app --reload

Check the API and test the same with below URL in browser.

http://127.0.0.1:8000/docs

Starting the client with below command

streamlit run app.py

http://localhost:8501


Test by uploading the desired test .csv files available in the same folder.

you can export any account resources csv files and let them analyze using this tool.
if you want to cover up more resource criterias then add the relevant fields in the python file.