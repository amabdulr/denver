# 🐳 Docker Guide for the Denver App

## What Is Docker?

Think of Docker as a **shipping container for software**. Just like a shipping container can hold furniture, electronics, or food and be transported on any truck, train, or ship — a Docker container holds your app, its dependencies, and its settings so it can run on **any machine** the same way.

### Why does this matter?

Without Docker, setting up this app means:
1. Installing Python 3.11
2. Creating a virtual environment
3. Installing all the packages from `requirements.txt`
4. Configuring environment variables
5. Hoping nothing conflicts with your system

With Docker, it's just:
1. Install Docker
2. Run one command

**That's it.** Docker packages everything into an image so the app runs identically whether it's on your Mac, a colleague's Windows PC, or a Linux server.

---

## Key Concepts (Plain English)

| Term | What It Is | Analogy |
|---|---|---|
| **Image** | A snapshot of the app + all its dependencies, frozen in time | A recipe |
| **Container** | A running instance of an image | A dish made from the recipe |
| **Dockerfile** | Instructions to build an image | The recipe card |
| **docker-compose.yml** | A file that describes how to run one or more containers together | A meal plan |
| **Volume** | Persistent storage that survives container restarts | A pantry that doesn't get emptied |
| **Port mapping** | Connecting a port inside the container to one on your machine | A mail forwarding address |
| **.env file** | A file with secrets/config passed into the container | Seasoning added at cook time |

---

## Installing Docker

### macOS

1. Download **Docker Desktop** from [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/)
2. Open the `.dmg` and drag Docker to Applications
3. Launch Docker Desktop — you'll see a whale icon 🐳 in your menu bar
4. Wait until it says **"Docker Desktop is running"**

Verify it works:
```bash
docker --version
docker compose version
```

---

## Your Docker Setup

All Docker files live in the `docker/` folder:

```
docker/
├── Dockerfile          # How to build the app image
├── .dockerignore       # Files to exclude from the image
├── docker-compose.yml  # How to run the container
└── .env.example        # Template for your secrets
```

### How the pieces fit together

The Docker image is **self-contained** — it ships with all app code, ontology
configs, Python dependencies, and empty `knowledge_docs/` product subfolders.
The Admin tab downloads product PDFs at runtime.

```
┌─────────────────────────────────────────────────┐
│  Docker Image (self-contained)                  │
│                                                 │
│  ┌───────────────────────────────────────────┐  │
│  │  Baked into image:                           │  │
│  │    app/*.py          (all app code)           │  │
│  │    ontology/         (guide mappings)         │  │
│  │    prompts/*.md      (prompt templates)        │  │
│  │    Python 3.11 + all pip packages             │  │
│  └───────────────────────────────────────────┘  │
│                                                 │
│  Docker Volumes (persist across restarts):       │
│    knowledge_docs_data ◄── Admin tab downloads   │
│    vectorstore_data    ◄── ChromaDB             │
│    app_config_data     ◄── user preferences     │
│    app_data            ◄── heading cache, etc.  │
│                                                 │
│  .env (injected at runtime) ── API keys          │
│                                                 │
│  browser :8503 ◄──── Streamlit :8501            │
└─────────────────────────────────────────────────┘
```

- Your **secrets** (`.env`) are the only host file — they're injected at runtime, never baked into the image.
- **Ontology configs** (`ontology/`) are baked in — they're small and ship with the image.
- **Product documentation** (`knowledge_docs/`) starts empty. Use the **Admin tab → Download PDFs** to populate it after first launch.
- All runtime data persists in **Docker-managed volumes** that survive container restarts.

---

## Step-by-Step: Running the App

### 1. One-time setup: Create your `.env` file

If you don't already have a `.env` in the project root:

```bash
cp docker/.env.example .env
```

Then edit `.env` and fill in your API keys:

```dotenv
CISCO_API_TYPE=cxai
OPENAI_API_BASE=https://your-api-endpoint.example.com
OPENAI_API_KEY=sk-your-key-here
```

### 2. Build and start

From the **project root** (the `Denver/` folder):

```bash
docker compose -f docker/docker-compose.yml up --build
```

Breaking that down:
- `docker compose` — the Docker Compose command
- `-f docker/docker-compose.yml` — points to our compose file in the `docker/` folder
- `up` — start the service
- `--build` — rebuild the image first (use this the first time, or after code changes)

You'll see logs scrolling by. Once you see Streamlit's startup message, open your browser:

