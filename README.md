# brand-microservices

pyenv install 3.10.7
pyenv global 3.10.7

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

Run:
uvicorn main:app --reload
