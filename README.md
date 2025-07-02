# 2025-SiteConneCT
Assignment for the 2025 edition of the "Web Development and the Semantic Web" course, by Alan Medina Wehbe, Eduardo Marchese Perim, Guilherme Dayrell Cruz Soares and Victor Soares Setubal Wingler Lucas.

#Como rodar a primeira vez:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export FLASK_APP=manage.py      
flask db-init
flask db-migrate 
flask db-upgrade
python install.py
python run.py 
```
