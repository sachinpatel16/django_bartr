# Generated by Django 4.2 on 2025-07-28 17:10

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("voucher", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="voucher",
            name="uuid",
            field=models.UUIDField(
                default=uuid.uuid4,
                error_messages={"unique": "A user with that uuid already exists."},
                help_text="Required. A 32 hexadecimal digits number as specified in RFC 4122",
                unique=True,
                verbose_name="uuid",
            ),
        ),
    ]
