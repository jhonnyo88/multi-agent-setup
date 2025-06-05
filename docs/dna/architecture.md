# Architecture

<!--
🎯 ADAPTATION GUIDE:
This document defines DigiNativa's technical architecture. To adapt for your project:

1. Replace our tech stack (React + FastAPI + Netlify) with your chosen technologies
2. Update architectural principles to match your technical constraints
3. Modify deployment strategy for your target platform
4. Keep the 4 core principles structure - they apply to most software projects

💡 WHY ARCHITECTURE MATTERS FOR AI TEAMS:
- Agents use this to make all technical implementation decisions
- Provides constraints that guide agent behavior (API-first, stateless, etc.)
- Ensures consistency across all generated code
- Prevents agents from making incompatible technology choices

🔧 EXAMPLES FOR OTHER DOMAINS:
E-commerce: React + Node.js + Stripe + AWS
Mobile app: React Native + Firebase + App Store
SaaS: Vue + Django + PostgreSQL + Docker + Kubernetes
-->

# Arkitektoniskt Ramverk: DigiNativa

## 1. Inledning

### Syfte
Detta dokument definierar den tekniska arkitekturen och de grundläggande reglerna för utvecklingen av spelet "DigiNativa". Ramverket är utformat för att ge AI-teamet maximal hastighet och autonomi, samtidigt som det säkerställer en högkvalitativ, robust och skalbar slutprodukt.

### Vägledande Filosofi
Alla beslut och all kod som produceras av teamet **ska** följa principerna i detta dokument. Denna arkitektur är specificerar designad för att vara:
- **AI-vänlig:** Väldefinierade patterns som AI-agenter enkelt kan följa
- **Produktionsklar:** Inga shortcuts eller "demo-kod" - allt ska vara deployment-ready
- **Skalbar:** Kan växa från MVP till full-scale production utan omarbetning
- **Underhållbar:** Människor ska kunna vidareutveckla vad AI-teamet bygger

<!--
🔧 FOR YOUR PROJECT: Update the introduction to reflect your technical goals
E-commerce: Focus on conversion optimization, payment security, inventory management
Mobile app: Emphasize performance, offline capability, app store compliance
SaaS: Highlight multi-tenancy, API design, enterprise integration
-->

---

## 2. Arkitekturella Grundprinciper

Dessa fyra principer utgör systemets orubbliga kärna och **måste** följas av alla AI-agenter.

### Princip 1: Tydlig Separation av Ansvar (Separation of Concerns)

**Definition:** Systemet är uppdelat i två logiskt oberoende delar: en **Frontend** som ansvarar för presentation och användarinteraktion, och en **Backend** som ansvarar för all spellogik och datahantering.

**Varför detta är kritiskt:**
- Förhindrar att systemet blir en kaotisk monolit
- Möjliggör för AI-agenter med olika specialiseringar att arbeta effektivt
- Gör det enkelt att skala frontend och backend oberoende
- Underlättar testning och felsökning

**Implementation för AI-agenter:**
- **Utvecklare (Frontend):** Arbetar endast i `/frontend` mappen, fokuserar på React-komponenter
- **Utvecklare (Backend):** Arbetar endast i `/backend` mappen, fokuserar på API-endpoints
- **Ingen delad kod** mellan frontend och backend (utom type definitions)
- **Kommunikation endast via API-anrop** - aldrig direkta databasanrop från frontend

<!--
🔧 ADAPT: Update separation strategy for your architecture
Microservices: Define service boundaries and communication patterns
Mobile app: Separate app logic from backend services
SaaS: Define module boundaries and data isolation
-->

### Princip 2: API-först (Kontraktet är Kung)

**Definition:** All kommunikation mellan Frontend och Backend sker via ett väldefinierat RESTful API som använder JSON. Detta API är det bindande kontraktet som styr utvecklingen.