**👉 http://localhost:8503**

### 3. First-time setup: Download product docs

After the app starts, go to the **🛠️ Admin** tab in the sidebar and use **Download PDFs** to download documentation for your product (e.g., SD-WAN). This only needs to be done once — downloaded PDFs persist in a Docker volume.

### 4. Stop the app

Press `Ctrl+C` in the terminal where it's running.

Or, if you started it in the background (see below), run:
```bash
docker compose -f docker/docker-compose.yml down
```

---

## Common Commands

Run all of these from the **project root** (`Denver/` folder).

| What you want to do | Command |
|---|---|
| **Start the app** | `docker compose -f docker/docker-compose.yml up --build` |
| **Start in background** | `docker compose -f docker/docker-compose.yml up -d --build` |
| **View logs** (if running in background) | `docker compose -f docker/docker-compose.yml logs -f` |
| **Stop the app** | `docker compose -f docker/docker-compose.yml down` |
| **Restart the app** | `docker compose -f docker/docker-compose.yml restart` |
| **Full rebuild** (after changing `requirements.txt`) | `docker compose -f docker/docker-compose.yml build --no-cache` |
| **Check if container is running** | `docker ps` |
| **Open a shell inside the container** | `docker exec -it denver-app bash` |
| **View container resource usage** | `docker stats denver-app` |

### 💡 Tip: Make it shorter with an alias

Add this to your `~/.zshrc`:
```bash
alias denver-docker="docker compose -f docker/docker-compose.yml"
```

Then you can just type:
```bash
denver-docker up --build
denver-docker down
denver-docker logs -f
```

---

## When Do I Need to Rebuild?

| What changed | Action needed |
|---|---|
| Edited a `.py` file | Rebuild: `up --build` (code is copied at build time) |
| Added/changed a package in `requirements.txt` | Rebuild: `up --build` (or `build --no-cache` if caching causes issues) |
| Updated ontology configs | Rebuild: `up --build` (`ontology/` is baked into the image) |
| Need to download new product docs | **Nothing!** Use the Admin tab — downloads persist in a Docker volume |
| Changed `.env` values | Restart: `down` then `up` (no rebuild needed) |
| Changed the `Dockerfile` itself | Rebuild: `up --build` |

---

## Troubleshooting

### "Port 8501 is already in use"
Something else is using port 8501 (maybe Streamlit running locally). Either stop it or change the port:
```bash
# Use port 9501 on your machine instead
docker compose -f docker/docker-compose.yml up --build -e 8501:9501
```
Or edit `docker/docker-compose.yml` and change `"8501:8501"` to `"9501:8501"`.

### "Cannot connect to the Docker daemon"
Docker Desktop isn't running. Open it from Applications and wait for the whale icon to stop animating.

### Container starts but app crashes
Check the logs:
```bash
docker compose -f docker/docker-compose.yml logs
```

### "Missing environment variable" errors
Make sure your `.env` file exists in the project root and has all required values. Compare against `docker/.env.example`.

### Want to start fresh?
```bash
# Remove container, image, and volumes
docker compose -f docker/docker-compose.yml down -v --rmi all
# Then rebuild
docker compose -f docker/docker-compose.yml up --build
```

⚠️ The `-v` flag deletes the vector store volume, so ChromaDB will need to re-ingest on next startup.

---

## Docker vs Running Locally — When to Use Which

| Scenario | Recommendation |
|---|---|
| Quick development / debugging | Run locally with `streamlit run sidebar_app.py` |
| Sharing with a teammate | Docker — they just need Docker + your `.env` values |
| Deploying to a server | Docker — consistent environment guaranteed |
| Your Python/SQLite version causes issues | Docker — it bundles Python 3.11 with a modern SQLite |
| First time trying the app | Docker — zero setup beyond installing Docker |

---

## Glossary

- **Build context** — the folder Docker looks at when building an image (our project root)
- **Layer caching** — Docker reuses unchanged steps to speed up rebuilds
- **Bind mount** — linking a specific host file to the container (e.g., `.env` for secrets)
- **Named volume** — Docker-managed storage that persists independently of any container (e.g., `vectorstore_data`, `knowledge_docs_data`)
- **Health check** — a periodic test that Docker runs to make sure the app is responding
- **Multi-stage build** — our Dockerfile uses two stages: one to compile dependencies (with gcc etc.), and a slim one to run the app — this keeps the final image small
