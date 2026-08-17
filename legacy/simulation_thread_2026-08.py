import sys
import random
import math
import csv
import pygame

# --- CONFIGURATION INITIALE ---
LARGEUR, HAUTEUR = 1000, 850
LARGEUR_GRAPH, HAUTEUR_GRAPH = 700, 700
FPS = 60

# Paramètres sociologiques fixes
FORCE_CONFORMISME = 0.02
FORCE_MEDIA = 0.01
PROBA_FAKE_NEWS = 0.01

# Variables dynamiques ajustables
seuil_censure = 0.4
nb_fact_checkers = 5

# Structures de données pour l'exportation
temps_simulation = 0
historique_logs = ["Minute 0 : Lancement de la simulation sociale."]
tous_les_logs_sauvegarde = ["Minute 0 : Lancement de la simulation sociale."]
donnees_csv_polarisation = [["Minute", "Seuil_Censure_Bulle", "Fact_Checkers", "Infectes",
"Polarisation_Pourcentage"]]

# Couleurs du compas
COULEUR_BD = (230, 245, 230)
COULEUR_BG = (255, 230, 230)
COULEUR_HD = (230, 230, 255)
COULEUR_HG = (255, 255, 230)

class Media:
    def __init__(self, nom, x_opinion, y_opinion, couleur):
        self.nom = nom
        self.opinion = pygame.Vector2(x_opinion, y_opinion)
        self.couleur = couleur

    def dessiner(self, surface):
        pos_x = int((self.opinion.x + 1) / 2 * (LARGEUR_GRAPH - 100) + 50)
        pos_y = int((self.opinion.y + 1) / 2 * (HAUTEUR_GRAPH - 100) + 50)
        pygame.draw.rect(surface, (0, 0, 0), (pos_x - 14, pos_y - 14, 28, 28))
        pygame.draw.rect(surface, self.couleur, (pos_x - 10, pos_y - 10, 20, 20))


class FactChecker:
    def __init__(self):
        self.opinion = pygame.Vector2(random.uniform(-0.8, 0.8), random.uniform(-0.8, 0.8))
        self.vitesse = pygame.Vector2(random.uniform(-0.01, 0.01), random.uniform(-0.01, 0.01))

    def patrouiller(self, population):
        self.vitesse += pygame.Vector2(random.uniform(-0.002, 0.002), random.uniform(-0.002, 0.002))
        if self.vitesse.length() > 0.015:
            self.vitesse.scale_to_length(0.015)
        self.opinion += self.vitesse

        if abs(self.opinion.x) > 1.0: self.vitesse.x *= -1
        if abs(self.opinion.y) > 1.0: self.vitesse.y *= -1

        for citoyen in population:
            if citoyen.infecte_fake:
                if self.opinion.distance_to(citoyen.opinion) < 0.15:
                    citoyen.infecte_fake = False
                    ajouter_log("Un Fact-Checker a soigné un citoyen.")

    def dessiner(self, surface):
        pos_x = int((self.opinion.x + 1) / 2 * (LARGEUR_GRAPH - 100) + 50)
        pos_y = int((self.opinion.y + 1) / 2 * (HAUTEUR_GRAPH - 100) + 50)
        points = [(pos_x, pos_y - 8), (pos_x + 6, pos_y), (pos_x, pos_y + 8), (pos_x - 6, pos_y)]
        pygame.draw.polygon(surface, (0, 180, 255), points)
        pygame.draw.polygon(surface, (0, 0, 0), points, 1)