**Utvecklingsprocess:**
1. **Speldesigner** specificerar funktionalitet i specs
2. **Utvecklare** designar API-endpoints först, innan implementation
3. **Testutvecklare** skapar tester baserat på API-kontrakt
4. **Frontend och Backend** utvecklas parallellt mot samma API-spec

**API Design Standards:**
```
# Standard URL structure
GET    /api/v1/game/state          # Hämta aktuellt spelläge
POST   /api/v1/game/action         # Utför spelhandling  
GET    /api/v1/user/progress       # Hämta användarframsteg
POST   /api/v1/analytics/event     # Logga spelanalytik

# Standard response format
{
  "success": boolean,
  "data": object | array,
  "message": string,
  "timestamp": ISO8601
}

# Error response format
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "User-friendly error message",
    "details": object
  },
  "timestamp": ISO8601
}
```

**Fördelar för AI-utveckling:**
- AI-agenter kan utveckla frontend och backend parallellt
- Tydlig kontrakt förhindrar integration-problem
- Automatiska API-dokumentation via FastAPI
- Enkelt att testa och validera integration

<!--
🔧 ADAPT: Define API standards for your domain
E-commerce: Product catalog, cart management, payment processing endpoints
Mobile app: User authentication, data sync, offline handling endpoints  
SaaS: Multi-tenant data, user management, billing integration endpoints
-->

### Princip 3: Statslös Backend (Stateless Backend)

**Definition:** Vår backend "minns" ingenting mellan anropen. All nödvändig information för att bearbeta en begäran (t.ex. vilket val spelaren gjort) måste skickas med i anropet från klienten.

**Praktisk Implementation:**
```python
# ❌ Fel: Sparar tillstånd i backend
class GameSession:
    def __init__(self):
        self.current_level = 1
        self.player_choices = []
    
    def make_choice(self, choice):
        self.player_choices.append(choice)  # State i backend!

# ✅ Rätt: Statslös backend
@app.post("/api/v1/game/make-choice")
async def make_choice(request: ChoiceRequest):
    # All state skickas från frontend
    game_state = request.current_game_state
    new_choice = request.choice
    
    # Beräkna nytt tillstånd baserat på input
    updated_state = calculate_new_state(game_state, new_choice)
    
    # Returnera nytt tillstånd till frontend
    return {"updated_state": updated_state}
```

**Kritiska fördelar:**
- Enkelt att testa - samma input ger alltid samma output
- Inga race conditions eller concurrency-problem
- Enkelt att skala horisontellt
- Inga komplex session management
- Perfekt för serverless deployment (Netlify Functions)

**Storage Strategy:**
```
MVP (Simplicity):           Production (Scale):
- Game state i localStorage - Game state i PostgreSQL  
- User progress i JSON-filer - User progress i databas
- No server-side sessions   - JWT tokens för auth
- No complex state sync     - Real-time sync via WebSockets
```

<!--
🔧 ADAPT: Define statelessness for your domain
E-commerce: Shopping cart in client, order processing stateless
Mobile app: App state local, server only for data persistence
SaaS: Session data in JWT, business logic stateless
-->

### Princip 4: Enkelhet och Pragmatism (Keep It Simple, Stupid)

**Definition:** Teamet ska **alltid** välja den enklaste lösningen som uppfyller kraven för den aktuella milstolpen. Vi bygger inte för framtida, hypotetiska problem.

**Decision Framework:**
```
När AI-agenter väljer teknisk lösning:

1. Gör den enklaste lösningen som fungerar först
2. Mät om den uppfyller performance-krav  
3. Optimera endast om mätningar visar problem
4. Dokumentera WHY en komplex lösning valdes

Exempel:
❌ Implementera Redis caching från start "för att det ska skala"
✅ Använd in-memory caching, mät performance, uppgradera vid behov

❌ Mikrotjänstarkitektur från dag 1 "för framtida skalning"  
✅ Modulär monolit, dela upp när faktiska bottlenecks identifieras
```

