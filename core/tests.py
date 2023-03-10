from typing import Any

from django.db import connection
from django.test.runner import DiscoverRunner


class TestRunner(DiscoverRunner):
    def teardown_databases(self, old_config: Any, **kwargs: Any) -> None:
        with connection.cursor() as cursor:
            cursor.execute(
                f"""SELECT
                pg_terminate_backend(pid) FROM pg_stat_activity WHERE
                pid <> pg_backend_pid() AND
                pg_stat_activity.datname =
                  '{connection.settings_dict["NAME"]}';"""
            )
            print(f"Killed {len(cursor.fetchall())} stale connections.")
        super().teardown_databases(old_config, **kwargs)
