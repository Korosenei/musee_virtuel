from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.http import JsonResponse
from django.core.paginator import Paginator

from .models import Categorie, Artiste, Salle, Oeuvre, Favori, Visite, Commentaire
from .forms import CommentaireForm, RechercheForm


def accueil(request):
    """Page d'accueil du musée virtuel"""
    categories = Categorie.objects.filter(est_active=True).annotate(
        nombre_oeuvres=Count('oeuvres')
    )
    oeuvres_en_avant = Oeuvre.objects.filter(
        est_visible=True,
        est_mise_en_avant=True
    )[:6]
    oeuvres_recentes = Oeuvre.objects.filter(
        est_visible=True
    ).order_by('-date_creation')[:8]

    contexte = {
        'categories': categories,
        'oeuvres_en_avant': oeuvres_en_avant,
        'oeuvres_recentes': oeuvres_recentes,
    }
    return render(request, 'core/accueil.html', contexte)


def liste_categories(request):
    """Liste toutes les catégories"""
    categories = Categorie.objects.filter(est_active=True).annotate(
        nombre_oeuvres=Count('oeuvres')
    )
    contexte = {'categories': categories}
    return render(request, 'core/liste_categories.html', contexte)


def detail_categorie(request, slug):
    """Affiche les œuvres d'une catégorie"""
    categorie = get_object_or_404(Categorie, slug=slug, est_active=True)
    oeuvres = Oeuvre.objects.filter(
        categorie=categorie,
        est_visible=True
    ).select_related('artiste', 'salle')

    # Pagination
    paginator = Paginator(oeuvres, 12)
    page = request.GET.get('page')
    oeuvres_page = paginator.get_page(page)

    contexte = {
        'categorie': categorie,
        'oeuvres': oeuvres_page,
    }
    return render(request, 'core/detail_categorie.html', contexte)


def liste_oeuvres(request):
    """Liste toutes les œuvres avec filtres"""
    oeuvres = Oeuvre.objects.filter(est_visible=True).select_related(
        'artiste', 'categorie', 'salle'
    )

    # Filtres
    categorie_slug = request.GET.get('categorie')
    artiste_slug = request.GET.get('artiste')
    salle_slug = request.GET.get('salle')
    tri = request.GET.get('tri', '-date_creation')

    if categorie_slug:
        oeuvres = oeuvres.filter(categorie__slug=categorie_slug)
    if artiste_slug:
        oeuvres = oeuvres.filter(artiste__slug=artiste_slug)
    if salle_slug:
        oeuvres = oeuvres.filter(salle__slug=salle_slug)

    # Tri
    oeuvres = oeuvres.order_by(tri)

    # Pagination
    paginator = Paginator(oeuvres, 16)
    page = request.GET.get('page')
    oeuvres_page = paginator.get_page(page)

    # Pour les filtres
    categories = Categorie.objects.filter(est_active=True)
    artistes = Artiste.objects.all()
    salles = Salle.objects.filter(est_active=True)

    contexte = {
        'oeuvres': oeuvres_page,
        'categories': categories,
        'artistes': artistes,
        'salles': salles,
        'tri_actuel': tri,
    }
    return render(request, 'core/liste_oeuvres.html', contexte)


def detail_oeuvre(request, slug):
    """Affiche le détail d'une œuvre"""
    oeuvre = get_object_or_404(
        Oeuvre.objects.select_related('artiste', 'categorie', 'salle'),
        slug=slug,
        est_visible=True
    )

    # Incrémenter le compteur de vues
    oeuvre.incrementer_vues()

    # Vérifier si l'œuvre est dans les favoris de l'utilisateur
    est_favori = False
    if request.user.is_authenticated:
        est_favori = Favori.objects.filter(
            utilisateur=request.user,
            oeuvre=oeuvre
        ).exists()

    # Commentaires approuvés
    commentaires = oeuvre.commentaires.filter(
        est_approuve=True
    ).select_related('utilisateur').order_by('-date_creation')

    # Formulaire de commentaire
    if request.method == 'POST' and request.user.is_authenticated:
        form = CommentaireForm(request.POST)
        if form.is_valid():
            commentaire = form.save(commit=False)
            commentaire.utilisateur = request.user
            commentaire.oeuvre = oeuvre
            commentaire.save()
            messages.success(request, 'Votre commentaire a été ajouté et sera visible après modération.')
            return redirect('core:detail_oeuvre', slug=slug)
    else:
        form = CommentaireForm()

    # Œuvres similaires (même catégorie)
    oeuvres_similaires = Oeuvre.objects.filter(
        categorie=oeuvre.categorie,
        est_visible=True
    ).exclude(id=oeuvre.id)[:4]

    contexte = {
        'oeuvre': oeuvre,
        'est_favori': est_favori,
        'commentaires': commentaires,
        'form': form,
        'oeuvres_similaires': oeuvres_similaires,
    }
    return render(request, 'core/detail_oeuvre.html', contexte)


def recherche_oeuvres(request):
    """Recherche d'œuvres"""
    query = request.GET.get('q', '')
    oeuvres = Oeuvre.objects.filter(est_visible=True)

    if query:
        oeuvres = oeuvres.filter(
            Q(titre__icontains=query) |
            Q(description__icontains=query) |
            Q(artiste__nom__icontains=query) |
            Q(technique__icontains=query)
        ).distinct()

    paginator = Paginator(oeuvres, 12)
    page = request.GET.get('page')
    oeuvres_page = paginator.get_page(page)

    contexte = {
        'oeuvres': oeuvres_page,
        'query': query,
        'nombre_resultats': oeuvres.count(),
    }
    return render(request, 'core/recherche.html', contexte)