**Complexity Indicators (när AI-agenter ska flagga för granskning):**
- Mer än 3 externa dependencies för en feature
- Konfigurerbarhet som inte används av aktuella krav
- Abstraktionslager utan konkret use case
- Performance-optimiseringar utan mätningar som motiverar dem

---

## 3. Systemöversikt & Teknisk Stack

### Repository Structure
```
diginativa-game/                    # 🔧 CHANGE: Your project repo name
├── frontend/                       # React application
│   ├── src/
│   │   ├── components/            # Reusable UI components
│   │   ├── pages/                 # Game screens/views
│   │   ├── hooks/                 # Custom React hooks
│   │   ├── services/              # API communication
│   │   ├── types/                 # TypeScript definitions
│   │   └── utils/                 # Helper functions
│   ├── public/                    # Static assets
│   ├── package.json               # Frontend dependencies
│   └── tailwind.config.js         # Styling configuration
│
├── backend/                       # FastAPI application  
│   ├── app/
│   │   ├── api/                   # API route definitions
│   │   ├── core/                  # Configuration and settings
│   │   ├── models/                # Data models (Pydantic)
│   │   ├── services/              # Business logic
│   │   └── utils/                 # Helper functions
│   ├── tests/                     # Backend tests
│   ├── requirements.txt           # Python dependencies
│   └── main.py                    # Application entry point
│
├── shared/                        # Type definitions shared between frontend/backend
├── docs/                          # Project documentation
├── scripts/                       # Build and deployment scripts
└── netlify.toml                   # Deployment configuration
```

<!--
🔧 ADAPT: Update repository structure for your tech stack
Node.js: Replace FastAPI structure with Express/Nest.js structure
Mobile: Replace with React Native or Flutter structure  
Microservices: Define service boundaries and communication
-->

### Technology Choices & Rationale

#### Frontend: React + TypeScript + Tailwind CSS

**Valda teknologier:**
- **React 18+:** Component-based architecture, excellent AI-agent documentation
- **TypeScript:** Type safety reduces AI-generated bugs, better IDE support
- **Tailwind CSS:** Utility-first CSS, prevents styling conflicts, fast development
- **Vite:** Fast build tool, excellent development experience

**Varför dessa val för AI-utveckling:**
```
React: 
✅ Välkänd av AI-modeller (enormous training data)
✅ Komponentbaserad = naturlig för AI att strukturera kod
✅ Enkel testning av isolerade komponenter
✅ Stor community för troubleshooting

TypeScript:
✅ Hjälper AI-agenter undvika typfel  
✅ Bättre IntelliSense för development
✅ Shared types mellan frontend/backend
✅ Compile-time error catching

Tailwind:
✅ Utility classes = konsekvent styling av AI-agenter
✅ Inga global CSS-konflikter
✅ Responsiv design blir automatisk
✅ Snabb prototyping av new features
```

**Performance Targets:**
- First Contentful Paint: <1.5 sekunder
- Largest Contentful Paint: <2.5 sekunder  
- Cumulative Layout Shift: <0.1
- Bundle size: <500KB gzipped

<!--
🔧 ADAPT: Choose frontend tech for your needs
Vue/Nuxt: For progressive enhancement projects
Angular: For enterprise applications with complex state
Svelte: For performance-critical applications
React Native: For mobile applications
-->

#### Backend: FastAPI + Python + SQLite→PostgreSQL

**Valda teknologier:**
- **FastAPI:** Auto-generated API docs, excellent type hints, async support
- **Python 3.9+:** AI-friendly language, excellent for rapid development
- **SQLite (MVP) → PostgreSQL (Production):** Simple start, professional scale
- **Pydantic:** Data validation and serialization with type hints

**Varför dessa val för AI-utveckling:**
```
FastAPI:
✅ Automatisk API-dokumentation (OpenAPI/Swagger)
✅ Type hints = mindre AI-fel i API-kontrakt
✅ Async support för high-performance endpoints
✅ Excellent development experience

Python:
✅ AI-modellers starkaste språk (mest training data)
✅ Enkel syntax = mindre AI-genererade syntaxfel
✅ Stort ecosystem för gaming/education libraries
✅ Excellent för rapid prototyping

SQLite → PostgreSQL:
✅ Ingen infrastruktur-komplexitet för MVP
✅ Same SQL syntax = smooth migration path
✅ Local development utan externa dependencies
✅ Production-ready scaling när det behövs
```

