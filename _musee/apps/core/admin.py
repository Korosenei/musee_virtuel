from django.contrib import admin
from django.utils.html import format_html
from .models import (Categorie, Artiste, Salle, Oeuvre, Favori, Visite, Commentaire )
from apps.accounts.models import ProfilUtilisateur


@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ('nom', 'apercu_couleur', 'ordre', 'est_active', 'nombre_oeuvres')
    list_filter = ('est_active', 'date_creation')
    search_fields = ('nom', 'description')
    prepopulated_fields = {'slug': ('nom',)}
    list_editable = ('ordre', 'est_active')
    ordering = ('ordre', 'nom')

    def apercu_couleur(self, obj):
        return format_html(
            '<div style="width: 30px; height: 30px; background-color: {}; border: 1px solid #ccc;"></div>',
            obj.couleur
        )

    apercu_couleur.short_description = 'Couleur'

    def nombre_oeuvres(self, obj):
        return obj.oeuvres.count()

    nombre_oeuvres.short_description = "Nombre d'œuvres"


@admin.register(Artiste)
class ArtisteAdmin(admin.ModelAdmin):
    list_display = ('nom', 'nationalite', 'annee_naissance', 'annee_deces', 'nombre_oeuvres')
    list_filter = ('nationalite', 'annee_naissance')
    search_fields = ('nom', 'biographie')
    prepopulated_fields = {'slug': ('nom',)}
    ordering = ('nom',)

    fieldsets = (
        ('Informations générales', {
            'fields': ('nom', 'slug', 'biographie', 'photo')
        }),
        ('Informations biographiques', {
            'fields': ('annee_naissance', 'annee_deces', 'nationalite')
        }),
        ('Liens', {
            'fields': ('site_web',)
        }),
    )

    def nombre_oeuvres(self, obj):
        return obj.oeuvres.count()

    nombre_oeuvres.short_description = "Nombre d'œuvres"


@admin.register(Salle)
class SalleAdmin(admin.ModelAdmin):
    list_display = ('nom', 'categorie', 'dimensions', 'eclairage', 'ordre', 'est_active')
    list_filter = ('categorie', 'eclairage', 'est_active')
    search_fields = ('nom', 'description')
    prepopulated_fields = {'slug': ('nom',)}
    list_editable = ('ordre', 'est_active')
    ordering = ('ordre', 'nom')

    fieldsets = (
        ('Informations générales', {
            'fields': ('nom', 'slug', 'description', 'categorie')
        }),
        ('Dimensions 3D', {
            'fields': ('largeur', 'longueur', 'hauteur')
        }),
        ('Apparence', {
            'fields': ('couleur_murs', 'texture_sol', 'eclairage')
        }),
        ('Paramètres', {
            'fields': ('ordre', 'est_active')
        }),
    )

    def dimensions(self, obj):
        return f"{obj.largeur}m × {obj.longueur}m × {obj.hauteur}m"

    dimensions.short_description = 'Dimensions'


class VisiteInline(admin.TabularInline):
    model = Visite
    extra = 0
    readonly_fields = ('date_visite', 'duree_secondes')
    can_delete = False


class CommentaireInline(admin.TabularInline):
    model = Commentaire
    extra = 0
    readonly_fields = ('date_creation',)
    fields = ('utilisateur', 'contenu', 'est_approuve', 'date_creation')


@admin.register(Oeuvre)
class OeuvreAdmin(admin.ModelAdmin):
    list_display = (
        'titre',
        'apercu_miniature',
        'artiste',
        'categorie',
        'salle',
        'annee',
        'nombre_vues',
        'est_visible',
        'est_mise_en_avant'
    )
    list_filter = (
        'categorie',
        'salle',
        'est_visible',
        'est_mise_en_avant',
        'date_creation'
    )
    search_fields = ('titre', 'description', 'artiste__nom')
    prepopulated_fields = {'slug': ('titre',)}
    list_editable = ('est_visible', 'est_mise_en_avant')
    readonly_fields = ('nombre_vues', 'date_creation', 'date_modification', 'apercu_image_hd')
    ordering = ('-date_creation',)
    date_hierarchy = 'date_creation'

    inlines = [CommentaireInline, VisiteInline]

    fieldsets = (
        ('Informations principales', {
            'fields': (
                'titre',
                'slug',
                'description',
                'description_courte'
            )
        }),
        ('Classification', {
            'fields': (
                'categorie',
                'artiste',
                'salle',
                'annee',
                'epoque'
            )
        }),
        ('Médias', {
            'fields': (
                'image_miniature',
                'image_haute_resolution',
                'apercu_image_hd',
                'modele_3d',
                'audio_guide',
                'video',
                'lien_video_externe'
            )
        }),
        ('Position 3D dans la salle', {
            'fields': (
                'position_x',
                'position_y',
                'position_z',
                'rotation',
                'echelle'
            ),
            'classes': ('collapse',)
        }),
        ('Métadonnées techniques', {
            'fields': (
                'dimensions',
                'technique',
                'materiau',
                'collection',
                'numero_inventaire',
                'metadonnees'
            ),
            'classes': ('collapse',)
        }),
        ('Visibilité et statistiques', {
            'fields': (
                'est_visible',
                'est_mise_en_avant',
                'nombre_vues',
                'date_creation',
                'date_modification'
            )
        }),
    )

    def apercu_miniature(self, obj):
        if obj.image_miniature:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px;" />',
                obj.image_miniature.url
            )
        return "Pas d'image"

    apercu_miniature.short_description = 'Aperçu'

    def apercu_image_hd(self, obj):
        if obj.image_haute_resolution:
            return format_html(
                '<img src="{}" style="max-width: 400px; max-height: 400px; border-radius: 8px;" />',
                obj.image_haute_resolution.url
            )
        return "Pas d'image haute résolution"

    apercu_image_hd.short_description = 'Aperçu HD'

    actions = ['rendre_visible', 'rendre_invisible', 'mettre_en_avant', 'retirer_mise_en_avant']

    def rendre_visible(self, request, queryset):
        nombre = queryset.update(est_visible=True)
        self.message_user(request, f"{nombre} œuvre(s) rendue(s) visible(s).")

    rendre_visible.short_description = "Rendre visible"

    def rendre_invisible(self, request, queryset):
        nombre = queryset.update(est_visible=False)
        self.message_user(request, f"{nombre} œuvre(s) rendue(s) invisible(s).")

    rendre_invisible.short_description = "Rendre invisible"

    def mettre_en_avant(self, request, queryset):
        nombre = queryset.update(est_mise_en_avant=True)
        self.message_user(request, f"{nombre} œuvre(s) mise(s) en avant.")

    mettre_en_avant.short_description = "Mettre en avant"

    def retirer_mise_en_avant(self, request, queryset):
        nombre = queryset.update(est_mise_en_avant=False)
        self.message_user(request, f"{nombre} œuvre(s) retirée(s) de la mise en avant.")

    retirer_mise_en_avant.short_description = "Retirer de la mise en avant"

