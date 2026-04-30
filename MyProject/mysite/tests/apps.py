from django.apps import AppConfig


class TestsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tests'

    def ready(self):
        # Lazy imports inside ready() are safe.
        # BUT we MUST NOT do database queries here as it triggers early model loading.
        try:
            from django.contrib.auth.signals import user_logged_in
            from django.dispatch import receiver
            # We don't import models here at top level of ready() if we can help it

            @receiver(user_logged_in)
            def link_submissions(sender, request, user, **kwargs):
                from .models import Submission
                # 1. Link by submission IDs stored in session
                submission_ids = request.session.get('submission_ids')
                if submission_ids:
                    Submission.objects.filter(id__in=submission_ids, user__isnull=True).update(user=user)

                # 2. Link by original session key
                old_key = request.session.get('original_session_key')
                if old_key:
                    Submission.objects.filter(user__isnull=True, session_key=old_key).update(user=user)
        except ImportError:
            pass

        # Database initialization logic
        try:
            from django.db import connection
            table_name = 'tests_submission'
            columns_to_add = [
                ('user_id', 'integer'),
                ('finished_at', 'datetime'),
                ('total_score', 'integer'),
                ('session_key', 'varchar(40)'),
                ('magma_sealed_data', 'text'),
            ]

            with connection.cursor() as cursor:
                # Check if table exists
                cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';")
                if not cursor.fetchone():
                    return

                # Get existing columns
                cursor.execute(f"PRAGMA table_info({table_name});")
                existing_columns = [row[1] for row in cursor.fetchall()]

                for column_name, column_type in columns_to_add:
                    if column_name not in existing_columns:
                        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type};")
        except Exception:
            pass