**API Architecture Pattern:**
```python
# Standardiserad FastAPI endpoint structure
@app.post("/api/v1/game/make-choice", response_model=GameStateResponse)
async def make_choice(
    request: ChoiceRequest,
    current_user: User = Depends(get_current_user)  # Optional auth
) -> GameStateResponse:
    """
    Process a player choice and return updated game state.
    
    🔧 ADAPT: Replace game logic with your domain logic
    E-commerce: process_cart_action, update_inventory
    Mobile app: sync_user_data, update_preferences  
    SaaS: execute_workflow_step, update_project_state
    """
    try:
        # Validate input (Pydantic handles this automatically)
        validated_choice = request.choice
        current_state = request.game_state
        
        # Execute business logic (stateless!)
        new_state = await game_service.process_choice(
            current_state=current_state,
            choice=validated_choice,
            user_context=current_user
        )
        
        # Return structured response
        return GameStateResponse(
            success=True,
            game_state=new_state,
            message="Choice processed successfully"
        )
        
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except GameLogicError as e:
        raise HTTPException(status_code=422, detail=str(e))
```

<!--
🔧 ADAPT: Choose backend tech for your domain
Node.js/Express: For JavaScript-heavy teams
Django: For content-heavy applications
Go/Gin: For high-performance APIs
.NET Core: For enterprise environments
-->

#### Deployment: Netlify (Serverless-first)

**Valda teknologier:**
- **Netlify:** Static site hosting + serverless functions
- **Netlify Functions:** FastAPI deployed as serverless functions
- **Branch Previews:** Automatic deployment för feature branches
- **Edge CDN:** Global distribution för optimal performance

**Deployment Architecture:**
```
Production Flow:
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   GitHub Repo   │───▶│  Netlify Build  │───▶│  Global CDN     │
│  (main branch)  │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │ Serverless API  │
                       │ (FastAPI)       │
                       └─────────────────┘

Feature Development:
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Feature Branch  │───▶│ Preview Deploy  │───▶│ Unique URL      │
│ (PR created)    │    │ (Automatic)     │    │ for testing     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

**Varför Netlify för AI-utveckling:**
```
Serverless Benefits:
✅ Ingen server-administration = AI-agenter fokuserar på kod
✅ Automatisk skalning baserat på användning
✅ Inbyggd CI/CD = automatic deployment vid code-push
✅ Branch previews = varje PR får egen test-miljö

Cost Efficiency:
✅ Pay-per-use pricing = ingen kostnad för idle time
✅ Gratis tier för development och small-scale testing
✅ Skalning endast när traffic ökar

Developer Experience:
✅ Automatic HTTPS för alla deployments
✅ Environment variables management
✅ Build logs och deployment status
✅ Rollback till tidigare versions
```

**netlify.toml Configuration:**
```toml
# 🔧 ADAPT: Update build commands for your tech stack
[build]
  publish = "frontend/dist"              # React build output
  command = "npm run build"              # Build command
  functions = "backend/netlify/functions" # Serverless functions

[build.environment]
  NODE_VERSION = "18"
  PYTHON_VERSION = "3.9"

# Redirect API calls to serverless functions
[[redirects]]
  from = "/api/*"
  to = "/.netlify/functions/:splat"
  status = 200

