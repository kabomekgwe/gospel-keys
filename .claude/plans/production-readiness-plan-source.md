# Piano Keys - Production Readiness Implementation Plan
**Making Piano Keys Production-Ready and User-Centered**

---

## Executive Summary

**Current State**: ~30% production ready
- Well-architected AI-powered multi-genre piano transcription platform
- CRITICAL security vulnerabilities: bypassed authentication, hardcoded secrets
- Testing coverage gaps: 12-15% (need 80%)
- Missing production infrastructure: SQLite (need PostgreSQL), local files (need S3)
- Limited UX: no onboarding, minimal accessibility, dark mode only

**Target State**: 100% production ready in 12 weeks
- Zero security vulnerabilities
- 80%+ test coverage with comprehensive E2E tests
- Production-grade infrastructure (PostgreSQL, S3/MinIO, Redis caching)
- User-centered design (onboarding, WCAG AA accessibility, contextual help)
- Full CI/CD pipeline with monitoring and observability

**Timeline**: 12 weeks (1-2 engineers)
**Budget**: ~$300/month infrastructure cost
**Strategy**: Security-first, incremental deployment, no breaking changes

---

## 6-Phase Roadmap

### Phase 1: Security & Foundation (Weeks 1-2) - CRITICAL BLOCKERS
**Goal**: Eliminate critical security vulnerabilities

**Week 1**: Critical Security Fixes
- Fix authentication bypass in `/backend/app/api/deps.py` (lines 30-48)
- Replace hardcoded secret key in `/backend/app/core/security.py` (line 17)
- Add rate limiting (slowapi) - 5 req/min auth, 10 req/hour uploads
- Implement security headers middleware (HSTS, CSP, X-Frame-Options)
- Add file upload security (MIME validation, virus scanning, random filenames)

**Week 2**: Foundation Infrastructure
- Implement structured logging with correlation IDs (`structlog`)
- Create global error handling middleware
- Add React Error Boundaries to frontend
- Set up secrets management and rotation
- Remove 24 console.log statements from production code

**Success Criteria**:
✓ No authentication bypasses
✓ No hardcoded secrets
✓ Rate limiting active on all endpoints
✓ All errors logged with context

---

### Phase 2: Infrastructure Migration (Weeks 3-4)
**Goal**: Migrate to production-grade database and storage

**Week 3**: PostgreSQL Migration
- Set up PostgreSQL 15+ with connection pooling
- Configure Alembic migrations
- Migrate SQLAlchemy from SQLite to PostgreSQL
- Add database indexes for performance
- Implement Redis caching layer (60%+ hit rate target)

**Week 4**: File Storage Migration
- Set up MinIO (self-hosted S3)
- Create storage abstraction layer (`storage_service.py`)
- Migrate file handling to S3 with presigned URLs
- Implement CDN-friendly headers
- Test horizontal scaling with 2+ instances

**Success Criteria**:
✓ PostgreSQL migration complete (0 data loss)
✓ Redis cache hit rate > 60%
✓ All files in S3/MinIO
✓ Application stateless and scalable

---

### Phase 3: Testing & Quality (Weeks 5-7)
**Goal**: Achieve 80% test coverage and code quality standards

**Week 5**: Backend Testing
- Configure pytest infrastructure with fixtures
- Write 215+ backend tests (services, API routes, database)
- Target: 80% backend coverage

**Week 6**: Frontend Testing
- Set up Vitest + React Testing Library + MSW
- Write 150+ frontend tests (components, routes, hooks)
- Target: 80% frontend coverage

**Week 7**: E2E Tests & Code Quality
- Write 20+ Playwright E2E tests for critical user journeys
- Configure Ruff (backend) + ESLint/Prettier (frontend)
- Set up mypy for type checking
- Add pre-commit hooks for automated quality checks

**Success Criteria**:
✓ Backend coverage > 80%
✓ Frontend coverage > 80%
✓ 20+ E2E tests passing
✓ 0 linting/type errors

---

### Phase 4: User Experience & Accessibility (Weeks 8-9)
**Goal**: Make application user-centered with WCAG AA compliance

**Week 8**: Onboarding & User Accounts
- Create authentication UI (login, signup, profile)
- Build onboarding wizard (skill level, genre preferences, goals)
- Implement help system and keyboard shortcuts modal
- Add user preferences with cross-device sync
- Make light/dark mode functional

**Week 9**: Accessibility & Notifications
- Accessibility audit with axe-core
- Add ARIA labels, keyboard navigation, screen reader support
- Fix color contrast issues
- Implement notification system (job completion, practice reminders)
- Create accessible toast components

**Success Criteria**:
✓ WCAG AA compliance 100%
✓ Onboarding completion rate > 80%
✓ All features keyboard accessible
✓ Screen reader tested

---

### Phase 5: CI/CD & Monitoring (Weeks 10-11)
**Goal**: Automated deployment pipeline and full observability

**Week 10**: CI/CD Pipeline
- Create GitHub Actions workflows (lint, test, security scan)
- Build deployment automation (staging, production)
- Implement blue-green deployment strategy
- Set up staging environment
- Create rollback procedures

**Week 11**: Monitoring & Observability
- Implement Prometheus `/metrics` endpoint
- Configure Grafana dashboards
- Integrate Sentry for error tracking
- Add APM for performance monitoring
- Create operational runbooks

**Success Criteria**:
✓ CI pipeline runtime < 15 minutes
✓ Deployment time < 5 minutes
✓ Monitoring dashboards live
✓ Error tracking active

---

### Phase 6: Production Hardening (Week 12)
**Goal**: Final security audit, load testing, and launch preparation

