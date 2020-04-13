# Installation
The example scrips in this folder make use of various python packages.  To install we recommend using pip and the provided `requirements.txt`.  We also recommend using virtualenv to encapsulate the run-time environment.  For example:

```bash
$ pip install virtualenv
$ python -m virtualenv venv
$ source ./venv/bin/activate
(venv) $ pip install -r requirements.txt
```

# Usage
Assuming you followed the installation instructions above, running the scripts looks something like this:

```bash
$ source ./venv/bin/activate
(venv) $ ./user-stats.py
```