# SPA routing support
[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200

# Performance optimization
[build.processing.html]
  pretty_urls = true

[build.processing.css]
  bundle = true
  minify = true

[build.processing.js]
  bundle = true
  minify = true
```

<!--
🔧 ADAPT: Choose deployment for your needs
Vercel: Alternative serverless platform with excellent Next.js integration
AWS: For enterprise applications needing complex infrastructure  
Docker + Kubernetes: For microservices or complex deployment requirements
Traditional hosting: For applications requiring persistent connections
-->

### Database Strategy: Progressive Complexity

#### MVP Phase: SQLite + JSON Files
```python
# Simple file-based storage for MVP
DATABASE_URL = "sqlite:///./diginativa.db"

# Game state storage
GAME_STATE_STORAGE = {
    "type": "local_json",
    "path": "./data/game_states/",
    "backup_interval": "daily"
}

# User progress tracking  
USER_PROGRESS_STORAGE = {
    "type": "sqlite_table",
    "table": "user_progress",
    "indexes": ["user_id", "last_played"]
}
```

#### Production Phase: PostgreSQL + Redis
```python
# Scalable production storage
DATABASE_URL = os.getenv("DATABASE_URL")  # PostgreSQL

# Caching layer
REDIS_URL = os.getenv("REDIS_URL")  # Redis for caching

# Game state storage
GAME_STATE_STORAGE = {
    "type": "postgresql_jsonb",
    "table": "game_states", 
    "ttl": 86400  # 24 hours
}

# Real-time features
WEBSOCKET_BACKEND = {
    "type": "redis_pubsub",
    "channels": ["game_events", "user_progress"]
}
```

**Migration Path:**
1. **MVP:** SQLite + JSON files (no infrastructure complexity)
2. **Growth:** Add PostgreSQL for user data, keep SQLite for development  
3. **Scale:** Full PostgreSQL + Redis caching + CDN
4. **Enterprise:** Add read replicas, connection pooling, monitoring

---

## 4. Arbetsflöde & Kvalitetssäkring

### AI-Agent Development Flow

```
1. Planning (Projektledare):
   ├── Projektledare bryter ner Feature till Stories
   ├── En Story för backend-logiken  
   ├── En Story för frontend-gränssnittet
   └── Båda refererar till samma API-kontrakt

2. Parallel Development:
   ├── Utvecklare (Backend) skriver FastAPI endpoints
   ├── Utvecklare (Frontend) skriver React komponenter  
   ├── Testutvecklare skriver API + UI tester
   └── Alla arbetar mot samma API-specifikation

3. Automatic Quality Gates:
   ├── All kod checkas in automatiskt
   ├── Testsviten körs (måste vara 100% grön)
   ├── ESLint + Prettier för kodstandard
   ├── Lighthouse för performance (>90 score)
   └── Type checking (TypeScript + Pydantic)

4. Manual QA Review:
   ├── QA-Testare testar från Anna-perspektiv
   ├── Verifierar alla 5 designprinciper
   ├── Kontrollerar <10 minuters speltid
   └── Funktionell granskning mot specifikation

5. Deployment:
   ├── Godkänt av QA → Automatic merge till main
   ├── Netlify bygger och deployar automatiskt
   ├── Branch cleanup och notifikationer
   └── Success metrics tracking börjar
```

### Quality Assurance Integration

**Automated Quality Gates:**
```yaml
# .github/workflows/quality-gates.yml
name: Quality Gates
on: [push, pull_request]

jobs:
  frontend_quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run TypeScript checks
        run: cd frontend && npm run type-check
      - name: Run ESLint
        run: cd frontend && npm run lint
      - name: Run tests  
        run: cd frontend && npm run test
      - name: Build production
        run: cd frontend && npm run build
      - name: Lighthouse CI
        run: npm run lighthouse-ci

  backend_quality:
    runs-on: ubuntu-latest  
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: cd backend && pip install -r requirements.txt
      - name: Run type checks
        run: cd backend && mypy .
      - name: Run tests
        run: cd backend && pytest
      - name: Test API documentation
        run: cd backend && python -c "from app.main import app; print('API docs generated')"
```

**Manual QA Checklist:**
- [ ] Alla acceptanskriterier från Story är uppfyllda
- [ ] Design Principle 1: Pedagogisk effekt verifierad  
- [ ] Design Principle 2: Realism och praktisk tillämpbarhet
- [ ] Design Principle 3: <10 minuters genomförande-tid
- [ ] Design Principle 4: Systemtänk genom interaktion demonstrerat
- [ ] Design Principle 5: Professionell ton utan infantilisering
- [ ] API-kontrakt följt exakt (inga avvikelser)
- [ ] Statslös backend bekräftad (ingen server-side state)
- [ ] Responsive design fungerar på mobile + desktop
- [ ] Lighthouse score >90 för performance + accessibility

---

## 5. Säkerhet & Best Practices

### Security Implementation

**Frontend Security:**
```typescript
// Content Security Policy
const CSP_HEADER = {
  "Content-Security-Policy": 
    "default-src 'self'; " +
    "script-src 'self' 'unsafe-inline'; " +
    "style-src 'self' 'unsafe-inline'; " +
    "img-src 'self' data: https:; " +
    "connect-src 'self' https://api.diginativa.se"
};

// Environment variable handling
const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';
// Never expose secret keys in frontend!
```

**Backend Security:**
```python
# CORS configuration
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://diginativa.netlify.app"],  # 🔧 UPDATE: Your domain
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Input validation
from pydantic import BaseModel, validator

class GameChoiceRequest(BaseModel):
    choice_id: str
    game_state: dict
    
    @validator('choice_id')
    def validate_choice_id(cls, v):
        if not v or len(v) > 50:
            raise ValueError('Invalid choice_id format')
        return v
```

**Environment Variables Security:**
```bash
# .env (NEVER commit this file!)
OPENAI_API_KEY=sk-proj-...                    # AI model access
GITHUB_TOKEN=ghp_...                          # GitHub automation  
DATABASE_URL=postgresql://user:pass@host/db   # Production database
NETLIFY_TOKEN=nfp_...                         # Deployment automation

# Production secrets (Netlify environment variables)
ANALYTICS_SECRET=...                          # Usage tracking
WEBHOOK_SECRET=...                            # GitHub webhook validation
```

### Performance Optimization

**Frontend Performance:**
```javascript
// Code splitting for optimal loading
const GameComponent = lazy(() => import('./components/Game'));
const ResultsComponent = lazy(() => import('./components/Results'));

// Image optimization
import gameImage from './assets/game-bg.webp';
// Use WebP format for 25-35% smaller file sizes

// Service worker for caching
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/sw.js');
}
```

**Backend Performance:**
```python
# Database connection pooling
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

