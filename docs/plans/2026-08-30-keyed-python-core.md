# Keyed Python Core Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Construire le coeur Python local de `keyed` pour generer, stocker, verifier, limiter et revoquer des cles API depuis une application FastAPI connectee a PostgreSQL.

**Architecture:** Le chemin de verification extrait un prefixe indexable de la cle recue, charge un unique enregistrement PostgreSQL, verifie le secret par SHA-256 sale et comparaison constante, applique expiration/revocation/scopes, puis consomme le quota dans un sliding window en memoire. Aucun dashboard, endpoint d'administration, proxy cloud, Redis, cache distribue ou SDK Node n'entre dans cette phase.

**Tech Stack:** Python 3.11+, FastAPI, Pydantic 2, asyncpg, pytest, pytest-asyncio, HTTPX, Ruff, mypy.

---

## Decisions techniques verrouillees pour l'implementation

1. Format de cle: `key_<environment>_<public_id>_<secret>`, par exemple `key_live_8f04c1d93a6072be81b94a50980e0187_<secret>`. Le prefixe persiste et indexe est toute la partie jusqu'au dernier separateur inclus. `environment` est limite a `live` ou `test` dans le MVP.
2. Entropie: `public_id` contient 128 bits aleatoires encodes en 32 caracteres hexadecimaux et `secret` provient de 32 octets aleatoires encodes avec `secrets.token_urlsafe`. La cle complete n'est retournee qu'a la creation.
3. Hash: `SHA-256(salt || secret)` avec un sel aleatoire de 32 octets par cle. Le hash et le sel sont stockes en `BYTEA`; la verification utilise `hmac.compare_digest` sur les octets.
4. Justification SHA-256: les secrets sont generes avec au moins 256 bits d'entropie, contrairement aux mots de passe humains. Le PRD et la landing mentionnent encore bcrypt/Argon2; leur correction est un point de validation humaine separe, pas une modification implicite de cette implementation.
5. Persistance: une requete PostgreSQL par verification, indexee par `prefix`. Ce choix preserve la revocation immediate. Aucun cache d'enregistrement dans le MVP.
6. Rate limiting: sliding window exact, local au processus, base sur `time.monotonic()`, avec verrous stripes `threading.Lock`. En deploiement beta, un seul worker est requis; plusieurs workers multiplieraient le quota effectif.
7. Latence: le seuil `<3ms` sera mesure et rapporte, mais ne sera pas un test unitaire bloquant dependant du materiel. Le benchmark separe le cout pur Python du temps de round-trip PostgreSQL.
8. Scopes: correspondance exacte de chaines, sans wildcard ni hierarchie dans le MVP.
9. Semantique HTTP: `401` pour cle absente/invalide/revoquee/expiree, `403` pour scope insuffisant, `429` pour quota depasse. Une cle valide est retournee comme principal de la dependance FastAPI.
10. Aucun commit ni push n'est execute sans validation humaine explicite. Les commits ci-dessous sont uniquement des points de controle proposes.

## Arborescence cible

```text
pyproject.toml
keyed/
  __init__.py
  core/
    __init__.py
    hash.py
    models.py
    rate_limit.py
  middleware/
    __init__.py
    fastapi.py
  storage/
    __init__.py
    base.py
    postgres.py
  migrations/
    001_create_api_keys.sql
  tests/
    __init__.py
    fakes.py
    test_hash.py
    test_models.py
    test_rate_limit.py
    test_postgres.py
    test_fastapi_auth.py
    test_performance.py
```

### Task 1: Initialiser le package et l'outillage

**Files:**
- Create: `pyproject.toml`
- Create: `keyed/__init__.py`
- Create: `keyed/core/__init__.py`
- Create: `keyed/middleware/__init__.py`
- Create: `keyed/storage/__init__.py`
- Create: `keyed/tests/__init__.py`

**Step 1: Definir le package**

Configurer `pyproject.toml` avec Python `>=3.11`, les dependances runtime `fastapi>=0.115,<1`, `pydantic>=2.9,<3`, `asyncpg>=0.29,<1`, et les dependances de developpement `pytest`, `pytest-asyncio`, `httpx`, `ruff`, `mypy`.

