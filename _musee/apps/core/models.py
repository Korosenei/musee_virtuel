from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator


class Categorie(models.Model):
    """Catégories de musée : Art, Science, Musique, Cinéma, Environnement"""
    nom = models.CharField(max_length=100, unique=True, verbose_name="Nom")
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(verbose_name="Description")
    icone = models.ImageField(
        upload_to='categories/icones/',
        blank=True,
        null=True,
        verbose_name="Icône"
    )
    couleur = models.CharField(
        max_length=7,
        default='#3B82F6',
        help_text='Couleur hexadécimale (ex: #FF5733)',
        verbose_name="Couleur"
    )
    ordre = models.IntegerField(
        default=0,
        help_text="Ordre d'affichage",
        verbose_name="Ordre"
    )
    est_active = models.BooleanField(default=True, verbose_name="Active")

    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    date_modification = models.DateTimeField(auto_now=True, verbose_name="Date de modification")

    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"
        ordering = ['ordre', 'nom']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nom)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nom


class Artiste(models.Model):
    """Artistes ou créateurs"""
    nom = models.CharField(max_length=200, verbose_name="Nom")
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    biographie = models.TextField(blank=True, verbose_name="Biographie")
    annee_naissance = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Année de naissance"
    )
    annee_deces = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Année de décès"
    )
    nationalite = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Nationalité"
    )
    photo = models.ImageField(
        upload_to='artistes/',
        blank=True,
        null=True,
        verbose_name="Photo"
    )
    site_web = models.URLField(blank=True, verbose_name="Site web")

    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    date_modification = models.DateTimeField(auto_now=True, verbose_name="Date de modification")

    class Meta:
        verbose_name = "Artiste"
        verbose_name_plural = "Artistes"
        ordering = ['nom']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nom)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nom


class Salle(models.Model):
    """Salles virtuelles du musée"""
    nom = models.CharField(max_length=200, verbose_name="Nom")
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField(verbose_name="Description")
    categorie = models.ForeignKey(
        Categorie,
        on_delete=models.CASCADE,
        related_name='salles',
        verbose_name="Catégorie"
    )

    # Dimensions de la salle (pour le rendu 3D)
    largeur = models.FloatField(
        default=20.0,
        help_text='Largeur en mètres',
        verbose_name="Largeur"
    )
    longueur = models.FloatField(
        default=20.0,
        help_text='Longueur en mètres',
        verbose_name="Longueur"
    )
    hauteur = models.FloatField(
        default=4.0,
        help_text='Hauteur en mètres',
        verbose_name="Hauteur"
    )

    # Apparence visuelle
    couleur_murs = models.CharField(
        max_length=7,
        default='#FFFFFF',
        verbose_name="Couleur des murs"
    )
    texture_sol = models.ImageField(
        upload_to='salles/textures/',
        blank=True,
        null=True,
        verbose_name="Texture du sol"
    )
    eclairage = models.CharField(
        max_length=50,
        choices=[
            ('naturel', 'Lumière naturelle'),
            ('chaud', 'Éclairage chaud'),
            ('froid', 'Éclairage froid'),
            ('tamisé', 'Éclairage tamisé')
        ],
        default='naturel',
        verbose_name="Éclairage"
    )

    ordre = models.IntegerField(default=0, verbose_name="Ordre")
    est_active = models.BooleanField(default=True, verbose_name="Active")

    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    date_modification = models.DateTimeField(auto_now=True, verbose_name="Date de modification")

    class Meta:
        verbose_name = "Salle"
        verbose_name_plural = "Salles"
        ordering = ['ordre', 'nom']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nom)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nom} - {self.categorie.nom}"


