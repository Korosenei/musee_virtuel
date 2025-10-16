from django import forms
from django.core.validators import MinLengthValidator
from .models import Commentaire, Oeuvre, Categorie, Artiste, Salle, Favori


class CommentaireForm(forms.ModelForm):
    """Formulaire pour ajouter un commentaire sur une œuvre"""

    class Meta:
        model = Commentaire
        fields = ['contenu']
        widgets = {
            'contenu': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Partagez votre avis sur cette œuvre...',
                'required': True
            })
        }
        labels = {
            'contenu': 'Votre commentaire'
        }

    def clean_contenu(self):
        contenu = self.cleaned_data.get('contenu')
        if len(contenu.strip()) < 10:
            raise forms.ValidationError('Le commentaire doit contenir au moins 10 caractères.')
        return contenu


class RechercheForm(forms.Form):
    """Formulaire de recherche d'œuvres"""

    requete = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Rechercher une œuvre, un artiste, une technique...',
            'autocomplete': 'off'
        }),
        label='Recherche'
    )

    categorie = forms.ModelChoiceField(
        queryset=Categorie.objects.filter(est_active=True),
        required=False,
        empty_label='Toutes les catégories',
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='Catégorie'
    )

    artiste = forms.ModelChoiceField(
        queryset=Artiste.objects.all(),
        required=False,
        empty_label='Tous les artistes',
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='Artiste'
    )

    annee_min = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Année min',
            'min': 1000,
            'max': 2100
        }),
        label='Année minimum'
    )

    annee_max = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Année max',
            'min': 1000,
            'max': 2100
        }),
        label='Année maximum'
    )

    tri = forms.ChoiceField(
        choices=[
            ('-date_creation', 'Plus récentes'),
            ('date_creation', 'Plus anciennes'),
            ('titre', 'Titre (A-Z)'),
            ('-titre', 'Titre (Z-A)'),
            ('annee', 'Année (croissant)'),
            ('-annee', 'Année (décroissant)'),
            ('-nombre_vues', 'Plus populaires'),
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='Trier par',
        initial='-date_creation'
    )

    def clean(self):
        cleaned_data = super().clean()
        annee_min = cleaned_data.get('annee_min')
        annee_max = cleaned_data.get('annee_max')

        if annee_min and annee_max and annee_min > annee_max:
            raise forms.ValidationError(
                "L'année minimum ne peut pas être supérieure à l'année maximum."
            )

        return cleaned_data


class FiltreOeuvreForm(forms.Form):
    """Formulaire de filtrage simplifié pour la galerie"""

    categorie = forms.ModelChoiceField(
        queryset=Categorie.objects.filter(est_active=True),
        required=False,
        empty_label='Toutes les catégories',
        widget=forms.Select(attrs={
            'class': 'form-control',
            'onchange': 'this.form.submit()'
        })
    )

    salle = forms.ModelChoiceField(
        queryset=Salle.objects.filter(est_active=True),
        required=False,
        empty_label='Toutes les salles',
        widget=forms.Select(attrs={
            'class': 'form-control',
            'onchange': 'this.form.submit()'
        })
    )


class ContactForm(forms.Form):
    """Formulaire de contact"""

    nom = forms.CharField(
        max_length=100,
        validators=[MinLengthValidator(2)],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Votre nom complet',
            'required': True
        }),
        label='Nom'
    )

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'votre.email@exemple.com',
            'required': True
        }),
        label='Email'
    )

    sujet = forms.ChoiceField(
        choices=[
            ('', 'Sélectionnez un sujet'),
            ('information', 'Demande d\'information'),
            ('technique', 'Problème technique'),
            ('suggestion', 'Suggestion'),
            ('partenariat', 'Partenariat'),
            ('autre', 'Autre')
        ],
        widget=forms.Select(attrs={
            'class': 'form-control',
            'required': True
        }),
        label='Sujet'
    )

    message = forms.CharField(
        validators=[MinLengthValidator(20)],
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 6,
            'placeholder': 'Votre message (minimum 20 caractères)...',
            'required': True
        }),
        label='Message'
    )

    def clean_message(self):
        message = self.cleaned_data.get('message')
        if len(message.strip()) < 20:
            raise forms.ValidationError('Le message doit contenir au moins 20 caractères.')
        return message