**Step 2: Configurer les tests**

Definir `asyncio_mode = "auto"`, les marqueurs `integration` et `performance`, et limiter la collecte a `keyed/tests`.

**Step 3: Installer l'environnement editable**

Run: `python -m venv .venv && .venv/bin/python -m pip install -e '.[dev]'`

Expected: installation terminee sans conflit de dependances.

**Step 4: Verifier le squelette**

Run: `.venv/bin/python -c "import keyed"`

Expected: exit code `0`.

**Step 5: Point de controle Git propose**

```bash
git add pyproject.toml keyed/__init__.py keyed/core/__init__.py keyed/middleware/__init__.py keyed/storage/__init__.py keyed/tests/__init__.py
git commit -m "chore: initialize keyed python package"
```

### Task 2: Modeliser une cle API et ses invariants

**Files:**
- Create: `keyed/core/models.py`
- Create: `keyed/tests/test_models.py`

**Step 1: Ecrire les tests en echec**

Tester les invariants suivants:

```python
def test_api_key_record_rejects_naive_expiration(): ...
def test_api_key_record_rejects_non_positive_rate_limit(): ...
def test_api_key_record_deduplicates_scopes(): ...
def test_api_key_record_reports_revoked_and_expired_state(): ...
```

**Step 2: Verifier l'echec**

Run: `.venv/bin/pytest keyed/tests/test_models.py -v`

Expected: FAIL car `APIKeyRecord` n'existe pas.

**Step 3: Implementer les modeles minimaux**

Creer:

```python
class APIKeyRecord(BaseModel):
    id: UUID
    prefix: str
    key_hash: bytes
    salt: bytes
    scopes: tuple[str, ...] = ()
    rate_limit: int | None = None
    rate_limit_window_seconds: int = 60
    expires_at: datetime | None = None
    revoked_at: datetime | None = None
    created_at: datetime

class GeneratedAPIKey(BaseModel):
    plaintext: str = Field(repr=False)
    record: APIKeyRecord

class AuthenticatedAPIKey(BaseModel):
    id: UUID
    prefix: str
    scopes: tuple[str, ...]
    rate_limit: int | None
```

Ajouter des validateurs pour UTC, limites positives, scopes non vides/dedupliques et tailles de hash/sel egales a 32 octets.

**Step 4: Faire passer les tests**

Run: `.venv/bin/pytest keyed/tests/test_models.py -v`

Expected: PASS.

**Step 5: Point de controle Git propose**

```bash
git add keyed/core/models.py keyed/tests/test_models.py
git commit -m "feat: define api key models"
```

### Task 3: Generer, parser et verifier les cles

**Files:**
- Create: `keyed/core/hash.py`
- Create: `keyed/tests/test_hash.py`

**Step 1: Ecrire les tests en echec**

```python
def test_generate_key_returns_plaintext_once_and_hash_material(): ...
def test_generate_key_uses_dynamic_indexable_prefix(): ...
def test_generated_keys_are_unique(): ...
def test_parse_prefix_rejects_malformed_keys(): ...
def test_verify_accepts_original_secret(): ...
def test_verify_rejects_wrong_secret_and_tampered_prefix(): ...
def test_verify_uses_hmac_compare_digest(monkeypatch): ...
```

**Step 2: Verifier l'echec**

Run: `.venv/bin/pytest keyed/tests/test_hash.py -v`

Expected: FAIL car le module n'existe pas.

**Step 3: Implementer l'API cryptographique**

Exposer uniquement:

```python
def generate_api_key(environment: Literal["live", "test"], **metadata: object) -> GeneratedAPIKey: ...
def extract_prefix(plaintext: str) -> str | None: ...
def verify_api_key(plaintext: str, record: APIKeyRecord) -> bool: ...
```

Utiliser `secrets.token_hex(16)`, `secrets.token_urlsafe(32)`, `secrets.token_bytes(32)`, `hashlib.sha256`, puis `hmac.compare_digest`. Ne jamais logger la cle complete; masquer `GeneratedAPIKey.plaintext` avec `Field(repr=False)`.

