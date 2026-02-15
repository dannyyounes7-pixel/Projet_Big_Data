# Guide de Déploiement Git - IAR Platform

## Étapes Complétées ✓

1. ✓ Initialisation du dépôt Git local
2. ✓ Ajout de tous les fichiers (sauf ceux dans .gitignore)
3. ✓ Premier commit créé

## Prochaines Étapes

### Option 1: GitHub (Recommandé)

#### 1. Créer un nouveau dépôt sur GitHub
- Aller sur https://github.com/new
- Nom du dépôt: `bigdata-iar-platform` (ou autre nom)
- Description: "Big Data platform for analyzing French communes - IAR index"
- **NE PAS** initialiser avec README, .gitignore ou licence (on les a déjà)
- Cliquer sur "Create repository"

#### 2. Lier le dépôt local à GitHub
```bash
git remote add origin https://github.com/VOTRE_USERNAME/bigdata-iar-platform.git
git branch -M main
git push -u origin main
```

#### 3. Vérifier
```bash
git remote -v
```

### Option 2: GitLab

#### 1. Créer un nouveau projet sur GitLab
- Aller sur https://gitlab.com/projects/new
- Nom du projet: `bigdata-iar-platform`
- Visibilité: Privé ou Public
- **NE PAS** initialiser avec README
- Cliquer sur "Create project"

#### 2. Lier le dépôt local à GitLab
```bash
git remote add origin https://gitlab.com/VOTRE_USERNAME/bigdata-iar-platform.git
git branch -M main
git push -u origin main
```

### Option 3: Autre service Git (Bitbucket, etc.)

Suivre les instructions fournies par le service.

## Commandes Git Utiles

### Vérifier l'état
```bash
git status
```

### Voir l'historique
```bash
git log --oneline
```

### Ajouter des modifications futures
```bash
git add .
git commit -m "Description des changements"
git push
```

### Créer une branche
```bash
git checkout -b feature/nouvelle-fonctionnalite
```

### Fusionner une branche
```bash
git checkout main
git merge feature/nouvelle-fonctionnalite
```

## Fichiers Ignorés

Le `.gitignore` exclut automatiquement:
- Fichiers de données volumineux (*.xlsx)
- Data lake (fichiers .parquet)
- Environnements virtuels (venv/)
- Logs (logs/*.txt)
- Cache Python (__pycache__/)
- Fichiers IDE (.vscode/, .idea/)

## Structure du Dépôt

```
bigdata-iar-platform/
├── .git/                 # Dépôt Git (caché)
├── .gitignore           # Fichiers à ignorer
├── README.md            # Documentation principale
├── requirements.txt     # Dépendances Python
├── config/              # Configurations
├── src/                 # Code source
├── api/                 # API REST
├── viz/                 # Visualisation
├── scripts/             # Scripts d'automatisation
└── docs/                # Documentation
```

## Bonnes Pratiques

1. **Commits fréquents**: Faire des commits réguliers avec des messages clairs
2. **Messages descriptifs**: Utiliser des messages de commit informatifs
3. **Branches**: Utiliser des branches pour les nouvelles fonctionnalités
4. **Pull avant Push**: Toujours faire `git pull` avant `git push`
5. **Ne jamais commit**: Mots de passe, clés API, données sensibles

## Collaboration

### Cloner le dépôt (pour d'autres utilisateurs)
```bash
git clone https://github.com/VOTRE_USERNAME/bigdata-iar-platform.git
cd bigdata-iar-platform
pip install -r requirements.txt
```

### Mettre à jour depuis le dépôt distant
```bash
git pull origin main
```

## Dépannage

### Erreur: "remote origin already exists"
```bash
git remote remove origin
git remote add origin URL_DU_DEPOT
```

### Annuler le dernier commit (non pushé)
```bash
git reset --soft HEAD~1
```

### Voir les différences
```bash
git diff
```

## Prochaines Étapes Recommandées

1. Créer un dépôt sur GitHub/GitLab
2. Pousser le code avec `git push`
3. Ajouter un fichier LICENSE
4. Configurer GitHub Actions pour CI/CD (optionnel)
5. Ajouter des badges au README (optionnel)

---

**Votre dépôt local est prêt !** Il ne reste plus qu'à le pousser vers GitHub/GitLab.
