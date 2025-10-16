from django.db import models
from django.contrib.auth.models import User


class ProfilUtilisateur(models.Model):
    """Extension du modèle User pour le profil utilisateur"""
    utilisateur = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profil',
        verbose_name="Utilisateur"
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        verbose_name="Avatar"
    )
    biographie = models.TextField(blank=True, verbose_name="Biographie")
    ville = models.CharField(max_length=100, blank=True, verbose_name="Ville")
    pays = models.CharField(max_length=100, blank=True, verbose_name="Pays")
    site_web = models.URLField(blank=True, verbose_name="Site web")

    # Préférences
    theme_prefere = models.CharField(
        max_length=20,
        choices=[
            ('clair', 'Thème clair'),
            ('sombre', 'Thème sombre')
        ],
        default='clair',
        verbose_name="Thème préféré"
    )
    langue = models.CharField(
        max_length=10,
        choices=[
            ('fr', 'Français'),
            ('en', 'English'),
            ('es', 'Español')
        ],
        default='fr',
        verbose_name="Langue"
    )

    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    date_modification = models.DateTimeField(auto_now=True, verbose_name="Date de modification")

    class Meta:
        verbose_name = "Profil utilisateur"
        verbose_name_plural = "Profils utilisateurs"

    def __str__(self):
        return f"Profil de {self.utilisateur.username}"