engine = create_engine(
    DATABASE_URL,
    poolclass=StaticPool,
    pool_size=10,
    max_overflow=20
)

# Response caching for expensive operations
from functools import lru_cache

@lru_cache(maxsize=128)
async def get_game_configuration(config_version: str):
    # Expensive computation cached in memory
    return complex_game_config_calculation(config_version)
```

---

## 6. Monitoring & Analytics

### Health Monitoring

**Application Health Checks:**
```python
# Backend health endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "1.0.0",
        "database": await check_database_connection(),
        "external_apis": await check_external_apis()
    }
```

**Frontend Performance Monitoring:**
```javascript
// Core Web Vitals tracking
import {getCLS, getFID, getFCP, getLCP, getTTFB} from 'web-vitals';

function sendToAnalytics(metric) {
  // Send to your analytics service
  console.log(metric);
}

getCLS(sendToAnalytics);
getFID(sendToAnalytics);
getFCP(sendToAnalytics);
getLCP(sendToAnalytics);
getTTFB(sendToAnalytics);
```

### Business Analytics

**Learning Analytics:**
```python
# Track pedagogical effectiveness
@app.post("/api/v1/analytics/learning-event")
async def track_learning_event(event: LearningEvent):
    """
    Track learning effectiveness for Design Principle 1: Pedagogik Framför Allt
    
    🔧 ADAPT: Replace learning metrics with your domain metrics
    E-commerce: Conversion events, cart abandonment, product views
    Mobile app: Feature usage, session length, user retention
    SaaS: Feature adoption, workflow completion, user onboarding
    """
    await analytics_service.track_event({
        "event_type": "learning_milestone",
        "user_id": event.user_id,
        "concept_learned": event.concept,
        "time_to_understanding": event.duration_seconds,
        "confidence_score": event.confidence_level,
        "practical_application": event.will_apply_at_work
    })
