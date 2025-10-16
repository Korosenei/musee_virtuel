from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.db.models import Count, Q
from django.core.paginator import Paginator
from .forms import InscriptionForm, ModifierUtilisateurForm, ModifierProfilForm
from .models import ProfilUtilisateur

from apps.core.models import Categorie, Artiste, Salle, Oeuvre, Favori, Visite, Commentaire


def inscription(request):
    """Inscription d'un nouvel utilisateur"""
    if request.user.is_authenticated:
        return redirect('core:accueil')

    if request.method == 'POST':
        form = InscriptionForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(
                request,
                f'Bienvenue {user.username} ! Votre compte a été créé avec succès.'
            )
            return redirect('core:accueil')
    else:
        form = InscriptionForm()

    contexte = {'form': form}
    return render(request, 'accounts/inscription.html', contexte)


@login_required
def profil(request):
    """Affichage du profil utilisateur"""
    # Récupérer ou créer le profil
    profil, created = ProfilUtilisateur.objects.get_or_create(
        utilisateur=request.user
    )

    # Statistiques utilisateur
    nombre_favoris = Favori.objects.filter(utilisateur=request.user).count()
    nombre_visites = Visite.objects.filter(utilisateur=request.user).count()
    nombre_commentaires = request.user.commentaires.filter(est_approuve=True).count()

    # Œuvres favorites récentes
    favoris_recents = Favori.objects.filter(
        utilisateur=request.user
    ).select_related('oeuvre', 'oeuvre__artiste').order_by('-date_ajout')[:6]

    # Historique récent
    visites_recentes = Visite.objects.filter(
        utilisateur=request.user
    ).select_related('oeuvre', 'oeuvre__artiste').order_by('-date_visite')[:6]

    # Catégories préférées (basées sur les favoris)
    categories_preferees = Favori.objects.filter(
        utilisateur=request.user
    ).values(
        'oeuvre__categorie__nom',
        'oeuvre__categorie__slug'
    ).annotate(
        nombre=Count('id')
    ).order_by('-nombre')[:5]

    contexte = {
        'profil': profil,
        'nombre_favoris': nombre_favoris,
        'nombre_visites': nombre_visites,
        'nombre_commentaires': nombre_commentaires,
        'favoris_recents': favoris_recents,
        'visites_recentes': visites_recentes,
        'categories_preferees': categories_preferees,
    }
    return render(request, 'accounts/profile.html', contexte)


@login_required
def modifier_profil(request):
    """Modification du profil utilisateur"""
    # Récupérer ou créer le profil
    profil, created = ProfilUtilisateur.objects.get_or_create(
        utilisateur=request.user
    )

    if request.method == 'POST':
        form_user = ModifierUtilisateurForm(request.POST, instance=request.user)
        form_profil = ModifierProfilForm(
            request.POST,
            request.FILES,
            instance=profil
        )

        if form_user.is_valid() and form_profil.is_valid():
            form_user.save()
            form_profil.save()
            messages.success(request, 'Votre profil a été mis à jour avec succès.')
            return redirect('accounts:profil')
    else:
        form_user = ModifierUtilisateurForm(instance=request.user)
        form_profil = ModifierProfilForm(instance=profil)

    contexte = {
        'form_user': form_user,
        'form_profil': form_profil,
    }
    return render(request, 'accounts/modifier_profil.html', contexte)


@login_required
def mes_favoris(request):
    """Liste des œuvres favorites de l'utilisateur"""
    # Filtres
    categorie_slug = request.GET.get('categorie')
    tri = request.GET.get('tri', '-date_ajout')

    favoris = Favori.objects.filter(
        utilisateur=request.user
    ).select_related('oeuvre', 'oeuvre__artiste', 'oeuvre__categorie')

    # Filtrage par catégorie
    if categorie_slug:
        favoris = favoris.filter(oeuvre__categorie__slug=categorie_slug)

    # Tri
    if tri == 'titre':
        favoris = favoris.order_by('oeuvre__titre')
    elif tri == '-titre':
        favoris = favoris.order_by('-oeuvre__titre')
    elif tri == 'note':
        favoris = favoris.order_by('note')
    elif tri == '-note':
        favoris = favoris.order_by('-note')
    elif tri == 'date_ajout':
        favoris = favoris.order_by('date_ajout')
    else:  # -date_ajout
        favoris = favoris.order_by('-date_ajout')

    # Pagination
    paginator = Paginator(favoris, 12)
    page = request.GET.get('page')
    favoris_page = paginator.get_page(page)

    # Catégories pour le filtre
    categories = Categorie.objects.filter(
        est_active=True,
        oeuvres__favoris__utilisateur=request.user
    ).distinct()

    contexte = {
        'favoris': favoris_page,
        'categories': categories,
        'tri_actuel': tri,
        'categorie_active': categorie_slug,
    }
    return render(request, 'accounts/mes_favoris.html', contexte)


