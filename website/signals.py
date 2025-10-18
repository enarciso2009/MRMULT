from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile, Empresa

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Cria automaticamente um profile vinculado ao User quando um novo usuario é criado

    """
    if created:
        empresa_padrao = Empresa.objects.first()
        Profile.objects.create(user=instance, empresa=empresa_padrao)
