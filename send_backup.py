from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.mail import EmailMessage
from pathlib import Path
import zipfile
from datetime import datetime
import os

class Command(BaseCommand):
    help = "Email SQLite DB backup and clean temp files"

    def handle(self, *args, **kwargs):
        base_dir = Path(settings.BASE_DIR)

        # DB path
        db_path = base_dir / "db.sqlite3"

        if not db_path.exists():
            self.stderr.write(self.style.ERROR("db.sqlite3 not found"))
            return

        # tmp directory inside BASE_DIR
        tmp_dir = base_dir / "tmp"
        tmp_dir.mkdir(exist_ok=True)

        # zip file path
        zip_name = f"db_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        zip_path = tmp_dir / zip_name

        try:
            # Create zip
            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(db_path, arcname="db.sqlite3")

            # Email
            email = EmailMessage(
                subject="Django SQLite DB Backup",
                body="Attached is the automated SQLite database backup.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=["bhadrinath95@gmail.com"],
            )

            email.attach_file(zip_path)
            email.send()

            self.stdout.write(self.style.SUCCESS("Backup emailed successfully"))

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Backup failed: {e}"))

        finally:
            # Cleanup: delete zip file
            if zip_path.exists():
                zip_path.unlink()
                self.stdout.write("Temporary zip file deleted")