class Citoyen:
    def __init__(self, id_citoyen):
        self.id = id_citoyen
        self.opinion = pygame.Vector2(random.uniform(-0.1, 0.1), random.uniform(-0.1, 0.1))
        self.infecte_fake = False

    def interagir_reseau_social(self, population):
        global seuil_censure
        tentatives = 0
        autre = random.choice(population)

        while autre.id == self.id or self.opinion.distance_to(autre.opinion) > seuil_censure:
            autre = random.choice(population)
            tentatives += 1
            if tentatives > 20:
                return

        distance = self.opinion.distance_to(autre.opinion)
        if distance > 0:
            vecteur_attraction = autre.opinion - self.opinion
            self.opinion += vecteur_attraction * FORCE_CONFORMISME

        if autre.infecte_fake and not self.infecte_fake:
            if random.random() < PROBA_FAKE_NEWS:
                self.infecter("Contagion")

    def infecter(self, source="Inconnu"):
        if not self.infecte_fake:
            self.infecte_fake = True
            quadrant = self.obtenir_nom_quadrant()
            ajouter_log(f"Fake News propagée ({source}) dans le pôle {quadrant}.")

        self.opinion.x = 1.0 if self.opinion.x > 0 else -1.0
        self.opinion.y = 1.0 if self.opinion.y > 0 else -1.0

    def obtenir_nom_quadrant(self):
        eco = "Droite" if self.opinion.x > 0 else "Gauche"
        soc = "Aut" if self.opinion.y < 0 else "Lib"
        return f"{eco}-{soc}"

    def subir_medias(self, medias):
        for media in medias:
            distance = self.opinion.distance_to(media.opinion)
            if distance < 0.5:
                vecteur_media = media.opinion - self.opinion
                self.opinion += vecteur_media * FORCE_MEDIA

        self.opinion.x = max(-1.0, min(1.0, self.opinion.x))
        self.opinion.y = max(-1.0, min(1.0, self.opinion.y))

    def dessiner(self, surface):
        pos_x = int((self.opinion.x + 1) / 2 * (LARGEUR_GRAPH - 100) + 50)
        pos_y = int((self.opinion.y + 1) / 2 * (HAUTEUR_GRAPH - 100) + 50)

        if self.infecte_fake:
            couleur = (255, 255, 255)
            taille = 6
        else:
            r = int((self.opinion.x + 1) / 2 * 255)
            g = int((self.opinion.y + 1) / 2 * 255)
            b = int((1 - abs(self.opinion.x)) * 150)
            couleur = (r, g, b)
            taille = 4

        pygame.draw.circle(surface, (20, 20, 20), (pos_x, pos_y), taille + 1)
        pygame.draw.circle(surface, couleur, (pos_x, pos_y), taille)


def ajouter_log(texte):
    global temps_simulation, historique_logs, tous_les_logs_sauvegarde
    minute = temps_simulation // FPS
    log = f"Min {minute} : {texte}"

    if not tous_les_logs_sauvegarde or tous_les_logs_sauvegarde[-1] != log:
        tous_les_logs_sauvegarde.append(log)
        historique_logs.append(log)
        if len(historique_logs) > 8:
            historique_logs.pop(0)


def calculer_polarisation(population):
    if not population: return 0
    somme_distances = 0
    for c in population:
        dist = math.sqrt(c.opinion.x**2 + c.opinion.y**2)
        somme_distances += dist
    distance_moyenne = somme_distances / len(population)
    pourcentage = (distance_moyenne / math.sqrt(2)) * 100
    return min(100, int(pourcentage))


