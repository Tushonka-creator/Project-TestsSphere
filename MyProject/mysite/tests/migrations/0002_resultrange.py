from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [
        ('tests', '0001_initial'),
    ]
    operations = [
        migrations.CreateModel(
            name='ResultRange',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('min_score', models.IntegerField()),
                ('max_score', models.IntegerField()),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('order', models.PositiveIntegerField(default=0)),
                ('test', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='result_ranges', to='tests.test')),
            ],
            options={'ordering': ['order', 'min_score', 'id']},
        ),
    ]
