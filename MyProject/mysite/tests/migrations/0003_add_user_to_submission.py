from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


def add_columns_if_not_exists(apps, schema_editor):
    table_name = 'tests_submission'
    columns_to_add = [
        ('user_id', 'integer'),
        ('finished_at', 'datetime'),
        ('total_score', 'integer'),
        ('session_key', 'varchar(40)'),
    ]

    with schema_editor.connection.cursor() as cursor:
        cursor.execute(f"PRAGMA table_info({table_name});")
        existing_columns = [row[1] for row in cursor.fetchall()]

        for column_name, column_type in columns_to_add:
            if column_name not in existing_columns:
                cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type};")
                print(f"Column {column_name} added to {table_name}")
            else:
                print(f"Column {column_name} already exists in {table_name}")


class Migration(migrations.Migration):
    dependencies = [
        ('tests', '0002_resultrange'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunPython(add_columns_if_not_exists),
            ],
            state_operations=[
                migrations.AddField(
                    model_name='submission',
                    name='user',
                    field=models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name='submissions',
                        to=settings.AUTH_USER_MODEL
                    ),
                ),
            ],
        ),
    ]
