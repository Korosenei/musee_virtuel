from django.contrib.auth.models import User
from apps.core.models import Categorie, Artiste, Salle, Oeuvre, Favori, Visite, Commentaire
from django.utils.text import slugify
from faker import Faker
import random

fake = Faker('fr_FR')

# --- Utilisateurs ---
users = []
for i in range(5):
    user, created = User.objects.get_or_create(
        username=f"user{i+1}",
        defaults={
            "email": f"user{i+1}@exemple.com",
            "password": "test1234"
        }
    )
    users.append(user)

print("✅ Utilisateurs créés :", len(users))

# --- Catégories ---
noms_categories = ["Art", "Science", "Musique", "Cinéma", "Environnement", "Histoire"]
categories = []

for i, nom in enumerate(noms_categories):
    cat, created = Categorie.objects.get_or_create(
        nom=nom,
        defaults={
            "description": f"Catégorie dédiée à {nom.lower()} et ses merveilles.",
            "couleur": random.choice(["#3B82F6", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6", "#6366F1"]),
            "ordre": i,
            "est_active": True
        }
    )
    categories.append(cat)

print("✅ Catégories créées :", len(categories))

# --- Artistes ---
artistes = []
for _ in range(10):
    nom = fake.name()
    art, created = Artiste.objects.get_or_create(
        nom=nom,
        defaults={
            "biographie": fake.paragraph(nb_sentences=5),
            "annee_naissance": random.randint(1850, 1995),
            "nationalite": fake.country(),
            "site_web": fake.url(),
        }
    )
    artistes.append(art)

print("✅ Artistes créés :", len(artistes))

# --- Images d’œuvres en ligne ---
images_miniatures = [
    "https://images.unsplash.com/photo-1526318472351-bc6c9e6d56ab?w=500",
    "https://images.unsplash.com/photo-1529101091764-c3526daf38fe?w=500",
    "https://images.unsplash.com/photo-1520697222865-9d8a2d8d3e87?w=500",
    "https://images.unsplash.com/photo-1504198453319-5ce911bafcde?w=500",
    "https://images.unsplash.com/photo-1511765224389-37f0e77cf0eb?w=500",
    "https://images.unsplash.com/photo-1508264165352-258a6c9b57e3?w=500",
    "https://images.unsplash.com/photo-1504198458649-3128b932f49b?w=500",
]

images_hd = [
    "https://upload.wikimedia.org/wikipedia/commons/0/02/Mona_Lisa%2C_by_Leonardo_da_Vinci%2C_from_C2RMF_retouched.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/2/24/Starry_Night_Over_the_Rhone.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/1/15/Claude_Monet_-_Impression%2C_Sunrise.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/0/09/The_Persistence_of_Memory.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/3/36/Vincent_van_Gogh_-_The_Starry_Night_-_Google_Art_Project.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/2/2f/The_Great_Wave_off_Kanagawa.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/4/4d/Michelangelo_-_Creation_of_Adam_%28cropped%29.jpg",
]

# --- Salles ---
salles = []
for i in range(5):
    cat = random.choice(categories)
    salle, created = Salle.objects.get_or_create(
        nom=f"Salle {i+1} - {cat.nom}",
        defaults={
            "description": fake.paragraph(nb_sentences=3),
            "categorie": cat,
            "largeur": random.uniform(15, 25),
            "longueur": random.uniform(15, 25),
            "hauteur": random.uniform(3, 5),
            "couleur_murs": random.choice(["#FFFFFF", "#FAFAFA", "#F3F4F6"]),
            "eclairage": random.choice(["naturel", "chaud", "froid", "tamisé"]),
            "ordre": i
        }
    )
    salles.append(salle)

print("✅ Salles créées :", len(salles))

# --- Œuvres ---
oeuvres = []
for i in range(20):
    titre = fake.sentence(nb_words=3).rstrip(".")
    oeuvre, created = Oeuvre.objects.get_or_create(
        titre=titre,
        defaults={
            "description": fake.paragraph(nb_sentences=4),
            "description_courte": fake.sentence(nb_words=10),
            "artiste": random.choice(artistes),
            "categorie": random.choice(categories),
            "salle": random.choice(salles),
            "annee": random.randint(1800, 2022),
            "epoque": random.choice(["Renaissance", "Contemporain", "Moderne", "Classique"]),
            "image_miniature": random.choice(images_miniatures),
            "image_haute_resolution": random.choice(images_hd),
            "position_x": random.uniform(-10, 10),
            "position_y": 0,
            "position_z": random.uniform(-10, 10),
            "rotation": random.uniform(0, 360),
            "echelle": random.uniform(0.5, 2.0),
            "dimensions": f"{random.randint(30, 150)} x {random.randint(30, 150)} cm",
            "technique": random.choice(["huile sur toile", "acrylique", "marbre", "bronze"]),
            "materiau": random.choice(["toile", "bois", "pierre", "métal"]),
            "collection": random.choice(["Collection nationale", "Privée", "Musée du Louvre"]),
            "numero_inventaire": f"INV-{1000 + i}",
            "nombre_vues": random.randint(0, 500),
            "est_mise_en_avant": random.choice([True, False]),
        }
    )
    oeuvres.append(oeuvre)

print("✅ Œuvres créées :", len(oeuvres))

# --- Favoris ---
for _ in range(15):
    Favori.objects.get_or_create(
        utilisateur=random.choice(users),
        oeuvre=random.choice(oeuvres),
        defaults={
            "note": random.randint(1, 5),
            "commentaire": fake.sentence(nb_words=15)
        }
    )

print("✅ Favoris ajoutés.")

# --- Visites ---
for _ in range(30):
    Visite.objects.get_or_create(
        utilisateur=random.choice(users),
        oeuvre=random.choice(oeuvres),
        defaults={
            "duree_secondes": random.randint(30, 300)
        }
    )

print("✅ Visites enregistrées.")

# --- Commentaires ---
for _ in range(25):
    Commentaire.objects.get_or_create(
        utilisateur=random.choice(users),
        oeuvre=random.choice(oeuvres),
        defaults={
            "contenu": fake.paragraph(nb_sentences=3),
            "est_approuve": random.choice([True, False])
        }
    )

print("✅ Commentaires créés.")

print("\n🎨 Données de test générées avec succès !")
