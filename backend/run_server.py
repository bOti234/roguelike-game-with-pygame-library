import os
import sys
from django.core.management import execute_from_command_line

def run_django_server():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.settings')
    sys.argv = ['manage.py', 'runserver', '0.0.0.0:8000']
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    # Change the current working directory to the one containing manage.py
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    run_django_server()