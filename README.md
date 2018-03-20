# The Process Virtual Machine

This project defines storage for an abstract _process_ in a company, and
implements a virtual machine that keeps track of the execution of instances of
the process.

## Develop

* `git clone https://github.com/tracsa/pvm.git && cd pvm`
* `virtualenv -p /usr/bin/python3 .env`
* `source .env/bin/activate`
* `pip install -r requirements.txt`
* `pytest`

## The PVM REST API

In this same repository you will find a flask application that exposes a REST
api for controling the PVM.

**How to run**

* `FLASK_APP=pvm.wsgi flask run`
