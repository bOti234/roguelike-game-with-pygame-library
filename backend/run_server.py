import os
import sys
from django.core.management import execute_from_command_line

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'roguelikegame.settings')
    try:
        from django.core.management.commands.runserver import Command as runserver
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    runserver.default_addr = '127.0.0.1'
    runserver.default_port = '8000'
    
    execute_from_command_line([sys.argv[0], 'runserver'])

if __name__ == '__main__':
    main()