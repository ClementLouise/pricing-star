# Setup Pricing Star — GitHub + Railway + Local (Windows)

Guide pas-à-pas pour créer le repo GitHub, le projet Railway, et préparer ton environnement local Windows pour lancer Claude Code.

**Durée totale estimée** : 30-45 minutes

---

## Phase A — Créer le repo GitHub (10 min)

### A.1 Créer le repo sur github.com

1. Va sur **https://github.com/new**
2. Remplis le formulaire :
   - **Repository name** : `pricing-star`
   - **Description** : `Navigate MFN. Defend NPV. — SaaS for mid-cap pharma pricing intelligence.`
   - **Visibility** : **Private** ⚠️ (important — ton PRD et ta stratégie ne doivent pas être publics)
   - ⛔ **NE coche PAS** "Add a README file"
   - ⛔ **NE coche PAS** "Add .gitignore"
   - ⛔ **NE coche PAS** "Choose a license"
   
   *(Tu vas pousser ton propre contenu, donc tu veux un repo VIDE)*

3. Clique **Create repository**

4. GitHub te montre maintenant une page avec des instructions. **Note l'URL HTTPS de ton repo**, ça ressemble à :
   ```
   https://github.com/TON-USERNAME/pricing-star.git
   ```
   Tu en auras besoin tout à l'heure.

### A.2 Vérifier que git est installé sur Windows

Ouvre **PowerShell** (Windows Terminal ou cmd) et tape :

```powershell
git --version
```

- ✅ Si tu vois `git version 2.x.x` → tout va bien, passe à A.3
- ❌ Si commande inconnue → installe Git pour Windows depuis **https://git-scm.com/download/win**, puis relance PowerShell

### A.3 Configurer git (une fois pour toutes)

Si tu n'as jamais configuré git sur cette machine :

```powershell
git config --global user.name "Ton Nom"
git config --global user.email "ton-email@example.com"
git config --global init.defaultBranch main
```

⚠️ **Important** : utilise le **même email que ton compte GitHub**, sinon les commits ne te seront pas attribués.

### A.4 Authentification GitHub depuis Windows

Pour pouvoir `git push` vers GitHub, il te faut un **Personal Access Token** (PAT). Le mot de passe normal ne marche plus depuis 2021.

1. Va sur **https://github.com/settings/tokens**
2. Clique **Generate new token** → **Generate new token (classic)**
3. Remplis :
   - **Note** : `Pricing Star — Windows Dev Machine`
   - **Expiration** : `90 days` (à renouveler)
   - **Select scopes** : coche uniquement **`repo`** (Full control of private repositories)
4. Clique **Generate token** en bas
5. **COPIE LE TOKEN MAINTENANT** (ressemble à `ghp_xxxxxxxxxxxxxxxxxxxxxxxx`). GitHub ne te le remontrera JAMAIS. Si tu le perds, tu devras en générer un nouveau.
6. **Stocke-le dans ton gestionnaire de mots de passe** (1Password, Bitwarden, KeePass...).

**Quand est-ce que tu utilises ce token ?** La première fois que tu fais `git push`, Windows te demandera tes credentials. Tu mets :
- **Username** : ton nom d'utilisateur GitHub
- **Password** : **le token** (PAS ton mot de passe GitHub)

Windows mémorise ça via "Credential Manager" et tu n'as plus à le retaper.

---

## Phase B — Préparer le projet en local (10 min)

### B.1 Choisir où créer le projet

Décide d'un dossier parent où vivront tes projets de code. Suggestion :

```powershell
# Créer un dossier projets si tu n'en as pas
mkdir C:\Users\TON-USERNAME\projects
cd C:\Users\TON-USERNAME\projects
```

⚠️ **Évite** OneDrive/Dropbox/Google Drive pour héberger des projets de code — la synchro fait des conflits avec node_modules et casse Git.

### B.2 Créer le dossier et dezipper le bundle

```powershell
# Créer le dossier
mkdir pricing-star
cd pricing-star

# Dezipper le bundle (adapte le chemin selon où tu as téléchargé le ZIP)
Expand-Archive -Path "$env:USERPROFILE\Downloads\pricing_star_complete_bundle.zip" -DestinationPath . -Force
```

Vérifie que tout est là :

```powershell
dir
```

Tu devrais voir : `CLAUDE.md`, `branding/`, `docs/`

### B.3 Initialiser Git localement

```powershell
git init
git branch -M main
```

### B.4 Créer le `.gitignore`

