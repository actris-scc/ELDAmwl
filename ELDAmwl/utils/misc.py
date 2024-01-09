import os


def current_environment():
    if 'env' in os.environ:
        return os.environ['env']
    else:
        return 'Production'