def exporter_donnees():
    """Génère les fichiers physiques txt et csv lors de la fermeture."""
    print("\n--- FERMETURE DETECTEE : EXPORTATION DES DONNÉES EN COURS ---")

    # 1. Export du fichier texte historique
    try:
        with open("logs_simulation.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(tous_les_logs_sauvegarde))
        print("✓ Fichier 'logs_simulation.txt' créé avec succès.")
    except Exception as e:
        print(f"Erreur lors de l'écriture du fichier texte : {e}")

    # 2. Export du fichier CSV pour analyse statistique
    try:
        with open("donnees_polarisation.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerows(donnees_csv_polarisation)
        print("✓ Fichier 'donnees_polarisation.csv' créé avec succès.")
    except Exception as e:
        print(f"Erreur lors de l'écriture du fichier CSV : {e}")

    print("--- FIN DE L'EXPORTATION ---")


def dessiner_interface(surface, police, population, alerte_seuil):
    surface.fill((235, 238, 243))

    mid_x, mid_y = LARGEUR_GRAPH // 2, HAUTEUR_GRAPH // 2
    pygame.draw.rect(surface, COULEUR_BG, (50, 50, mid_x - 50, mid_y - 50))
    pygame.draw.rect(surface, COULEUR_BD, (mid_x, 50, mid_x - 50, mid_y - 50))
    pygame.draw.rect(surface, COULEUR_HG, (50, mid_y, mid_x - 50, mid_y - 50))
    pygame.draw.rect(surface, COULEUR_HD, (mid_x, mid_y, mid_x - 50, mid_y - 50))

    pygame.draw.line(surface, (120, 120, 120), (50, mid_y), (LARGEUR_GRAPH - 50, mid_y), 2)
    pygame.draw.line(surface, (120, 120, 120), (mid_x, 50), (mid_x, HAUTEUR_GRAPH - 50), 2)

    surface.blit(police.render("GAUCHE", True, (150, 0, 0)), (55, mid_y + 10))
    surface.blit(police.render("DROITE", True, (0, 0, 150)), (LARGEUR_GRAPH - 110, mid_y + 10))
    surface.blit(police.render("AUTORITAIRE", True, (50, 50, 50)), (mid_x - 45, 55))
    surface.blit(police.render("LIBERTAIRE", True, (50, 50, 50)), (mid_x - 40, HAUTEUR_GRAPH - 75))

    px = LARGEUR_GRAPH + 20
    pygame.draw.rect(surface, (255, 255, 255), (px, 50, 250, 420))
    pygame.draw.rect(surface, (200, 200, 200), (px, 50, 250, 420), 2)

    nb_infectes = sum(1 for c in population if c.infecte_fake)
    censure_pct = int((2.0 - seuil_censure) / 2.0 * 100)
    polarisation = calculer_polarisation(population)

    # Capture des données à chaque nouvelle minute ronde pour le CSV
    minute_actuelle = temps_simulation // FPS
    if temps_simulation % FPS == 0:
        # Évite d'enregistrer des lignes en double pour la même minute
        if len(donnees_csv_polarisation) == 1 or donnees_csv_polarisation[-1][0] != minute_actuelle:
            donnees_csv_polarisation.append([minute_actuelle, censure_pct, nb_fact_checkers, nb_infectes,
polarisation])

    if polarisation > 60 and not alerte_seuil[0]:
        alerte_seuil[0] = True
        ajouter_log("ALERTE : Polarisation supérieure à 60 % !")
    elif polarisation <= 60:
        alerte_seuil[0] = False

    surface.blit(police.render("COMMANDES CLAVIER :", True, (0, 0, 0)), (px + 10, 65))
    surface.blit(police.render("[ESPACE] : Lancer Fake News", True, (80, 80, 80)), (px + 10, 90))
    surface.blit(police.render("[HAUT/BAS] : Ajuster Censure", True, (80, 80, 80)), (px + 10, 110))
    surface.blit(police.render("[GAUCHE/DRT] : +/- Fact-Checkers", True, (80, 80, 80)), (px + 10, 130))

    surface.blit(police.render("DONNÉES TEMPS RÉEL :", True, (0, 0, 0)), (px + 10, 175))
    surface.blit(police.render(f"Bulle de filtre : {censure_pct} %", True, (255, 0, 0) if seuil_censure < 0.3
else (0, 150, 0)), (px + 10, 200))
    surface.blit(police.render(f"Fact-Checkers actifs : {nb_fact_checkers}", True, (0, 120, 255)), (px + 10,
230))
    surface.blit(police.render(f"Citoyens infectés : {nb_infectes} / {len(population)}", True, (200, 0, 100)),
(px + 10, 260))

    surface.blit(police.render(f"POLARISATION GLOBALE : {polarisation} %", True, (150, 0, 200)), (px + 10,
310))
    fond_barre = pygame.Rect(px + 10, 335, 230, 20)
    pygame.draw.rect(surface, (235, 235, 235), fond_barre)
    largeur_jauge = int(230 * (polarisation / 100))
    pygame.draw.rect(surface, (140, 30, 180), pygame.Rect(px + 10, 335, largeur_jauge, 20))
    pygame.draw.rect(surface, (100, 100, 100), fond_barre, 1)

    # Box de l'historique
    pygame.draw.rect(surface, (20, 25, 35), (50, HAUTEUR_GRAPH + 10, LARGEUR - 100, 110))
    pygame.draw.rect(surface, (100, 105, 120), (50, HAUTEUR_GRAPH + 10, LARGEUR - 100, 110), 2)
    surface.blit(police.render("FIL HISTORIQUE DES ÉVÉNEMENTS (LOGS ET EXPORT AUTOMATIQUE AU
QUITTER) :", True, (0, 255, 150)), (65, HAUTEUR_GRAPH + 20))

    offset_y = HAUTEUR_GRAPH + 45
    for log in historique_logs:
    texte_log = police.render(log, True, (230, 235, 245))
    surface.blit(texte_log, (65, offset_y))
    offset_y += 15

def main():
global seuil_censure, nb_fact_checkers, temps_simulation
pygame.init()
ecran = pygame.display.set_mode((LARGEUR, HAUTEUR))
pygame.display.set_caption("Simulation Sociologique : Système d'Exportation Reynolds")
horloge = pygame.time.Clock()
police = pygame.font.SysFont("Arial", 13, bold=True)

population = [Citoyen(i) for i in range(200)]
medias = [
Media("Média Rouge", -0.8, -0.8, (200, 0, 0)),
Media("Média Vert", -0.8, 0.8, (0, 180, 0)),
Media("Média Bleu", 0.8, -0.8, (0, 0, 200)),
Media("Média Jaune", 0.8, 0.8, (200, 200, 0))
]
fact_checkers = [FactChecker() for _ in range(nb_fact_checkers)]
alerte_seuil = [False]

try:
while True:
temps_simulation += 1

for evenement in pygame.event.get():
if evenement.type == pygame.QUIT:
exporter_donnees()
pygame.quit()
sys.exit()

if evenement.type == pygame.KEYDOWN:
if evenement.key == pygame.K_SPACE:
random.choice(population).infecter("Patient Zéro")
elif evenement.key == pygame.K_UP:
seuil_censure = max(0.12, seuil_censure - 0.05)
ajouter_log(f"Algorithme durci (Seuil : {seuil_censure:.2f}).")
elif evenement.key == pygame.K_DOWN:
seuil_censure = min(1.5, seuil_censure + 0.05)
ajouter_log(f"Algorithme assoupli (Seuil : {seuil_censure:.2f}).")
elif evenement.key == pygame.K_RIGHT:
nb_fact_checkers += 1
fact_checkers.append(FactChecker())
ajouter_log(f"Déploiement d'un nouveau Fact-Checker ({nb_fact_checkers} au total).")
elif evenement.key == pygame.K_LEFT:
if nb_fact_checkers > 0:
nb_fact_checkers -= 1
fact_checkers.pop()
ajouter_log(f"Retrait d'un Fact-Checker ({nb_fact_checkers} au total).")

for _ in range(2):
for citoyen in population:
citoyen.interagir_reseau_social(population)
citoyen.subir_medias(medias)

for fc in fact_checkers:
fc.patrouiller(population)

dessiner_interface(ecran, police, population, alerte_seuil)
for citoyen in population: citoyen.dessiner(ecran)
for media in medias: media.dessiner(ecran)
for fc in fact_checkers: fc.dessiner(ecran)

pygame.display.flip()
horloge.tick(FPS)

except KeyboardInterrupt:
# Permet aussi de récupérer les exports si on coupe le script via Ctrl+C dans le terminal
exporter_donnees()
pygame.quit()
sys.exit()

if name == "main":
main()
