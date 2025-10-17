from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentification
    path('inscription/', views.inscription, name='inscription'),
    path('connexion/', auth_views.LoginView.as_view(
        template_name='accounts/connexion.html'
    ), name='connexion'),
    path('deconnexion/', auth_views.LogoutView.as_view(), name='deconnexion'),

    # Profil
    path('profil/', views.profil, name='profil'),
    path('profil/modifier/', views.modifier_profil, name='modifier_profil'),
    path('mes-favoris/', views.mes_favoris, name='mes_favoris'),
    path('mon-historique/', views.mon_historique, name='mon_historique'),
    path('mes-commentaires/', views.mes_commentaires, name='mes_commentaires'),
    path('supprimer-compte/', views.supprimer_compte, name='supprimer_compte'),

    # Réinitialisation mot de passe
    path('mot-de-passe/reinitialiser/',
         auth_views.PasswordResetView.as_view(
             template_name='comptes/reinitialisation_mdp.html'
         ),
         name='reinitialisation_mdp'),
    path('mot-de-passe/reinitialiser/envoye/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='comptes/reinitialisation_mdp_envoye.html'
         ),
         name='reinitialisation_mdp_envoye'),
    path('mot-de-passe/reinitialiser/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='comptes/reinitialisation_mdp_confirmer.html'
         ),
         name='reinitialisation_mdp_confirmer'),
    path('mot-de-passe/reinitialiser/termine/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='comptes/reinitialisation_mdp_termine.html'
         ),
         name='reinitialisation_mdp_termine'),
]