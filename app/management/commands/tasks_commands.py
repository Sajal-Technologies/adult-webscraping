from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from app.models import RunScript
from django.utils import timezone  
from datetime import datetime, timedelta

class Command(BaseCommand):
    def handle(self, *args, **options):

        List_of_working_commands = [
            "sexmax",
            "revsharecash",
            "handjob",
            "fivek",
        ]
            
        current_datetime = timezone.now()
        run_script = RunScript.objects.first()
        
        only_login = True
        next_run_time = run_script.last_run + timedelta(hours=run_script.datetime)
        if next_run_time < current_datetime:
            only_login = False
            print(f"Run script at {run_script.datetime} hours is ready to run.")
        else:
            print(f"Run script at {run_script.datetime} hours is not ready to run yet.")
        
        for command in List_of_working_commands :
            call_command(command, '--only_login', only_login)