from django.db import migrations, models
import django.db.models
import django.db.models.expressions


class Migration(migrations.Migration):
    dependencies = [
        ('booking', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='booking',
            unique_together=set(),
        ),
        migrations.AddConstraint(
            model_name='booking',
            constraint=models.UniqueConstraint(
                fields=('show', 'seat_number'),
                condition=django.db.models.Q(('status', 'booked')),
                name='unique_booked_seat_per_show',
            ),
        ),
    ]