**Step 4: Faire passer les tests**

Run: `.venv/bin/pytest keyed/tests/test_hash.py -v`

Expected: PASS.

**Step 5: Point de controle Git propose**

```bash
git add keyed/core/hash.py keyed/tests/test_hash.py
git commit -m "feat: add api key hashing"
```

### Task 4: Implementer le sliding-window local

**Files:**
- Create: `keyed/core/rate_limit.py`
- Create: `keyed/tests/test_rate_limit.py`

**Step 1: Ecrire les tests en echec**

```python
async def test_allows_requests_below_limit(): ...
async def test_rejects_request_above_limit(): ...
async def test_reopens_window_after_old_events_expire(): ...
async def test_isolates_keys(): ...
async def test_concurrent_calls_never_over_admit(): ...
async def test_disabled_limit_always_allows(): ...
def test_cleanup_removes_inactive_buckets(): ...
```

Injecter une horloge factice afin de ne jamais utiliser `sleep()` dans les tests.

**Step 2: Verifier l'echec**

Run: `.venv/bin/pytest keyed/tests/test_rate_limit.py -v`

Expected: FAIL car `SlidingWindowRateLimiter` n'existe pas.

**Step 3: Implementer le limiteur**

Creer un `RateLimitDecision(allowed, limit, remaining, reset_after)` et un `SlidingWindowRateLimiter`. Stocker un `deque[float]` par `key_id`, retirer les timestamps `<= now - window`, puis admettre ou refuser atomiquement sous un verrou stripe. Ajouter une methode `clear(key_id)` pour liberer l'etat lors d'une revocation connue et une purge bornee des buckets inactifs.

**Step 4: Faire passer les tests**

Run: `.venv/bin/pytest keyed/tests/test_rate_limit.py -v`

Expected: PASS, y compris le test concurrent.

**Step 5: Point de controle Git propose**

```bash
git add keyed/core/rate_limit.py keyed/tests/test_rate_limit.py
git commit -m "feat: add in-memory sliding window limiter"
```

### Task 5: Definir le contrat de stockage et la migration PostgreSQL

**Files:**
- Create: `keyed/storage/base.py`
- Create: `keyed/storage/postgres.py`
- Create: `keyed/migrations/001_create_api_keys.sql`
- Create: `keyed/tests/test_postgres.py`

**Step 1: Ecrire le contrat et les tests d'integration en echec**

Le protocole minimal contient:

```python
class APIKeyStore(Protocol):
    async def create(self, record: APIKeyRecord) -> None: ...
    async def get_by_prefix(self, prefix: str) -> APIKeyRecord | None: ...
    async def revoke(self, key_id: UUID, revoked_at: datetime) -> bool: ...
```

Tester creation/lecture, unicite du prefixe, revocation visible a la lecture suivante, types UTC, et absence de plaintext en base.

**Step 2: Verifier l'echec**

Run: `KEYED_TEST_DATABASE_URL=postgresql://... .venv/bin/pytest keyed/tests/test_postgres.py -v -m integration`

Expected: FAIL avant implementation. Si aucune base de test n'est disponible, le test doit etre marque SKIP et ce manque doit etre rapporte explicitement.

**Step 3: Creer la table minimale**

La migration cree `keyed_api_keys` avec `id UUID PRIMARY KEY`, `prefix TEXT UNIQUE NOT NULL`, `key_hash BYTEA NOT NULL`, `salt BYTEA NOT NULL`, `scopes TEXT[] NOT NULL`, `rate_limit INTEGER`, `rate_limit_window_seconds INTEGER NOT NULL`, `expires_at TIMESTAMPTZ`, `revoked_at TIMESTAMPTZ`, `created_at TIMESTAMPTZ NOT NULL`. Ajouter les contraintes positives pour les limites.

**Step 4: Implementer `PostgresAPIKeyStore`**

Utiliser un `asyncpg.Pool` fourni par l'application. Ecrire des requetes parametrees uniquement. Mapper explicitement `asyncpg.Record` vers `APIKeyRecord`. Ne jamais creer un pool global a l'import.

