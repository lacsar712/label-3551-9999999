from django.core.management.base import BaseCommand
from management.models import TemporaryParkingPermit, TemporaryParkingApplication


class Command(BaseCommand):
    help = 'Updates temporary parking permit and application statuses for expired permits'

    def handle(self, *args, **kwargs):
        self.stdout.write("Updating expired temporary parking permits and applications...")

        permit_count = 0
        for permit in TemporaryParkingPermit.objects.filter(status='active'):
            if permit.update_status_if_expired():
                permit_count += 1

        app_count = 0
        for app in TemporaryParkingApplication.objects.filter(status='approved'):
            if app.update_expired_status():
                app_count += 1

        total = max(permit_count, app_count)
        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully updated {total} expired temporary parking records "
                f"({permit_count} permits, {app_count} applications)."
            )
        )
