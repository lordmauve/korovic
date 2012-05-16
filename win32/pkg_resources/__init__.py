"""Redefine some stuff we rely on in pkg_resources to be less magical (for py2exe package"""
import os.path

def fname(name, file):
    name = '\\'.join(name.split('.')[:-1])
    return os.path.join(name, file)

def resource_string(name, file):
     return open(fname(name, file), 'rb').read()

def resource_stream(name, file):
    return open(fname(name, file), 'rb')
