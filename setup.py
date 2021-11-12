from distutils.core import setup  # Need this to handle modules
import py2exe
import socket
import threading
import pyaudio
from os import system

setup(console=['Client.py'])