**Step 5: Faire passer l'integration**

Run: `KEYED_TEST_DATABASE_URL=postgresql://... .venv/bin/pytest keyed/tests/test_postgres.py -v -m integration`

Expected: PASS sur une base PostgreSQL jetable.

**Step 6: Point de controle Git propose**

```bash
git add keyed/storage/base.py keyed/storage/postgres.py keyed/migrations/001_create_api_keys.sql keyed/tests/test_postgres.py
git commit -m "feat: add postgres api key store"
```

### Task 6: Integrer l'authentification FastAPI

**Files:**
- Create: `keyed/middleware/fastapi.py`
- Create: `keyed/tests/fakes.py`
- Create: `keyed/tests/test_fastapi_auth.py`

**Step 1: Ecrire les tests ASGI en echec**

Construire une application FastAPI de test via `httpx.AsyncClient(transport=ASGITransport(app=app))` et couvrir:

```python
async def test_missing_key_returns_401(): ...
async def test_malformed_key_returns_401_without_store_lookup(): ...
async def test_unknown_key_returns_401(): ...
async def test_wrong_secret_returns_401(): ...
async def test_revoked_key_returns_401(): ...
async def test_expired_key_returns_401(): ...
async def test_valid_key_returns_principal(): ...
async def test_missing_scope_returns_403(): ...
async def test_required_scopes_accept_exact_match(): ...
async def test_rate_limit_returns_429_and_headers(): ...
async def test_store_failure_returns_503_without_leaking_details(): ...
```

**Step 2: Verifier l'echec**

Run: `.venv/bin/pytest keyed/tests/test_fastapi_auth.py -v`

Expected: FAIL car l'integration n'existe pas.

**Step 3: Implementer la configuration et la dependance**

Exposer:

```python
def configure_keyed(app: FastAPI, store: APIKeyStore, limiter: SlidingWindowRateLimiter) -> None: ...
async def get_api_key_auth(request: Request, x_api_key: Annotated[str | None, Header(alias="X-API-Key")] = None) -> AuthenticatedAPIKey: ...
def require_scopes(*required: str) -> Callable[..., Awaitable[AuthenticatedAPIKey]]: ...
```

`configure_keyed` place les dependances dans `app.state`. `get_api_key_auth` execute dans cet ordre: presence, parsing du prefixe, lecture store, revocation, expiration UTC, hash constant, quota. `require_scopes` reutilise `get_api_key_auth` puis applique une inclusion exacte.

**Step 4: Normaliser les reponses**

Ajouter `WWW-Authenticate: ApiKey` sur les `401`; ajouter `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset` sur les succes et les `429`, ainsi que `Retry-After` sur `429`. Ne jamais distinguer publiquement cle inconnue, secret faux, revocation ou expiration.

**Step 5: Faire passer les tests**

Run: `.venv/bin/pytest keyed/tests/test_fastapi_auth.py -v`

Expected: PASS.

**Step 6: Point de controle Git propose**

```bash
git add keyed/middleware/fastapi.py keyed/tests/fakes.py keyed/tests/test_fastapi_auth.py
git commit -m "feat: add fastapi api key authentication"
```

### Task 7: Ajouter les tests de charge et le budget de latence

**Files:**
- Create: `keyed/tests/test_performance.py`

**Step 1: Mesurer le coeur pur Python**

Tester au moins 10 000 verifications avec un enregistrement deja charge, puis rapporter mediane, p95 et p99 pour `extract_prefix + verify + rate_limit`. Ne pas rendre ce test bloquant sur une machine inconnue; echouer uniquement sur regression grossiere, par exemple p95 superieur a 25 ms.

**Step 2: Mesurer le chemin concurrent**

Lancer 1 000 appels repartis sur au moins 100 cles et verifier absence d'exception, absence de sur-admission et stabilite memoire des buckets.

**Step 3: Mesurer PostgreSQL separement**