```powershell
@"
# Dependencies
node_modules/
__pycache__/
*.pyc
.venv/
venv/

# Build outputs
dist/
build/
.next/

# Environment & secrets (CRITIQUE)
.env
.env.local
.env.*.local
*.pem
*.key
secrets/

# IDE
.vscode/
.idea/
*.swp

# Windows / Mac system files
.DS_Store
Thumbs.db
desktop.ini

# Logs
*.log
logs/

# Test artifacts
coverage/
.coverage
.pytest_cache/

# Database
*.sqlite
*.sqlite3
"@ | Out-File -FilePath .gitignore -Encoding utf8
```

Vérifie qu'il a été créé :

```powershell
type .gitignore
```

### B.5 Premier commit local

```powershell
git add .
git commit -m "chore: initial Pricing Star PRD bundle and reference materials"
```

Tu devrais voir un message indiquant que ~30 fichiers ont été ajoutés.

### B.6 Connecter le repo local à GitHub et push

```powershell
# Remplace TON-USERNAME par ton vrai username GitHub
git remote add origin https://github.com/TON-USERNAME/pricing-star.git

# Push initial
git push -u origin main
```

**À ce moment** : Windows va te demander tes credentials.
- Username : ton GitHub username
- Password : **ton Personal Access Token** (celui copié à l'étape A.4)

✅ Si succès, ouvre `https://github.com/TON-USERNAME/pricing-star` dans ton navigateur et tu vois tes fichiers.

---

## Phase C — Setup Railway (10 min)

⚠️ **Note importante** : Railway n'est techniquement nécessaire qu'à partir de Phase 0/1 du build (quand Claude Code va déployer une vraie app). Tu peux faire cette phase MAINTENANT pour être prêt, ou la décaler quand Claude Code en aura besoin.

**Mon conseil** : fais-le maintenant pour gagner du temps plus tard. C'est rapide.

### C.1 Créer un projet Railway

1. Va sur **https://railway.app/dashboard**
2. Clique **New Project**
3. Choisis **Deploy from GitHub repo**
4. Si Railway n'a pas accès à ton repo `pricing-star` :
   - Clique **Configure GitHub App**
   - Tu arrives sur GitHub : sélectionne **Only select repositories** → coche `pricing-star`
   - Clique **Save**
   - Reviens sur Railway, et tu vois maintenant `pricing-star` dans la liste
5. Sélectionne `pricing-star`

⚠️ Railway va probablement essayer de déployer immédiatement et **échouer** parce que ton repo ne contient pas encore de code applicatif (juste le PRD). C'est normal. **Ignore l'erreur** ou clique sur le déploiement et **annule-le**.

### C.2 Renomme le projet (cosmétique)

Dans Railway, le projet aura un nom auto-généré du genre `pricing-star-production-abc123`. Pour clarifier :

1. Clique sur le projet
2. Clique sur **Settings** (icône engrenage en haut à droite)
3. Renomme en `pricing-star`

### C.3 Provisionner Postgres

Dans le projet Railway :

1. Clique **+ New** (en haut à droite)
2. Sélectionne **Database** → **Add PostgreSQL**
3. Attends 30-60 secondes que Railway provisionne la DB
4. Clique sur le service Postgres → onglet **Variables**
5. **Note les variables disponibles** (tu n'as PAS besoin de les copier maintenant, juste de savoir qu'elles existent) :
   - `DATABASE_URL` (la plus importante)
   - `PGHOST`, `PGPORT`, `PGUSER`, `PGPASSWORD`, `PGDATABASE`

Claude Code utilisera ces variables plus tard via Railway env injection.

### C.4 Provisionner Redis

Même processus :

1. Clique **+ New**
2. **Database** → **Add Redis**
3. Attends 30 secondes
4. Variable `REDIS_URL` sera disponible

### C.5 Récupérer le token Railway (pour CLI plus tard)

Tu auras éventuellement besoin de la **Railway CLI** pour gérer ton projet depuis le terminal. Pas urgent maintenant, mais pour anticiper :

1. Va sur **https://railway.app/account/tokens**
2. **Create Token** → nom : `pricing-star-cli`
3. Copie le token, **stocke-le dans ton gestionnaire de mots de passe**

---

## Phase D — Vérification & Premier prompt Claude Code (5 min)

### D.1 Checklist finale

Avant de lancer Claude Code, vérifie :

- [ ] Repo GitHub `pricing-star` existe et est **privé**
- [ ] Tu as poussé le bundle PRD avec succès (`git push` a fonctionné)
- [ ] Tu vois tous les fichiers sur github.com/TON-USERNAME/pricing-star
- [ ] Projet Railway `pricing-star` créé
- [ ] Postgres + Redis provisionnés sur Railway
- [ ] Personal Access Token GitHub stocké dans gestionnaire de mots de passe
- [ ] Railway token stocké dans gestionnaire de mots de passe

### D.2 Lancer Claude Code

```powershell
# Tu es toujours dans C:\Users\TON-USERNAME\projects\pricing-star
claude code
```

Claude Code s'ouvre dans le contexte de ce dossier.

### D.3 Coller le premier prompt

Le contenu du fichier `FIRST_PROMPT_CLAUDE_CODE.md` que je t'ai livré précédemment, **section "Étape 2 — Premier prompt à coller dans Claude Code"**.

---

## Pièges Windows-spécifiques à éviter

### Piège 1 : Path trop long
Windows a une limite historique de 260 caractères pour les paths. Si tu mets ton projet dans `C:\Users\Prenom\OneDrive\Documents\Projets perso 2026\dev\pricing-star\...`, tu vas avoir des erreurs avec node_modules. **Solution** : garde le path court, mets ton projet dans `C:\Users\TON-USERNAME\projects\pricing-star`.

### Piège 2 : Line endings (CRLF vs LF)
Windows utilise des line endings différents de Mac/Linux. Quand tu ouvres tes `.md` dans certains éditeurs, ça peut polluer git avec des "changements" qui ne sont que des CRLF→LF. **Solution préventive** :

```powershell
git config --global core.autocrlf true
```

### Piège 3 : Antivirus qui bloque node_modules
Certains antivirus Windows scannent agressivement les milliers de petits fichiers de `node_modules` et ralentissent le build à 30 minutes. **Solution** : ajoute ton dossier `projects/` aux exclusions Windows Defender (ou de ton antivirus).

### Piège 4 : PowerShell vs cmd vs WSL
Tu peux travailler dans n'importe quel terminal. **Recommandation** : utilise **Windows Terminal** (gratuit sur Microsoft Store) ou **PowerShell** moderne. Évite cmd.exe (limité). WSL Ubuntu est aussi excellent si tu connais Linux.

### Piège 5 : Caractères spéciaux dans le path
Si ton username Windows contient des accents (ex: `André`), certains outils Python/Node peuvent buguer. **Solution** : crée le projet directement sous `C:\projects\pricing-star` au lieu de dans `C:\Users\André\...`.

---

## Que faire si...

### "git push" demande mes credentials à chaque fois
Solution : installe **Git Credential Manager** (généralement inclus dans Git for Windows récent). Si pas le cas, télécharge-le depuis https://github.com/git-ecosystem/git-credential-manager.

### Railway m'a déployé l'app et je vois plein d'erreurs
C'est normal au début (pas de code applicatif dans le repo). Va dans Railway → Settings → tu peux **désactiver les auto-deploys** jusqu'à ce que Claude Code écrive le vrai code applicatif. Tu réactiveras quand le code Python/React sera là.

### Je veux supprimer le repo et recommencer
- Sur GitHub : Settings du repo → tout en bas, "Danger Zone" → Delete repository
- En local : `Remove-Item -Recurse -Force .\pricing-star\`

### J'ai oublié mon Personal Access Token
Sur https://github.com/settings/tokens : tu ne peux pas le récupérer, mais tu peux **regenerate** ou en créer un nouveau. N'oublie pas de mettre à jour Windows Credential Manager (cherche "Gestionnaire d'identification" dans Windows).

---

## Récap des 3 secrets à stocker

| Secret | Où l'obtenir | Quand l'utiliser |
|---|---|---|
| GitHub Personal Access Token | https://github.com/settings/tokens | Premier `git push`, puis Windows mémorise |
| Railway API Token | https://railway.app/account/tokens | Pour Railway CLI (plus tard) |
| Railway DATABASE_URL | Onglet Variables du service Postgres | Phase 0/1 du build (Claude Code va l'utiliser) |

**Stocke les 3 dans 1Password / Bitwarden / KeePass.** Ne jamais les écrire dans un fichier `.env` qui pourrait être committé.

---

## Et après ?

Quand tu as terminé Phases A + B + C :
1. Ouvre `FIRST_PROMPT_CLAUDE_CODE.md`
2. Lance `claude code` dans ton dossier `pricing-star`
3. Colle le premier prompt
4. Réponds à Claude Code et c'est parti 🚀

Si tu as une erreur ou un doute pendant le setup, reviens vers moi avec le message d'erreur exact et je te débloque.
