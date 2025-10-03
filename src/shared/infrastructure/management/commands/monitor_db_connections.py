from django.core.management.base import BaseCommand
from django.db import connection
import time


class Command(BaseCommand):
    help = "Monitor database connections"

    def add_arguments(self, parser):
        parser.add_argument(
            "--interval",
            type=int,
            default=30,
            help="Monitoring interval in seconds (default: 30)",
        )

    def handle(self, *args, **options):
        interval = options["interval"]

        self.stdout.write(
            self.style.SUCCESS(
                f"Starting DB connection monitoring (interval: {interval}s)"
            )
        )

        try:
            while True:
                with connection.cursor() as cursor:
                    # Get current connection count
                    cursor.execute(
                        """
                        SELECT count(*) as active_connections
                        FROM pg_stat_activity
                        WHERE state = 'active'
                    """
                    )
                    active_count = cursor.fetchone()[0]

                    # Get total connection count
                    cursor.execute(
                        """
                        SELECT count(*) as total_connections
                        FROM pg_stat_activity
                    """
                    )
                    total_count = cursor.fetchone()[0]

                    # Get max connections setting
                    cursor.execute("SHOW max_connections")
                    max_connections = int(cursor.fetchone()[0])

                    # Get connections by application
                    cursor.execute(
                        """
                        SELECT application_name, count(*) as conn_count
                        FROM pg_stat_activity
                        WHERE application_name IS NOT NULL
                        GROUP BY application_name
                        ORDER BY conn_count DESC
                    """
                    )
                    app_connections = cursor.fetchall()

                    self.stdout.write(
                        f"Active: {active_count}, Total: {total_count}/{max_connections} "
                        f"({(total_count/max_connections)*100:.1f}%)"
                    )

                    # if app_connections:
                    #     self.stdout.write("By application:")
                    #     for app_name, count in app_connections:
                    #         self.stdout.write(f"  {app_name}: {count}")

                    if total_count > max_connections * 0.8:
                        self.stdout.write(
                            self.style.WARNING(
                                f"WARNING: Connection usage is high ({total_count}/{max_connections})"
                            )
                        )

                time.sleep(interval)

        except KeyboardInterrupt:
            self.stdout.write(self.style.SUCCESS("Monitoring stopped"))
