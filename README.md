# multi-agent-setup
This is my attempt to set up a development team of AI agents.

# DigiNativa AI-Team

*A complete multi-agent AI team for developing interactive learning games - and a reference implementation for building AI development teams in any domain.*

[![License: CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc-sa/4.0/)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![AI Framework](https://img.shields.io/badge/AI-CrewAI-green.svg)](https://github.com/joaomdmoura/crewAI)

## 🎯 What This Is

This repository contains a **fully functional AI team** that develops the DigiNativa learning game - an interactive experience teaching digitalization strategy to Swedish public sector employees.

**More importantly:** This serves as a **complete, working example** of how to build multi-agent AI teams for software development. You can adapt this approach for your own projects.

### Why This Matters

- **🤖 Real AI Team:** 6 specialized agents that actually develop software
- **📚 Complete Reference:** Everything from setup to deployment documented
- **🔧 Highly Adaptable:** Clear guides for adapting to e-commerce, mobile apps, SaaS, etc.
- **🚀 Production Ready:** No demo code - everything is deployment-ready
- **🌍 Open Source:** Learn from our approach, contribute improvements

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.9+** (AI framework requirement)
- **GitHub CLI** installed (`gh --version` should work)
- **Git** configured with your GitHub account
- **API Keys:** OpenAI API key for AI agents

### 5-Minute Setup
```bash
# 1. Clone the repository
git clone https://github.com/jhonnyo88/multi-agent-setup.git
cd multi-agent-setup

# 2. Run the setup wizard
python scripts/setup.py
# This will:
# - Create virtual environment
# - Install dependencies  
# - Configure environment variables
# - Test API connections
# - Initialize database

# 3. Deploy your AI team
python scripts/deploy_agents.py

# 4. Check everything is working
python scripts/health_check.py
```

### First Feature Request
```bash
# Create your first feature via GitHub Issues
gh issue create --title "Add user authentication" --body "Enable users to create accounts and login"

# Or use the web interface:
# Go to: https://github.com/jhonnyo88/multi-agent-setup/issues/new
# Select: "Feature Request" template
# Fill in the DigiNativa-specific details
```

---

## 🤖 Meet the AI Team

### Our 6 Specialized Agents

#### 🎯 **Projektledare (Project Manager)**
- **Role:** Orchestrates the entire team and manages GitHub Issues
- **Specialization:** Workflow management, exception handling, stakeholder communication  
- **Key Skills:** CrewAI orchestration, GitHub API integration, deadline management

#### 🎨 **Speldesigner (Game Designer)**  
- **Role:** Creates pedagogical game mechanics and user experience
- **Specialization:** Learning design, serious games, UX for professional users
- **Key Skills:** Educational psychology, game mechanics, user research

#### 💻 **Utvecklare (Full-Stack Developer)**
- **Role:** Implements React frontend + FastAPI backend
- **Specialization:** Modern web development, API-first architecture
- **Key Skills:** React, Python, RESTful APIs, serverless deployment

#### 🧪 **Testutvecklare (Test Automation Engineer)**
- **Role:** Creates automated tests for all functionality
- **Specialization:** Test automation, quality assurance, CI/CD
- **Key Skills:** Pytest, Selenium, API testing, test strategy

#### 🔍 **QA-Testare (Manual QA Tester)**  
- **Role:** Tests from end-user perspective ("Anna" - our target user)
- **Specialization:** User acceptance testing, usability validation
- **Key Skills:** Manual testing, user empathy, bug reporting

#### ⚡ **Kvalitetsgranskare (Quality Reviewer)**
- **Role:** Automated code quality and performance validation  
- **Specialization:** Code analysis, performance optimization, architecture compliance
- **Key Skills:** Static analysis, Lighthouse testing, architecture validation

### How They Work Together

```
Feature Request (GitHub Issue)
           ↓
    Projektledare analyzes
           ↓
    Speldesigner creates specification
           ↓
    ┌─ Utvecklare codes ─┐    ┌─ Testutvecklare writes tests ─┐
    │                   │    │                              │
    └───────────────────┼────┴──────────────────────────────┘
                        ↓
                QA-Testare validates
                        ↓
            Kvalitetsgranskare reviews
                        ↓
                Human approval & deploy
```

---

## 🛠️ Technology Stack

### Current Implementation (DigiNativa)
- **Frontend:** React 18 + TypeScript + Tailwind CSS + Vite
- **Backend:** FastAPI (Python) + SQLite → PostgreSQL  
- **Deployment:** Netlify (static site + serverless functions)
- **AI Framework:** CrewAI with OpenAI GPT-4
- **Communication:** GitHub Issues API for all coordination
- **Testing:** Pytest + Selenium + Lighthouse

### Why These Choices?

**🤖 AI-Friendly Technologies:**
- **Well-documented:** Extensive training data for AI models
- **Predictable patterns:** AI agents can follow established conventions
- **Strong typing:** TypeScript + Pydantic reduce AI-generated bugs
- **Rapid iteration:** Fast feedback loops for AI development

**🚀 Production-Ready Architecture:**
- **Serverless-first:** No server management complexity
- **API-first:** Clean separation enabling parallel AI development
- **Stateless backend:** Eliminates complex session management
- **Progressive enhancement:** Start simple, scale when needed

**💡 Human-Maintainable:**
- **Standard technologies:** Humans can easily take over and extend
- **Clear separation:** Frontend/backend boundaries are obvious
- **Excellent tooling:** Great debugging and development experience

---

## 🔧 Adapting for Your Project

This implementation is specifically built for DigiNativa (a learning game for Swedish public sector), but **the structure is designed to be highly adaptable**.

### 30-Minute Adaptation

Perfect for testing the approach with your own project:

```python
# In config/settings.py - change these core settings:

PROJECT_DOMAIN = "e_commerce"  # Instead of "game_development"
TARGET_AUDIENCE = {
    "primary_persona": "Online Shopper",  # Instead of "Anna"
    "description": "Busy consumer seeking convenience",
    "time_constraints": "< 2 minutes checkout"
}

TECH_STACK = {
    "frontend": {"framework": "React"},  # Keep or change
    "backend": {"framework": "Node.js"},  # Change from FastAPI
    "deployment": {"platform": "Vercel"}  # Change from Netlify
}
```

### 2-Hour Deep Customization

For serious adaptation to your domain:

1. **📝 Rewrite DNA documents:** Adapt `docs/dna/` files for your domain
   - `vision_and_mission.md`: Your project goals instead of digitalization education
   - `target_audience.md`: Your users instead of "Anna" the public sector employee
   - `design_principles.md`: Your 5 principles instead of pedagogical ones

2. **🤖 Customize agents:** Modify agent prompts in `agents/` for your expertise
   - Replace game design skills with your domain expertise
   - Update development focus from learning games to your product type
   - Adjust QA testing for your user scenarios

3. **🛠️ Update tech stack:** Change `architecture.md` for your technologies
   - Swap FastAPI for your preferred backend framework
   - Update deployment strategy for your target platform  
   - Modify database strategy for your data requirements

### Domain-Specific Examples

**E-commerce Platform:**
```python
PROJECT_DOMAIN = "e_commerce"
DESIGN_PRINCIPLES = [
    "Conversion First",      # Every element optimizes for sales
    "Trust Building",        # Design builds customer confidence  
    "Mobile Native",         # Mobile-first responsive design
    "Speed & Performance",   # Fast loading, quick interactions
    "Personalization"        # Tailored user experiences
]
```

**Mobile App Development:**
```python
PROJECT_DOMAIN = "mobile_development"  
TECH_STACK = {
    "frontend": {"framework": "React Native"},
    "backend": {"framework": "Node.js + Express"},
    "deployment": {"platform": "App Store + Google Play"}
}
```

**SaaS Platform:**
```python
PROJECT_DOMAIN = "saas_development"
TARGET_AUDIENCE = {
    "primary_persona": "Business Manager",
    "description": "Decision maker seeking efficiency tools",
    "technical_level": "intermediate"
}
```

---

## 📊 Success Metrics

### AI Team Performance

**Development Velocity:**
- **Story Cycle Time:** 2-4 days from GitHub issue to deployed feature
- **Quality Gate Pass Rate:** >90% of stories pass all automated checks first time
- **Human Intervention Rate:** <10% of stories require human debugging or guidance

**Quality Metrics:**
- **Code Quality:** 100% test coverage, 0 linting warnings
- **Performance:** Lighthouse scores >90 for all frontend features
- **Architecture Compliance:** All code follows API-first, stateless principles

**Stakeholder Satisfaction:**
- **Feature Approval Rate:** >85% of delivered features approved without revision
- **Business Value:** Features directly address user needs and business goals
- **Maintainability:** Human developers can easily understand and extend AI-generated code

### Domain-Specific Metrics (DigiNativa Game)

**User Engagement:**
- **Completion Rate:** 80% of users complete at least one full game session
- **Session Duration:** Average 8 minutes (target: <10 minutes)
- **Return Rate:** 60% of users return within one week

**Learning Effectiveness:**  
- **Knowledge Improvement:** 75% show improved understanding in post-tests
- **Real-World Application:** 70% report using learned concepts in their actual work
- **Confidence Building:** 80% feel more confident about digitalization strategy

**Organizational Adoption:**
- **Active Organizations:** 50+ Swedish municipalities using the game
- **Training Integration:** 30+ organizations integrate into formal training programs
- **Peer Recommendations:** 85% recommend to colleagues in similar roles

---

## 📚 Documentation Structure

### For Users Getting Started
- **`README.md`** (this file): Project overview and quick start
- **`SETUP_GUIDE.md`**: Detailed setup instructions
- **`ADAPTATION_GUIDE.md`**: How to customize for your domain

### Project DNA (Core Decision Drivers)
- **`docs/dna/vision_and_mission.md`**: Project purpose and success metrics
- **`docs/dna/target_audience.md`**: User personas and needs analysis
- **`docs/dna/design_principles.md`**: The 5 principles guiding all decisions
- **`docs/dna/architecture.md`**: Technical architecture and constraints
- **`docs/dna/definition_of_done.md`**: Quality criteria for completed work

### Technical Implementation  
- **`docs/workflows/`**: How the AI team operates internally
- **`docs/implementation/`**: Technical guides for extending the system
- **`docs/examples/`**: Real examples from DigiNativa development

### AI Team Configuration
- **`agents/`**: Individual agent implementations and prompts
- **`tools/`**: Reusable tools that agents use for their work
- **`workflows/`**: Coordination logic between agents

---

## 🤝 Contributing & Community

This project serves dual purposes:
1. **Active DigiNativa development** (our primary business goal)
2. **Reference implementation** for the AI development community

### Ways to Contribute

**🐛 Bug Reports**
Found issues with our AI team implementation? Please report them! This helps both DigiNativa and future AI team builders.

**💡 Enhancement Ideas**  
Suggestions for improving AI team workflows, agent coordination, or development processes.

**📖 Documentation Improvements**
Help us explain concepts more clearly, add examples, or translate adaptation guides.

**🔄 Domain Adaptations**
Share how you adapted this framework for your domain. We'll feature successful adaptations to help others.

**🧪 Experimental Features**
Try new AI models, frameworks, or coordination patterns and share your results.

### Community Resources

TBD

---

## 🔒 Security & Best Practices

### API Keys & Secrets Management
```bash
# ✅ Correct: Use environment variables
OPENAI_API_KEY=sk-proj-your-key-here

# ❌ Never do this: Hardcode keys in code
api_key = "sk-proj-your-key-here"  # Don't do this!
```

### Production Deployment Checklist
- [ ] All API keys configured in production environment
- [ ] GitHub webhooks configured for automatic deployment
- [ ] Monitoring and alerting set up for agent failures
- [ ] Database backups automated and tested
- [ ] SSL certificates and HTTPS enforced
- [ ] Rate limiting configured for API endpoints
- [ ] Error logging and crash reporting enabled
- [ ] Performance monitoring (Core Web Vitals) active

### Privacy & Compliance
- **Data Minimization:** Only collect data necessary for functionality
- **User Consent:** Clear privacy policy for any data collection
- **EU GDPR Compliance:** For European users (like our Swedish target audience)
- **Secure API Design:** Input validation, rate limiting, CORS configuration

---

## 🔧 Development Workflow

### For Humans Working with the AI Team

**1. Creating New Features:**
```bash
# Use GitHub Issues with our templates
gh issue create --template feature-request.yml --title "Add user dashboard"

# Or via web interface with structured templates
# The AI Projektledare will automatically pick up and analyze the issue
```

**2. Monitoring AI Team Progress:**
```bash
# Check current team status
python scripts/health_check.py

# View detailed logs
tail -f state/logs/projektledare.log

# Check story progress
python scripts/story_status.py --story-id STORY-123
```

**3. Reviewing AI-Generated Code:**
```bash
# AI team creates pull requests automatically
# Human reviews focus on:
# - Business logic correctness
# - Integration with existing systems
# - Performance implications
# - Security considerations

# Approve and merge
gh pr review --approve
gh pr merge --squash
```

### AI Team Internal Workflow

**Automated Coordination:**
```
GitHub Issue Created
         ↓
Projektledare receives webhook
         ↓
Analyzes requirements using DNA documents
         ↓
Creates child issues for implementation
         ↓
Assigns to relevant specialists
         ↓
Monitors progress and handles exceptions
         ↓
Coordinates final review and deployment
```

**Exception Handling:**
- **Deadlock Detection:** If QA fails 3 times, escalate to human
- **Tool Failures:** Automatic retry with alternative approaches
- **Specification Ambiguity:** Request clarification from stakeholders
- **Performance Issues:** Automatic optimization suggestions

---

## 📈 Monitoring & Analytics

### System Health Dashboard

**Real-time Metrics:**
- **Agent Status:** Online/offline status for each AI agent
- **Queue Length:** Number of pending tasks per agent
- **Success Rates:** Completion rates for different task types
- **Response Times:** Average time from task assignment to completion

**Quality Metrics:**
- **Code Quality Trends:** Test coverage, linting scores over time
- **Bug Detection Rate:** Issues caught by automated vs manual testing
- **Architecture Compliance:** Adherence to API-first and stateless principles
- **Performance Trends:** Lighthouse scores and load times over time

### Business Intelligence

**Feature Development Analytics:**
```python
# Track development velocity
VELOCITY_METRICS = {
    "stories_per_sprint": "Average stories completed per 2-week period",
    "cycle_time_trend": "Story completion time trending up/down",
    "quality_gate_efficiency": "% stories passing automated checks first try",
    "human_intervention_rate": "% stories requiring human debugging"
}

# User impact analysis  
USER_IMPACT_METRICS = {
    "feature_adoption_rate": "% users trying new features within 30 days",
    "user_satisfaction_score": "NPS score for AI-developed features",
    "business_value_delivered": "Features directly addressing user pain points"
}
```

### Learning & Improvement

**AI Team Evolution:**
- **Prompt Optimization:** Track which agent prompts lead to better results
- **Tool Effectiveness:** Measure which tools agents use most successfully
- **Workflow Refinement:** Identify and eliminate bottlenecks in coordination
- **Domain Knowledge Growth:** Monitor agent improvement in domain-specific tasks

---

## 🚨 Troubleshooting Common Issues

### Setup Problems

**"Python version not supported"**
```bash
# Update Python to 3.9+
# On macOS:
brew install python@3.9

# On Ubuntu:
sudo apt update && sudo apt install python3.9

# On Windows:
# Download from python.org
```

**"OpenAI API key invalid"**
```bash
# Verify your key format
echo $OPENAI_API_KEY  # Should start with 'sk-proj-' or 'sk-'

# Test the key manually
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
     https://api.openai.com/v1/models
```

**"GitHub CLI not authenticated"**
```bash
# Login to GitHub CLI
gh auth login
# Select GitHub.com, HTTPS, and follow prompts
```

### Runtime Issues

**"Agent not responding"**
```bash
# Check agent status
python scripts/health_check.py --agent projektledare

# Restart specific agent
python scripts/restart_agent.py --agent projektledare

# Check logs for errors
tail -f state/logs/projektledare.log
```

**"Quality gates failing"**
```bash
# Run quality checks manually
cd frontend && npm run lint
cd backend && pytest

# Check Lighthouse performance
npm run lighthouse-ci

# Verify API contracts
cd backend && python -m pytest tests/test_api_contracts.py
```

**"Deployment failures"**
```bash
# Check Netlify build logs
netlify logs

# Verify environment variables
netlify env:list

# Test local build
npm run build
```

### Performance Issues

**"Slow agent responses"**
- Check OpenAI API rate limits and quotas
- Monitor memory usage: `python scripts/monitor_resources.py`
- Consider upgrading to GPT-4 Turbo for faster responses

**"High resource usage"**
- Enable agent task queuing: `ENABLE_TASK_QUEUE=true`
- Reduce concurrent agent operations: `MAX_CONCURRENT_AGENTS=3`
- Optimize database queries: `python scripts/analyze_slow_queries.py`

---

## 🎯 Roadmap & Future Plans

### Short-term (Next 3 months)
- **Enhanced Agent Coordination:** Better task distribution and load balancing
- **Advanced Error Recovery:** More sophisticated exception handling
- **Performance Optimization:** Faster agent response times and decision making
- **Additional Tool Integration:** Slack notifications, Jira integration, analytics dashboards

### Medium-term (3-12 months)  
- **Multi-Model Support:** Integration with Claude, Gemini, and other AI models
- **Domain Template Library:** Pre-configured setups for common domains (e-commerce, SaaS, mobile)
- **Advanced Analytics:** Predictive modeling for development timelines and success rates
- **Enterprise Features:** SSO, audit logging, compliance reporting

### Long-term (1+ years)
- **Autonomous Architecture Evolution:** AI team adapts its own processes based on success metrics
- **Cross-Project Learning:** Agents learn from successful patterns across multiple projects
- **Human-AI Collaboration Tools:** Enhanced interfaces for human-AI teamwork
- **Industry Standardization:** Contribute to standards for AI development teams

### Community-Driven Features
Vote on and contribute to upcoming features:
- **Visual Workflow Builder:** GUI for customizing agent workflows
- **Agent Marketplace:** Share and discover specialized agent configurations
- **Integration Ecosystem:** Pre-built connectors for popular development tools
- **Educational Resources:** Tutorials, courses, and certification programs

---

## 📞 Support & Getting Help

### Documentation Resources
- **📖 Complete Setup Guide:** `SETUP_GUIDE.md` for detailed installation
- **🔧 Adaptation Guide:** `ADAPTATION_GUIDE.md` for customizing to your domain  
- **🏗️ Architecture Deep-dive:** `docs/dna/architecture.md` for technical details
- **🤖 Agent Customization:** `docs/implementation/agent_customization.md`

### Community Support
- **💬 GitHub Discussions:** Ask questions, share experiences, get help from community
- **🐛 Issue Tracker:** Report bugs, request features, track development progress
- **📧 Direct Contact:** For enterprise inquiries and partnerships
- **🎥 Video Tutorials:** Step-by-step guides for common tasks and customizations

### Professional Services
- **🏢 Enterprise Setup:** Custom implementation for large organizations
- **📚 Training Programs:** Workshops on AI team development and management
- **🔧 Custom Adaptations:** Professional services for complex domain adaptations
- **📊 Success Optimization:** Consulting on maximizing AI team effectiveness

### Emergency Support
- **🚨 Critical Issues:** For production-down situations affecting live systems
- **⚡ Rapid Response:** 24-hour response for enterprise customers
- **🔒 Security Issues:** Dedicated channel for reporting security vulnerabilities

---

### License: Creative Commons BY-NC-SA 4.0
This project is licensed under the Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International license. See the `LICENSE` file for full details.

**What this means:**
- ❌ **Commercial Use:** You may **not** use this project for primarily commercial purposes without explicit permission.
- ✅ **Modification:** Adapt and build upon the project freely.
- ✅ **Distribution:** Share the project and your adaptations with others.
- ✅ **Private Use:** Use internally within your organization or for personal, non-commercial projects.
- ⚠️ **Attribution:** You must give appropriate credit, provide a link to the license, and indicate if changes were made.
- ⚠️ **ShareAlike:** If you remix, transform, or build upon the material, you must distribute your contributions under the same license as the original.

### Trademark Notice
"DigiNativa" is a trademark used for our specific implementation of this learning game. When you adapt this framework for your project, please use your own project name and branding.

### Contributing License Agreement
By contributing to this project, you agree that your contributions will be licensed under the same Creative Commons BY-NC-SA 4.0 license.

---

## 🙏 Acknowledgments

### Core Technologies
- **[CrewAI](https://github.com/joaomdmoura/crewAI):** The multi-agent framework that makes this possible
- **[OpenAI](https://openai.com/):** GPT-4 powers our intelligent agents
- **[React](https://reactjs.org/):** Frontend framework for modern web applications
- **[FastAPI](https://fastapi.tiangolo.com/):** High-performance Python web framework
- **[Netlify](https://netlify.com/):** Serverless deployment and hosting platform

---

## 📊 Project Statistics

![GitHub stars](https://img.shields.io/github/stars/jhonnyo88/multi-agent-setup)
![GitHub forks](https://img.shields.io/github/forks/jhonnyo88/multi-agent-setup)  
![GitHub issues](https://img.shields.io/github/issues/jhonnyo88/multi-agent-setup)
![GitHub pull requests](https://img.shields.io/github/issues-pr/jhonnyo88/multi-agent-setup)

**Development Activity:**
- **Total Commits:** [Auto-updated]
- **Contributors:** [Auto-updated]  
- **Languages:** Python, TypeScript, JavaScript, Markdown
- **Code Quality:** ![Codecov](https://img.shields.io/codecov/c/github/jhonnyo88/multi-agent-setup)

**Community Metrics:**
- **Active Installations:** [Tracked via telemetry with user consent]
- **Successful Adaptations:** [Community-reported implementations]
- **Enterprise Deployments:** [Known production usage]

---

*Last updated: December 2024 | Next major update: Q1 2025*

**Ready to build your own AI development team? [Start with our 5-minute setup](#-quick-start) or [explore the adaptation guide](ADAPTATION_GUIDE.md).**
