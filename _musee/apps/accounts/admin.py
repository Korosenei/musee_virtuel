from django.contrib import admin
from django.utils.html import format_html
from .models import ProfilUtilisateur
from apps.core.models import (Categorie, Artiste, Salle, Oeuvre, Favori, Visite, Commentaire )


@admin.register(ProfilUtilisateur)
class ProfilUtilisateurAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'ville', 'pays', 'theme_prefere', 'langue')
    list_filter = ('theme_prefere', 'langue', 'pays')
    search_fields = ('utilisateur__username', 'utilisateur__email', 'ville')
    readonly_fields = ('date_creation', 'date_modification')

    fieldsets = (
        ('Utilisateur', {
            'fields': ('utilisateur', 'avatar', 'biographie')
        }),
        ('Localisation', {
            'fields': ('ville', 'pays', 'site_web')
        }),
        ('Préférences', {
            'fields': ('theme_prefere', 'langue')
        }),
        ('Dates', {
            'fields': ('date_creation', 'date_modification'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Favori)
class FavoriAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'oeuvre', 'note', 'date_ajout')
    list_filter = ('note', 'date_ajout')
    search_fields = ('utilisateur__username', 'oeuvre__titre')
    readonly_fields = ('date_ajout',)
    date_hierarchy = 'date_ajout'

    def has_add_permission(self, request):
        # Les favoris sont ajoutés via le frontend
        return False


@admin.register(Visite)
class VisiteAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'oeuvre', 'date_visite', 'duree_formatee')
    list_filter = ('date_visite',)
    search_fields = ('utilisateur__username', 'oeuvre__titre')
    readonly_fields = ('date_visite',)
    date_hierarchy = 'date_visite'

    def duree_formatee(self, obj):
        minutes = obj.duree_secondes // 60
        secondes = obj.duree_secondes % 60
        return f"{minutes}m {secondes}s"

    duree_formatee.short_description = 'Durée'

    def has_add_permission(self, request):
        # Les visites sont enregistrées automatiquement
        return False


@admin.register(Commentaire)
class CommentaireAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'oeuvre', 'extrait_contenu', 'est_approuve', 'date_creation')
    list_filter = ('est_approuve', 'date_creation')
    search_fields = ('utilisateur__username', 'oeuvre__titre', 'contenu')
    list_editable = ('est_approuve',)
    readonly_fields = ('date_creation', 'date_modification')
    date_hierarchy = 'date_creation'
    actions = ['approuver_commentaires', 'refuser_commentaires']

    def extrait_contenu(self, obj):
        return obj.contenu[:50] + '...' if len(obj.contenu) > 50 else obj.contenu

    extrait_contenu.short_description = 'Contenu'

    def approuver_commentaires(self, request, queryset):
        nombre = queryset.update(est_approuve=True)
        self.message_user(request, f"{nombre} commentaire(s) approuvé(s).")

    approuver_commentaires.short_description = "Approuver les commentaires"

    def refuser_commentaires(self, request, queryset):
        nombre = queryset.update(est_approuve=False)
        self.message_user(request, f"{nombre} commentaire(s) refusé(s).")

    refuser_commentaires.short_description = "Refuser les commentaires"


# Personnalisation du site admin
admin.site.site_header = "Administration du Musée Virtuel"
admin.site.site_title = "Musée Virtuel Admin"
admin.site.index_title = "Tableau de bord"