from django.db import migrations, models
import django.core.validators


digit_validator = django.core.validators.RegexValidator('^\\d+$', 'Digits only.')


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='PhoneNumber',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('area_code', models.CharField(max_length=3, validators=[digit_validator])),
                ('local_number', models.CharField(max_length=7, validators=[digit_validator])),
                ('cost', models.DecimalField(decimal_places=2, max_digits=10)),
            ],
            options={'ordering': ['area_code', 'local_number']},
        ),
        migrations.AddConstraint(
            model_name='phonenumber',
            constraint=models.UniqueConstraint(fields=('area_code', 'local_number'), name='unique_area_code_local_number'),
        ),
        migrations.AddIndex(
            model_name='phonenumber',
            index=models.Index(fields=['area_code'], name='idx_area_code'),
        ),
        migrations.AddIndex(
            model_name='phonenumber',
            index=models.Index(fields=['local_number'], name='idx_local_number'),
        ),
    ]

