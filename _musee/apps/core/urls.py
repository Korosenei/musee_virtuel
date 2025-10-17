from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Page d'accueil
    path('', views.accueil, name='accueil'),

    # Catégories
    path('categories/', views.liste_categories, name='liste_categories'),
    path('categorie/<slug:slug>/', views.detail_categorie, name='detail_categorie'),

    # Œuvres
    path('oeuvres/', views.liste_oeuvres, name='liste_oeuvres'),
    path('oeuvre/<slug:slug>/', views.detail_oeuvre, name='detail_oeuvre'),
    path('oeuvres/recherche/', views.recherche_oeuvres, name='recherche_oeuvres'),

    # Artistes
    path('artistes/', views.liste_artistes, name='liste_artistes'),
    path('artiste/<slug:slug>/', views.detail_artiste, name='detail_artiste'),

    # Salles virtuelles
    path('salles/', views.liste_salles, name='liste_salles'),
    path('salle/<slug:slug>/', views.detail_salle, name='detail_salle'),

    # Visite virtuelle 3D
    path('visite-virtuelle/', views.visite_virtuelle, name='visite_virtuelle'),
    path('visite-virtuelle/<slug:salle_slug>/', views.visite_virtuelle_salle, name='visite_virtuelle_salle'),

    # Interactions utilisateur (nécessite authentification)
    path('oeuvre/<int:oeuvre_id>/ajouter-favori/', views.ajouter_favori, name='ajouter_favori'),
    path('oeuvre/<int:oeuvre_id>/retirer-favori/', views.retirer_favori, name='retirer_favori'),
    path('oeuvre/<int:oeuvre_id>/commenter/', views.ajouter_commentaire, name='ajouter_commentaire'),
    path('oeuvre/<int:oeuvre_id>/enregistrer-visite/', views.enregistrer_visite, name='enregistrer_visite'),

    # À propos
    path('a-propos/', views.a_propos, name='a_propos'),
    path('contact/', views.contact, name='contact'),
]