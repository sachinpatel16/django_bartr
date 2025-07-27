# your_app/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model

from freelancing.custom_auth.models import Wallet, MerchantProfile

User = get_user_model()
@receiver(post_save, sender=User)
def create_user_wallet(sender, instance, created, **kwargs):
    if created:
        # Create wallet with 1000.00 for the new user
        content_type = ContentType.objects.get_for_model(User)
        Wallet.objects.create(
            balance=1000.00,
            content_type=content_type,
            object_id=instance.uuid
        )


@receiver(post_save, sender=MerchantProfile)
def update_user_merchant_flag(sender, instance, created, **kwargs):
    if created:
        user = instance.user
        user.is_merchant = True
        user.merchant_id = instance.id
        user.save(update_fields=["is_merchant", "merchant_id"])