@login_required
def mon_historique(request):
    """Historique des visites de l'utilisateur"""
    # Filtres
    periode = request.GET.get('periode', 'tout')

    visites = Visite.objects.filter(
        utilisateur=request.user
    ).select_related('oeuvre', 'oeuvre__artiste', 'oeuvre__categorie')

    # Filtrage par période
    from datetime import datetime, timedelta
    if periode == 'jour':
        date_limite = datetime.now() - timedelta(days=1)
        visites = visites.filter(date_visite__gte=date_limite)
    elif periode == 'semaine':
        date_limite = datetime.now() - timedelta(weeks=1)
        visites = visites.filter(date_visite__gte=date_limite)
    elif periode == 'mois':
        date_limite = datetime.now() - timedelta(days=30)
        visites = visites.filter(date_visite__gte=date_limite)

    visites = visites.order_by('-date_visite')

    # Pagination
    paginator = Paginator(visites, 20)
    page = request.GET.get('page')
    visites_page = paginator.get_page(page)

    # Statistiques
    nombre_total_visites = Visite.objects.filter(utilisateur=request.user).count()
    nombre_oeuvres_vues = Visite.objects.filter(
        utilisateur=request.user
    ).values('oeuvre').distinct().count()
    duree_totale = sum(
        v.duree_secondes for v in Visite.objects.filter(utilisateur=request.user)
    )
    duree_totale_minutes = duree_totale // 60

    # Œuvre la plus visitée
    oeuvre_plus_visitee = Visite.objects.filter(
        utilisateur=request.user
    ).values(
        'oeuvre__id',
        'oeuvre__titre',
        'oeuvre__slug'
    ).annotate(
        nombre_visites=Count('id')
    ).order_by('-nombre_visites').first()

    contexte = {
        'visites': visites_page,
        'periode_active': periode,
        'nombre_total_visites': nombre_total_visites,
        'nombre_oeuvres_vues': nombre_oeuvres_vues,
        'duree_totale_minutes': duree_totale_minutes,
        'oeuvre_plus_visitee': oeuvre_plus_visitee,
    }
    return render(request, 'accounts/mon_historique.html', contexte)


@login_required
def supprimer_compte(request):
    """Suppression du compte utilisateur"""
    if request.method == 'POST':
        confirmation = request.POST.get('confirmation')
        if confirmation == 'SUPPRIMER':
            user = request.user
            user.delete()
            messages.success(
                request,
                'Votre compte a été supprimé avec succès. Au revoir !'
            )
            return redirect('core:accueil')
        else:
            messages.error(
                request,
                'Vous devez taper "SUPPRIMER" pour confirmer la suppression.'
            )

    return render(request, 'accounts/supprimer_compte.html')


@login_required
def mes_commentaires(request):
    """Liste des commentaires de l'utilisateur"""
    commentaires = request.user.commentaires.select_related(
        'oeuvre',
        'oeuvre__artiste'
    ).order_by('-date_creation')

    # Pagination
    paginator = Paginator(commentaires, 15)
    page = request.GET.get('page')
    commentaires_page = paginator.get_page(page)

    # Statistiques
    nombre_approuves = request.user.commentaires.filter(est_approuve=True).count()
    nombre_en_attente = request.user.commentaires.filter(est_approuve=False).count()

    contexte = {
        'commentaires': commentaires_page,
        'nombre_approuves': nombre_approuves,
        'nombre_en_attente': nombre_en_attente,
    }
    return render(request, 'accounts/mes_commentaires.html', contexte)


@login_required
def recommandations(request):
    """Recommandations personnalisées basées sur les favoris et l'historique"""
    # Récupérer les catégories favorites
    categories_favorites = Favori.objects.filter(
        utilisateur=request.user
    ).values_list('oeuvre__categorie', flat=True).distinct()

    # Récupérer les artistes favoris
    artistes_favoris = Favori.objects.filter(
        utilisateur=request.user
    ).values_list('oeuvre__artiste', flat=True).distinct()

    # IDs des œuvres déjà vues/favorites
    oeuvres_connues = set(
        list(Favori.objects.filter(
            utilisateur=request.user
        ).values_list('oeuvre_id', flat=True)) +
        list(Visite.objects.filter(
            utilisateur=request.user
        ).values_list('oeuvre_id', flat=True))
    )

    # Recommandations basées sur les catégories favorites
    recommandations_categories = Oeuvre.objects.filter(
        categorie__in=categories_favorites,
        est_visible=True
    ).exclude(id__in=oeuvres_connues).order_by('-nombre_vues')[:8]

    # Recommandations basées sur les artistes favoris
    recommandations_artistes = Oeuvre.objects.filter(
        artiste__in=artistes_favoris,
        est_visible=True
    ).exclude(id__in=oeuvres_connues).order_by('-nombre_vues')[:8]

    # Œuvres populaires (si pas assez de recommandations)
    oeuvres_populaires = Oeuvre.objects.filter(
        est_visible=True
    ).exclude(id__in=oeuvres_connues).order_by('-nombre_vues')[:8]

    # Nouvelles œuvres
    nouvelles_oeuvres = Oeuvre.objects.filter(
        est_visible=True
    ).exclude(id__in=oeuvres_connues).order_by('-date_creation')[:8]

    contexte = {
        'recommandations_categories': recommandations_categories,
        'recommandations_artistes': recommandations_artistes,
        'oeuvres_populaires': oeuvres_populaires,
        'nouvelles_oeuvres': nouvelles_oeuvres,
    }
    return render(request, 'accounts/recommandations.html', contexte)