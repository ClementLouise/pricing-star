# Premier prompt Claude Code — Pricing Star

## Étape 1 — Préparer ton repo (terminal local, AVANT Claude Code)

```bash
# 1. Créer le dossier projet
mkdir pricing-star
cd pricing-star

# 2. Dezipper le bundle dedans (adapter le chemin selon où tu as téléchargé)
unzip ~/Downloads/pricing_star_complete_bundle.zip -d .

# 3. Initialiser git
git init -q
git branch -M main

# 4. Créer un .gitignore minimal
cat > .gitignore << 'EOF'
node_modules/
__pycache__/
*.pyc
.venv/
venv/
.env
.env.local
.DS_Store
dist/
build/
*.log
.pytest_cache/
coverage/
.vscode/
.idea/
EOF

# 5. Premier commit pour avoir un point de départ propre
git add .
git commit -m "chore: initial PRD bundle and CLAUDE.md"

# 6. Lancer Claude Code dans ce dossier
claude code
```

## Étape 2 — Premier prompt à coller dans Claude Code

Copie-colle exactement ce qui suit dans Claude Code :

---

```
Hello Claude Code. This is Pricing Star, a pre-Phase 0 SaaS project for mid-cap 
pharma pricing intelligence. Your task right now is ORIENTATION ONLY — no code 
generation in this round.

Please do the following, in this exact order:

# Step 1: Read foundational files

Read these in order, treating them as your primary specification:

1. CLAUDE.md (root) — your operating instructions for this repo
2. docs/PRD_v2/00_README.md — PRD navigation and constraints
3. docs/PRD_v2/01_PRODUCT_VISION.md — product context
4. docs/PRD_v2/11_BUILD_ORDER.md — phased roadmap
5. docs/PRD_v2/13_TRIAL_MODE.md — GTM-critical architecture you must understand 
   before Phase 0 starts
6. docs/reference/README.md — what's in the reference materials directory
7. docs/PRD_v2/02_TECH_STACK.md — but note: I have made these specific choices 
   that override the PRD where it offers options:

   - Hosting: **Railway** (not AWS) — for MVP at minimum
   - Repo: **GitHub** (already initialized in this directory)
   - Auth: **Auth0 free tier** for MVP (Keycloak migration deferred)
   - Cloud architecture: SaaS multi-tenant **Option A** (centralized, isolation by tenant_id)
   - Trial mode is **mandatory in Phase 0**, not deferred

# Step 2: Confirm understanding

After reading, write me a brief response (max 500 words) covering:

a) **Product summary in 3 sentences**: What is Pricing Star, who is it for, what 
   is the GTM strategy?

b) **Three non-negotiable rules** you identified from CLAUDE.md, and confirm you 
   understand WHY each one matters.

c) **Trial Mode core insight**: In one paragraph, explain why Trial Mode is GTM-
   critical and how it's implemented architecturally.

d) **One question or ambiguity** you noticed while reading the PRD — something 
   you'd want clarified before coding. Be specific. If everything seems crystal 
   clear, tell me you have no questions (this is rare and worth noting).

# Step 3: Propose Phase 0 plan

Propose a Phase 0 execution plan with the following structure:

- A list of all tasks for Phase 0 (use the checklist in 11_BUILD_ORDER.md as 
  baseline, but ADD any task that is implied by Trial Mode requirements or by 
  the Railway-specific deployment that aren't in the original list)
- For each task: estimated effort (S = <2h, M = 2-8h, L = 1-3 days, XL = >3 days)
- Critical path identification (which tasks block the most downstream work)
- A proposed task ordering for the first week

# Step 4: STOP

Do NOT write any code, do NOT initialize npm, do NOT touch the filesystem 
(except reading). Wait for my validation of your understanding and plan before 
moving forward.

If anything in this prompt is unclear, ask me before starting Step 1.
```

---

## Étape 3 — Ce à quoi t'attendre

Claude Code va passer 5-15 minutes à lire le PRD (peut-être plus selon la longueur). Sa réponse devrait :