def liste_artistes(request):
    """Liste tous les artistes"""
    artistes = Artiste.objects.annotate(
        nombre_oeuvres=Count('oeuvres')
    ).order_by('nom')

    paginator = Paginator(artistes, 20)
    page = request.GET.get('page')
    artistes_page = paginator.get_page(page)

    contexte = {'artistes': artistes_page}
    return render(request, 'core/liste_artistes.html', contexte)


def detail_artiste(request, slug):
    """Affiche le détail d'un artiste et ses œuvres"""
    artiste = get_object_or_404(Artiste, slug=slug)
    oeuvres = Oeuvre.objects.filter(
        artiste=artiste,
        est_visible=True
    ).order_by('-annee')

    contexte = {
        'artiste': artiste,
        'oeuvres': oeuvres,
    }
    return render(request, 'core/detail_artiste.html', contexte)


def liste_salles(request):
    """Liste toutes les salles"""
    salles = Salle.objects.filter(est_active=True).select_related(
        'categorie'
    ).annotate(nombre_oeuvres=Count('oeuvres'))

    contexte = {'salles': salles}
    return render(request, 'core/liste_salles.html', contexte)


def detail_salle(request, slug):
    """Affiche le détail d'une salle"""
    salle = get_object_or_404(
        Salle.objects.select_related('categorie'),
        slug=slug,
        est_active=True
    )
    oeuvres = Oeuvre.objects.filter(
        salle=salle,
        est_visible=True
    ).select_related('artiste')

    contexte = {
        'salle': salle,
        'oeuvres': oeuvres,
    }
    return render(request, 'core/detail_salle.html', contexte)


def visite_virtuelle(request):
    """Page de visite virtuelle 3D - Vue générale"""
    salles = Salle.objects.filter(est_active=True).select_related('categorie')

    # Ajouter une propriété "surface" à chaque salle
    for salle in salles:
        if salle.largeur and salle.longueur:
            salle.surface = salle.largeur * salle.longueur
        else:
            salle.surface = None

    contexte = {'salles': salles}
    return render(request, 'core/visite_virtuelle.html', contexte)


def visite_virtuelle_salle(request, salle_slug):
    """Visite virtuelle 3D d'une salle spécifique"""
    salle = get_object_or_404(
        Salle.objects.select_related('categorie'),
        slug=salle_slug,
        est_active=True
    )

    # Récupérer toutes les œuvres de la salle avec leurs positions 3D
    oeuvres = Oeuvre.objects.filter(
        salle=salle,
        est_visible=True
    ).select_related('artiste')

    contexte = {
        'salle': salle,
        'oeuvres': oeuvres,
    }
    return render(request, 'core/visite_virtuelle_salle.html', contexte)


@login_required
def ajouter_favori(request, oeuvre_id):
    """Ajouter une œuvre aux favoris"""
    oeuvre = get_object_or_404(Oeuvre, id=oeuvre_id)
    favori, created = Favori.objects.get_or_create(
        utilisateur=request.user,
        oeuvre=oeuvre
    )

    if created:
        messages.success(request, f'"{oeuvre.titre}" ajoutée à vos favoris.')
    else:
        messages.info(request, 'Cette œuvre est déjà dans vos favoris.')

    return redirect('core:detail_oeuvre', slug=oeuvre.slug)


@login_required
def retirer_favori(request, oeuvre_id):
    """Retirer une œuvre des favoris"""
    oeuvre = get_object_or_404(Oeuvre, id=oeuvre_id)
    Favori.objects.filter(utilisateur=request.user, oeuvre=oeuvre).delete()
    messages.success(request, f'"{oeuvre.titre}" retirée de vos favoris.')
    return redirect('core:detail_oeuvre', slug=oeuvre.slug)


@login_required
def ajouter_commentaire(request, oeuvre_id):
    """Ajouter un commentaire (via AJAX)"""
    if request.method == 'POST':
        oeuvre = get_object_or_404(Oeuvre, id=oeuvre_id)
        form = CommentaireForm(request.POST)

        if form.is_valid():
            commentaire = form.save(commit=False)
            commentaire.utilisateur = request.user
            commentaire.oeuvre = oeuvre
            commentaire.save()

            return JsonResponse({
                'success': True,
                'message': 'Commentaire ajouté avec succès.'
            })

        return JsonResponse({
            'success': False,
            'errors': form.errors
        })

    return JsonResponse({'success': False})


@login_required
def enregistrer_visite(request, oeuvre_id):
    """Enregistrer une visite d'œuvre (AJAX)"""
    if request.method == 'POST':
        oeuvre = get_object_or_404(Oeuvre, id=oeuvre_id)
        duree = int(request.POST.get('duree', 0))

        Visite.objects.create(
            utilisateur=request.user,
            oeuvre=oeuvre,
            duree_secondes=duree
        )

        return JsonResponse({'success': True})

    return JsonResponse({'success': False})


def a_propos(request):
    """Page à propos"""
    return render(request, 'core/a_propos.html')


def contact(request):
    """Page de contact"""
    return render(request, 'core/contact.html')
