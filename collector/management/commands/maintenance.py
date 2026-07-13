from django.core.management.base import BaseCommand
from collector.services.maintenance import create_backup, evaluate_sources, process_positive_discovery, purge_old_content


class Command(BaseCommand):
    help = "Run daily source evaluation, discovery, retention and backup"

    def handle(self, *args, **kwargs):
        evaluate_sources()
        process_positive_discovery()
        count = purge_old_content()
        backup = create_backup()
        self.stdout.write(self.style.SUCCESS(f"Maintenance complete: purged={count}, backup={backup}"))

