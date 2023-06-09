# Generated by Django 4.1.7 on 2023-03-02 19:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shopapp', '0004_order_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductToOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('count', models.PositiveSmallIntegerField()),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='shopapp.order')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='shopapp.product')),
            ],
        ),
    ]