Avec `KEYED_TEST_DATABASE_URL`, mesurer le chemin complet FastAPI + PostgreSQL sur une base locale. Rapporter le p95 observe; ne pas attribuer au code Python la latence reseau de la base.

**Step 4: Executer les benchmarks**

Run: `.venv/bin/pytest keyed/tests/test_performance.py -v -m performance`

Expected: PASS et sortie contenant les percentiles mesures.

**Step 5: Point de controle Git propose**

```bash
git add keyed/tests/test_performance.py
git commit -m "test: add core performance coverage"
```

### Task 8: Verification finale et documentation technique minimale

**Files:**
- Create: `README.md`
- Modify after explicit approval only: `PRD.md`
- Modify after explicit approval only: `index.html`
- Modify after explicit approval only: `waitlist.html`

**Step 1: Documenter uniquement l'utilisation reelle**

Le README doit contenir installation locale, migration SQL, configuration du pool, `configure_keyed`, exemple `Depends(get_api_key_auth)`, exemple `Depends(require_scopes("documents:read"))`, modele mono-worker du rate limiter, et traitement de la cle plaintext a affichage unique.

**Step 2: Executer la qualite statique**

Run: `.venv/bin/ruff check .`

Expected: PASS.

Run: `.venv/bin/ruff format --check .`

Expected: PASS.

Run: `.venv/bin/mypy keyed`

Expected: PASS.

**Step 3: Executer la suite hors integration/performance**

Run: `.venv/bin/pytest -m "not integration and not performance" -v`

Expected: PASS.

**Step 4: Executer la matrice complete**

Run: `KEYED_TEST_DATABASE_URL=postgresql://... .venv/bin/pytest -v`

Expected: PASS, avec les mesures de performance rapportees separement.

**Step 5: Faire une revue de secrets**

Run: `rg -n "(api[_-]?key|token|secret|password)\s*[:=]\s*['\"][^'\"]+" keyed pyproject.toml README.md`

Expected: aucune credential reelle; seuls des placeholders explicites sont permis.

**Step 6: Soumettre les incoherences documentaires a validation humaine**

Avant tout changement public, demander l'autorisation de remplacer les mentions bcrypt/Argon2 par la formulation exacte sur SHA-256 pour secrets aleatoires a forte entropie. Ne pas modifier `DISTRIBUTION_POSTS.md` sans accord explicite.

**Step 7: Point de controle Git propose**

```bash
git add README.md
git commit -m "docs: document python middleware usage"
```

## Criteres d'acceptation Axe 2

1. Une cle `live` ou `test` est generee avec 256 bits d'entropie et n'est jamais persistee en clair.
2. Une verification valide effectue exactement une lecture PostgreSQL indexee par prefixe.
3. Toute modification de `revoked_at` est visible des la requete suivante.
4. Expiration et scopes sont appliques avant l'acces a la route.
5. Le quota exact est respecte sous concurrence dans un processus unique.
6. Les erreurs HTTP ne revelent pas pourquoi une credential est invalide.
7. Les suites unitaires, ASGI, integration et performance passent ou toute impossibilite d'integration est explicitement rapportee.
8. Le README ne promet pas de garantie multi-worker que l'implementation en memoire ne peut pas tenir.
9. Aucun dashboard, endpoint d'administration, SDK Node, Redis, proxy, analytics ou pricing n'est ajoute.
10. Aucun commit ou push n'est effectue sans validation humaine explicite.

## Risques a surveiller pendant l'execution

1. La promesse `<3ms` depend fortement de la proximite de PostgreSQL; le benchmark doit distinguer coeur Python et I/O.
2. Le rate limiter memoire est exact par processus, pas par cluster. La beta doit tourner avec un worker ou accepter explicitement cette limite.
3. Le prefixe public aleatoire de 128 bits rend une collision negligeable; la contrainte `UNIQUE` PostgreSQL reste la defense finale.
4. Le sel protege la representation stockee, mais la securite depend surtout de l'entropie du secret et de l'absence de logs plaintext.
5. Les textes publics actuels ne sont pas encore coherents avec le choix SHA-256; cette divergence doit etre resolue avant recrutement beta technique.
