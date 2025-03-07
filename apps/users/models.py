from django.contrib.auth.models import AbstractUser
from django.db import models
import os
from django.dispatch import receiver
from django.db.models.signals import pre_save, post_delete

class User(AbstractUser):

    # Adds an extra fields to Django user model

    email = models.EmailField(unique=True)
    is_verified = models.BooleanField(default=False)
    mails_count = models.IntegerField(default=0)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)

@receiver(pre_save, sender=User)
def delete_old_profile_image(sender, instance, **kwargs):
    """
    Deletes the old profile image from the file system when a new image is uploaded.
    This signal is triggered before saving the User model.
    """
    # If this is a new user, there's no existing image to delete.
    if not instance.pk:
        return

    try:
        old_instance = User.objects.get(pk=instance.pk)
    except User.DoesNotExist:
        return

    old_image = old_instance.profile_image
    new_image = instance.profile_image

    # If an old image exists and it's different from the new one, remove the old file.
    if old_image and old_image != new_image:
        if os.path.isfile(old_image.path):
            os.remove(old_image.path)

@receiver(post_delete, sender=User)
def delete_profile_image_on_delete(sender, instance, **kwargs):
    """
    Deletes the profile image file from the file system when the User is deleted.
    This signal is triggered after deleting the User model.
    """
    if instance.profile_image and os.path.isfile(instance.profile_image.path):
        os.remove(instance.profile_image.path)
