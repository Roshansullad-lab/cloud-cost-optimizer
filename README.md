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

Cloud docker deployed service can be accessed with below URL and for testing you can upload the .csv files from the 
below path

server running on render docker containers URL. it might take 5 seconds to startup docker container on fresh request.
so if link is not working try refreshing after 5 seconds.

https://cloud-cost-optimizer-k8pz.onrender.com/docs

Mock data files for aws and azure resources you can download these and try in the above API testing flow
use AWS and Azure keywords tags to try out different cloud services

https://github.com/Roshansullad-lab/cloud-cost-optimizer/blob/main/aws_inventory.csv

https://github.com/Roshansullad-lab/cloud-cost-optimizer/blob/main/aws_inventory1.csv

https://github.com/Roshansullad-lab/cloud-cost-optimizer/blob/main/azure_inventory.csv