```

### Success Metrics Tracking

**Automated Metrics Collection:**
```python
# Metrics aligned with vision_and_mission.md success criteria
TRACKED_METRICS = {
    "user_engagement": {
        "completion_rate": "% users who complete full game session",
        "target": 0.80,
        "measurement": "session_completed / session_started"
    },
    "learning_outcomes": {
        "knowledge_improvement": "% showing improved understanding",
        "target": 0.75,
        "measurement": "post_test_score > pre_test_score"
    },
    "system_adoption": {
        "organizational_usage": "Number of organizations actively using",
        "target": 50,
        "measurement": "COUNT(DISTINCT organization_id WHERE last_active > 30_days)"
    },
    "technical_excellence": {
        "uptime_percentage": "System availability",
        "target": 0.95,
        "measurement": "uptime_minutes / total_minutes"
    }
}
```

---

## 7. Migration & Scaling Strategy

### MVP to Production Evolution

**Phase 1: MVP (Month 1-3)**
```
Frontend: React + Tailwind + Vite
Backend: FastAPI + SQLite
Deployment: Netlify
Users: <100 concurrent
Features: Core game mechanics
```

**Phase 2: Growth (Month 4-8)**
```
Frontend: Same + PWA capabilities
Backend: FastAPI + PostgreSQL
Deployment: Netlify + CDN
Users: <1000 concurrent  
Features: User accounts, progress tracking
```

**Phase 3: Scale (Month 9+)**
```
Frontend: Same + Advanced caching
Backend: FastAPI + PostgreSQL + Redis
Deployment: Multi-region CDN
Users: 10,000+ concurrent
Features: Real-time collaboration, analytics
```

### Technology Migration Paths

**Database Migration:**
```python
# Automated migration script
def migrate_sqlite_to_postgresql():
    """
    Migrate from SQLite (MVP) to PostgreSQL (Production)
    while maintaining zero downtime for users.
    """
    # 1. Export all SQLite data
    sqlite_data = export_sqlite_data()
    
    # 2. Create PostgreSQL schema
    create_postgresql_schema()
    
    # 3. Import data with transformation
    import_to_postgresql(sqlite_data)
    
    # 4. Validate data integrity
    validate_migration()
    
    # 5. Switch connection string
    update_database_url()
```

---

## Slutgiltigt Direktiv till AI-teamet

Ni är ett högpresterande system som bygger verklig, produktionsklar kod. Er framgång beror på er förmåga att disciplinerat följa detta arkitektoniska ramverk.

### Non-Negotiable Requirements

1. **API-First Always:** Inga direkta databas-anrop från frontend
2. **Stateless Backend:** Inget server-side state mellan requests  
3. **Separation of Concerns:** Frontend och backend förblir separata
4. **Simplicity First:** Välj enklaste lösningen som fungerar

### Success Criteria

- All kod ska vara deployment-ready från dag 1
- Inga "TODO" eller "FIXME" kommentarer i production code
- 100% test coverage för all business logic
- Lighthouse score >90 för all frontend code
- API response times <200ms för all endpoints

### Quality Assurance

Fokusera på att leverera små, testade och värdefulla inkrement enligt färdplanen. Lita på processen, respektera API-kontraktet och bygg aldrig mer än vad som krävs för nästa steg.

Gör ni detta, kommer vi inte bara att bygga "DigiNativa" – vi kommer att bygga det på rätt sätt.

---

*Detta arkitektoniska ramverk är levande och uppdateras baserat på faktiska utvecklingserfarenheter och tekniska upptäckter under projektets gång.*