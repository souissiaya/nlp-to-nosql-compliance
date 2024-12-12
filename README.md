python3.12 -m venv venv
source venv/bin/activate 
pip3.12 install -r requirements.txt
python3.12 -m spacy download en_core_web_sm 
python3.12 init_db/populate_db.py
python3.12 app/compliance_query.py  