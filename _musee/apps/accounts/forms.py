
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from .models import ProfilUtilisateur

from apps.core.models import Commentaire, Oeuvre, Categorie, Artiste, Salle, Favori, Visite, Oeuvre


class InscriptionForm(UserCreationForm):
    """Formulaire d'inscription personnalisé"""

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'votre.email@exemple.com'
        }),
        label='Email'
    )

    prenom = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Votre prénom'
        }),
        label='Prénom'
    )

    nom = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Votre nom'
        }),
        label='Nom'
    )

    class Meta:
        model = User
        fields = ['username', 'prenom', 'nom', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom d\'utilisateur'
            })
        }
        labels = {
            'username': 'Nom d\'utilisateur'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget = forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Mot de passe'
        })
        self.fields['password1'].label = 'Mot de passe'
        self.fields['password1'].help_text = 'Au moins 8 caractères, pas trop commun.'

        self.fields['password2'].widget = forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirmez le mot de passe'
        })
        self.fields['password2'].label = 'Confirmation du mot de passe'
        self.fields['password2'].help_text = 'Saisissez le même mot de passe.'

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Cette adresse email est déjà utilisée.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data.get('prenom', '')
        user.last_name = self.cleaned_data.get('nom', '')

        if commit:
            user.save()
            # Créer automatiquement le profil utilisateur
            ProfilUtilisateur.objects.create(utilisateur=user)

        return user


class ModifierUtilisateurForm(forms.ModelForm):
    """Formulaire pour modifier les informations de base de l'utilisateur"""

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control'
        }),
        label='Email'
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Prénom'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom'
            })
        }
        labels = {
            'first_name': 'Prénom',
            'last_name': 'Nom'
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Vérifier que l'email n'est pas déjà utilisé par un autre utilisateur
        if User.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
            raise forms.ValidationError('Cette adresse email est déjà utilisée.')
        return email


class ModifierProfilForm(forms.ModelForm):
    """Formulaire pour modifier le profil utilisateur"""

    class Meta:
        model = ProfilUtilisateur
        fields = ['avatar', 'biographie', 'ville', 'pays', 'site_web', 'theme_prefere', 'langue']
        widgets = {
            'avatar': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'biographie': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Parlez-nous de vous, vos centres d\'intérêt artistiques...'
            }),
            'ville': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Ouagadougou'
            }),
            'pays': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Burkina Faso'
            }),
            'site_web': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://votre-site.com'
            }),
            'theme_prefere': forms.Select(attrs={
                'class': 'form-control'
            }),
            'langue': forms.Select(attrs={
                'class': 'form-control'
            })
        }
        labels = {
            'avatar': 'Photo de profil',
            'biographie': 'Biographie',
            'ville': 'Ville',
            'pays': 'Pays',
            'site_web': 'Site web',
            'theme_prefere': 'Thème préféré',
            'langue': 'Langue'
        }


class NoteFavoriForm(forms.ModelForm):
    """Formulaire pour noter et commenter un favori"""

    class Meta:
        model = Favori
        fields = ['note', 'commentaire']
        widgets = {
            'note': forms.Select(
                choices=[(i, '⭐' * i) for i in range(1, 6)],
                attrs={
                    'class': 'form-control'
                }
            ),
            'commentaire': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Notes personnelles sur cette œuvre (optionnel)...'
            })
        }
        labels = {
            'note': 'Votre note',
            'commentaire': 'Commentaire personnel'
        }


class RechercheAvanceeForm(forms.Form):
    """Formulaire de recherche avancée avec tous les critères"""

    requete = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Titre, description, artiste...'
        }),
        label='Recherche textuelle'
    )

    categorie = forms.ModelMultipleChoiceField(
        queryset=Categorie.objects.filter(est_active=True),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label='Catégories'
    )

    artiste = forms.ModelMultipleChoiceField(
        queryset=Artiste.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label='Artistes'
    )

    salle = forms.ModelMultipleChoiceField(
        queryset=Salle.objects.filter(est_active=True),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label='Salles'
    )

    periode = forms.ChoiceField(
        choices=[
            ('', 'Toutes les périodes'),
            ('antiquite', 'Antiquité (avant 476)'),
            ('moyen_age', 'Moyen Âge (476-1492)'),
            ('renaissance', 'Renaissance (1400-1600)'),
            ('classique', 'Période classique (1600-1800)'),
            ('moderne', 'Période moderne (1800-1945)'),
            ('contemporain', 'Contemporain (après 1945)')
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='Période historique'
    )

    annee_debut = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ex: 1800',
            'min': -3000,
            'max': 2100
        }),
        label='Année de début'
    )

    annee_fin = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ex: 1900',
            'min': -3000,
            'max': 2100
        }),
        label='Année de fin'
    )

    a_modele_3d = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='Possède un modèle 3D'
    )

    a_audio = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='Possède un guide audio'
    )

    a_video = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='Possède une vidéo'
    )

    tri = forms.ChoiceField(
        choices=[
            ('-date_creation', 'Ajout récent'),
            ('date_creation', 'Ajout ancien'),
            ('titre', 'Titre (A-Z)'),
            ('-titre', 'Titre (Z-A)'),
            ('annee', 'Année (croissant)'),
            ('-annee', 'Année (décroissant)'),
            ('-nombre_vues', 'Popularité'),
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
        annee_debut = cleaned_data.get('annee_debut')
        annee_fin = cleaned_data.get('annee_fin')

        if annee_debut and annee_fin and annee_debut > annee_fin:
            raise forms.ValidationError(
                "L'année de début ne peut pas être supérieure à l'année de fin."
            )

        return cleaned_data