✅ **Bon signe** : Sortir une synthèse cohérente du produit, identifier les 3 règles non-négociables (engine V1.7 préservé / multi-tenancy / audit append-only), comprendre l'asymétrie MFN comme insight central

⚠️ **Signal d'alerte** : Réponse vague type "I'll build a pharma pricing platform with React and Python" → indique qu'il a survolé le PRD. Reprends le prompt.

🔴 **Bloquant** : Il commence à écrire du code malgré l'instruction "Step 4: STOP" → Re-cadre fermement avec : "You violated Step 4 of my prompt. Please undo any changes and restart from Step 1."

## Étape 4 — Suite (après validation)

Une fois sa proposition validée, voici les **3 prompts suivants** que tu utiliseras dans la même session :

### Prompt 2 (après validation Phase 0 plan)

```
Approved plan. Execute Phase 0 tasks in the order you proposed, but with these constraints:

1. Pause after each task for me to review (don't batch 5 tasks in one go)
2. After each task, run any tests you wrote and show me the output
3. Do NOT push to GitHub or any remote yet — local commits only
4. Use Conventional Commits format
5. If you encounter a blocker (missing info, ambiguous spec, decision needed), STOP and ask me — don't guess

Start with Task #1.
```

### Prompt 3 (mid-Phase 0 checkpoint, optionnel)

```
Pause. Before continuing, give me a status update:

- Tasks completed (with brief description of what each did)
- Tasks remaining in Phase 0
- Any deviations from the original plan and why
- Anything you want me to validate before continuing

Then wait for my "continue" before moving to the next task.
```

### Prompt 4 (transition Phase 0 → Phase 1)

```
Phase 0 looks complete. Before starting Phase 1 (calc engine port), please:

1. Read docs/PRD_v2/04_CALC_ENGINE_SPEC.md and docs/PRD_v2/10_TEST_FIXTURES.md in full
2. Read docs/reference/PharmaPricingTool_V1.7.jsx — focus on the line ranges 
   referenced in 04_CALC_ENGINE_SPEC.md
3. Read docs/reference/run_vertex_test_v11.py and run_oncmab_test_v20.py 
   — these are reference Python implementations
4. Propose a Phase 1 execution plan with the same structure as Phase 0 (tasks, 
   effort estimates, critical path)
5. Identify which V1.7 functions you have the most/least confidence porting 
   correctly
6. STOP and wait for my validation

Critical reminder: The calc engine logic is preserved verbatim from V1.7. 
Test fixtures must pass. Any deviation = bug.
```

## Tips pour toute la session

**1. Garde le control sur les commits**
Demande explicitement à Claude Code de ne PAS commiter automatiquement. Tu reviewes, puis tu commits toi-même (ou tu lui demandes de commiter avec un message précis).

**2. Si Claude Code "improvise"**
Tout dérapage (ex: il ajoute une feature non spécifiée, il change un choix de tech stack) → réponse immédiate :
```
Stop. That deviates from the PRD. Revert the change and explain why you 
proposed it. If the PRD is unclear on this, raise a clarification question 
instead of inventing a solution.
```

**3. Si une session devient trop longue**
Claude Code peut "perdre" du contexte sur très longues sessions. À chaque transition de phase, redémarre une nouvelle session avec un prompt récapitulatif :
```
This is a new session continuing the Pricing Star build. We have completed 
Phase 0 (foundation). I am now starting Phase 1 (calc engine port). Please 
read CLAUDE.md and docs/PRD_v2/04_CALC_ENGINE_SPEC.md before proceeding.
```

**4. Si un prompt produit un mauvais résultat**
N'essaie pas de "réparer" en ajoutant un autre message. **Reverte avec git** et reformule le prompt. Mieux vaut 5 reverts qu'un repo cassé.

**5. Respecte le budget de tokens**
Claude Code a un context window limité. Lui faire relire 9000 lignes de PRD à chaque message = gaspillage. Le CLAUDE.md est conçu pour qu'il sache quoi lire et quand. Fais-lui confiance.

---

*Bonne build ! Si tu as une question pendant la session Claude Code, tu peux toujours revenir ici pour analyse.*
