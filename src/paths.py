import os.path

SRC = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SRC)
TEMPLATES = os.path.join(ROOT, "templates")
DATA = os.path.join(ROOT, "data")

def makedir_if_not_exists(dirname):
    if not os.path.isdir(dirname):
        os.makedirs(dirname)