**Monday-Tuesday**: Security Audit
- Run OWASP ZAP automated scan
- Check OWASP Top 10 vulnerabilities
- Fix identified issues
- Document security policy

**Wednesday**: Load Testing
- Test with 100+ concurrent users (Locust/k6)
- Optimize bottlenecks
- Set performance baselines (API p95 < 200ms, FCP < 1.5s)

**Thursday**: Disaster Recovery
- Implement automated backups
- Test restoration procedures
- Document recovery process (RTO < 1 hour)

**Friday**: Launch Checklist
- Complete pre-launch checklist
- Verify all tests passing
- Configure SSL/TLS
- Prepare post-launch monitoring
- GO LIVE 🚀

**Success Criteria**:
✓ 0 critical vulnerabilities
✓ Handles 100+ concurrent users
✓ Backup/restore tested
✓ Launch checklist 100% complete

---

## Critical Files to Modify

### HIGHEST PRIORITY (Week 1)
1. **`/backend/app/api/deps.py`** - Remove authentication bypass (lines 30-48)
2. **`/backend/app/core/security.py`** - Replace hardcoded SECRET_KEY (line 17)
3. **`/backend/app/core/config.py`** - Add environment variable validation
4. **`/backend/app/main.py`** - Add middleware (rate limiting, security headers, error handling)

### HIGH PRIORITY (Weeks 2-4)
5. **`/backend/app/database/session.py`** - Migrate to PostgreSQL
6. **`/backend/.env.example`** - Document all environment variables
7. **`/frontend/src/routes/__root.tsx`** - Add Error Boundary
8. **`/backend/app/services/storage_service.py`** - Create S3 abstraction (NEW FILE)

### MEDIUM PRIORITY (Weeks 5-9)
9. **`/backend/tests/conftest.py`** - Test infrastructure
10. **`/frontend/src/test/utils.tsx`** - Frontend test utilities
11. **`/frontend/src/components/Piano.tsx`** - Accessibility improvements
12. **`/frontend/src/components/onboarding/OnboardingWizard.tsx`** - Onboarding flow (NEW FILE)

---

## Risk Mitigation & Rollback

### Database Migration (Week 3)
- **Risk**: Data loss
- **Mitigation**: Backup SQLite, test on copy, migrate during low-traffic window
- **Rollback**: Revert to SQLite backup, RTO < 1 hour

### Authentication Changes (Week 1)
- **Risk**: Locking out users
- **Mitigation**: Create admin bypass token, test with multiple users, deploy during low-traffic
- **Rollback**: Redeploy previous version, RTO < 5 minutes

### File Storage Migration (Week 4)
- **Risk**: File access broken
- **Mitigation**: Dual-write to local + S3, verify integrity, keep local copies 7 days
- **Rollback**: Revert to local filesystem, RTO < 30 minutes

---

## Success Metrics

### Security
- [ ] 0 authentication bypasses
- [ ] 0 hardcoded secrets
- [ ] Rate limiting on 100% endpoints
- [ ] 0 critical vulnerabilities (OWASP scan)

### Testing
- [ ] Backend coverage > 80%
- [ ] Frontend coverage > 80%
- [ ] 20+ E2E tests passing
- [ ] 0 linting/type errors

### Infrastructure
- [ ] PostgreSQL migration (0 data loss)
- [ ] Redis cache hit rate > 60%
- [ ] All files in S3
- [ ] App runs with 2+ instances

### User Experience
- [ ] WCAG AA compliance 100%
- [ ] Onboarding completion > 80%
- [ ] Light/dark mode functional
- [ ] 100% keyboard navigation

### Performance
- [ ] API response p95 < 200ms
- [ ] Frontend FCP < 1.5s
- [ ] Handles 100+ concurrent users
- [ ] Uptime > 99.9%

---

## Resource Requirements

### Infrastructure Costs
- **Staging**: $80/month (VPS, PostgreSQL, Redis, MinIO)
- **Production**: $180/month (2x app servers, larger database, storage)
- **Tools**: $40/month (Sentry, email service)
- **Total**: ~$300/month

### Team
- **Minimum**: 1 full-stack engineer (12 weeks full-time)
- **Optimal**: 1 backend + 1 frontend engineer (8 weeks with parallel work)

---

## Critical Path Dependencies

1. **Phase 1 MUST complete first** - All other work blocked on security fixes
2. **Phase 2 depends on Phase 1** - Database/storage require secure config
3. **Phase 3 can run parallel to Phase 2** (after Week 2) - Testing independent of infrastructure
4. **Phase 4 depends on Weeks 1-2 of Phase 2** - User accounts need PostgreSQL
5. **Phase 5 depends on Phase 3** - CI/CD requires tests
6. **Phase 6 depends on all phases** - Cannot launch without security, testing, infrastructure

---

## Next Steps

**When ready to execute:**

1. **Start with Week 1, Day 1** - Fix authentication bypass in `deps.py`
2. **Create feature branch** - `feature/production-readiness-phase-1`
3. **Work incrementally** - Small PRs, frequent testing
4. **Track progress** - Use todo list for each week's tasks
5. **Test rollback procedures** - Before each major change

**Key Principle**: Security first, test everything, deploy incrementally, monitor closely.

---

## Party Mode Team Assessment

🧙 **BMad Master's Recommendation**: This plan prioritizes the unsexy but critical work - security hardening, comprehensive testing, and production infrastructure. The modular phase structure allows flexibility while maintaining clear dependencies. The 12-week timeline is achievable with 1-2 dedicated engineers.

**Success requires discipline**: Don't skip Phase 1 (security) to jump to "more interesting" UX work. The foundation must be solid before building up.