class Oeuvre(models.Model):
    """Œuvre ou objet exposé dans le musée"""
    titre = models.CharField(max_length=300, verbose_name="Titre")
    slug = models.SlugField(max_length=300, unique=True, blank=True)
    description = models.TextField(verbose_name="Description")
    description_courte = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="Description courte"
    )

    # Relations
    artiste = models.ForeignKey(
        Artiste,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='oeuvres',
        verbose_name="Artiste"
    )
    categorie = models.ForeignKey(
        Categorie,
        on_delete=models.CASCADE,
        related_name='oeuvres',
        verbose_name="Catégorie"
    )
    salle = models.ForeignKey(
        Salle,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='oeuvres',
        verbose_name="Salle"
    )

    # Informations temporelles
    annee = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Année de création"
    )
    epoque = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Époque"
    )

    # Médias
    image_miniature = models.ImageField(
        upload_to='oeuvres/miniatures/',
        verbose_name="Image miniature"
    )
    image_haute_resolution = models.ImageField(
        upload_to='oeuvres/hd/',
        blank=True,
        null=True,
        verbose_name="Image haute résolution"
    )
    modele_3d = models.FileField(
        upload_to='modeles_3d/',
        blank=True,
        null=True,
        help_text='Format .glb ou .gltf',
        verbose_name="Modèle 3D"
    )
    audio_guide = models.FileField(
        upload_to='audio/',
        blank=True,
        null=True,
        verbose_name="Guide audio"
    )
    video = models.FileField(
        upload_to='videos/',
        blank=True,
        null=True,
        verbose_name="Vidéo"
    )
    lien_video_externe = models.URLField(
        blank=True,
        help_text='Lien YouTube ou Vimeo',
        verbose_name="Lien vidéo externe"
    )

    # Position 3D dans la salle virtuelle
    position_x = models.FloatField(
        default=0,
        verbose_name="Position X"
    )
    position_y = models.FloatField(
        default=0,
        verbose_name="Position Y"
    )
    position_z = models.FloatField(
        default=0,
        verbose_name="Position Z"
    )
    rotation = models.FloatField(
        default=0,
        help_text='Rotation en degrés',
        verbose_name="Rotation"
    )
    echelle = models.FloatField(
        default=1.0,
        validators=[MinValueValidator(0.1), MaxValueValidator(10.0)],
        verbose_name="Échelle"
    )

    # Métadonnées supplémentaires
    dimensions = models.CharField(
        max_length=100,
        blank=True,
        help_text='Ex: 120 x 80 cm',
        verbose_name="Dimensions"
    )
    technique = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Technique"
    )
    materiau = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Matériau"
    )
    collection = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Collection"
    )
    numero_inventaire = models.CharField(
        max_length=50,
        blank=True,
        unique=True,
        verbose_name="Numéro d'inventaire"
    )

    # Métadonnées JSON pour flexibilité
    metadonnees = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Métadonnées"
    )

    # Statut et visibilité
    est_visible = models.BooleanField(default=True, verbose_name="Visible")
    est_mise_en_avant = models.BooleanField(
        default=False,
        verbose_name="Mise en avant"
    )
    nombre_vues = models.IntegerField(default=0, verbose_name="Nombre de vues")

    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    date_modification = models.DateTimeField(auto_now=True, verbose_name="Date de modification")

    class Meta:
        verbose_name = "Œuvre"
        verbose_name_plural = "Œuvres"
        ordering = ['-date_creation']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['categorie', 'est_visible']),
            models.Index(fields=['-nombre_vues']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titre)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.titre

    def incrementer_vues(self):
        """Incrémenter le compteur de vues"""
        self.nombre_vues += 1
        self.save(update_fields=['nombre_vues'])


class Favori(models.Model):
    """Œuvres favorites des utilisateurs"""
    utilisateur = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favoris',
        verbose_name="Utilisateur"
    )
    oeuvre = models.ForeignKey(
        Oeuvre,
        on_delete=models.CASCADE,
        related_name='favoris',
        verbose_name="Œuvre"
    )
    note = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Note"
    )
    commentaire = models.TextField(blank=True, verbose_name="Commentaire")
    date_ajout = models.DateTimeField(auto_now_add=True, verbose_name="Date d'ajout")

    class Meta:
        verbose_name = "Favori"
        verbose_name_plural = "Favoris"
        unique_together = ('utilisateur', 'oeuvre')
        ordering = ['-date_ajout']

    def __str__(self):
        return f"{self.utilisateur.username} - {self.oeuvre.titre}"


class Visite(models.Model):
    """Historique des visites des utilisateurs"""
    utilisateur = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='visites',
        verbose_name="Utilisateur"
    )
    oeuvre = models.ForeignKey(
        Oeuvre,
        on_delete=models.CASCADE,
        related_name='visites',
        verbose_name="Œuvre"
    )
    date_visite = models.DateTimeField(auto_now_add=True, verbose_name="Date de visite")
    duree_secondes = models.IntegerField(
        default=0,
        verbose_name="Durée (secondes)"
    )

    class Meta:
        verbose_name = "Visite"
        verbose_name_plural = "Visites"
        ordering = ['-date_visite']
        indexes = [
            models.Index(fields=['utilisateur', '-date_visite']),
        ]

    def __str__(self):
        return f"{self.utilisateur.username} - {self.oeuvre.titre} ({self.date_visite})"


class Commentaire(models.Model):
    """Commentaires sur les œuvres"""
    utilisateur = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='commentaires',
        verbose_name="Utilisateur"
    )
    oeuvre = models.ForeignKey(
        Oeuvre,
        on_delete=models.CASCADE,
        related_name='commentaires',
        verbose_name="Œuvre"
    )
    contenu = models.TextField(verbose_name="Contenu")
    est_approuve = models.BooleanField(default=False, verbose_name="Approuvé")

    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    date_modification = models.DateTimeField(auto_now=True, verbose_name="Date de modification")

    class Meta:
        verbose_name = "Commentaire"
        verbose_name_plural = "Commentaires"
        ordering = ['-date_creation']

    def __str__(self):
        return f"{self.utilisateur.username} sur {self.oeuvre.titre}"