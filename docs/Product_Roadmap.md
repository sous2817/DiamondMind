# DiamondMind Product Roadmap
**Generated:** 2026-01-07  
**Backlog:** 17 stories analyzed

---

## Executive Summary

Based on the current backlog, I recommend a **3-phase roadmap** that balances quick wins, foundational infrastructure, and advanced AI features. This approach ensures steady progress with logical dependencies while delivering value incrementally.

**Total Estimated Effort:** ~330-438 hours (8-11 months at 10 hrs/week)

---

## Phase 1: Core UX & Performance (Q1 2026) - IN PROGRESS
**Goal:** Improve user experience and system stability  
**Duration:** 7-9 weeks  
**Effort:** ~112-138 hours  
**Completed:** 3/4 stories ✅

### Priority Order

#### 1. **DM-29: Mobile-Side Resolution Scaling** ✅ COMPLETE (HIGH)
- **Status:** Deployed 2026-01-08
- **Impact:** Video compression infrastructure in place
- **Effort:** 4 hours (actual)
- **Dependencies:** None
- **Value:** Foundation for native compression (DM-58)
- **Notes:** Expo Go compatible, real compression pending EAS build

#### 2. **DM-28: AI Service Frame Skipping** ✅ COMPLETE (HIGH)
- **Status:** Deployed 2026-01-08
- **Impact:** 40-50% faster processing (60-90s → 30-45s)
- **Effort:** 2 hours (actual)
- **Dependencies:** None
- **Value:** Reduced CPU usage, more stable on free tier
- **Notes:** FRAME_SKIP=2 deployed to Render

#### 3. **DM-59: Frame-by-Frame Video Scrubbing** ✅ COMPLETE (HIGH)
- **Status:** Deployed 2026-01-08
- **Impact:** Enables precise frame-by-frame swing analysis
- **Effort:** 8 hours (actual, including debugging)
- **Dependencies:** None
- **Value:** Professional video analysis tool, differentiating feature
- **Notes:** Slider + step buttons, skeleton overlay synced

#### 4. **DM-15: User Profile System** (HIGH)
- **Why Fourth:** Foundation for personalization, enables future features
- **Impact:** Enables age-appropriate feedback, user data management
- **Effort:** 40-50 hours (includes auth setup)
- **Dependencies:** None (enables DM-19)
- **Value:** Personalization, data ownership

**Phase 1 Deliverables:**
- ✅ Stable, fast analysis (no crashes) - **ACHIEVED via DM-28/29**
- ✅ Professional video scrubbing - **ACHIEVED via DM-59**
- ⏳ User accounts with profiles - **PENDING (DM-15)**
- ⏳ Foundation for personalization - **PENDING (DM-15)**

---

## Phase 2: GenAI Foundation (Q2 2026)
**Goal:** Build AI infrastructure for advanced features  
**Duration:** 10-13 weeks  
**Effort:** ~160-200 hours

### Priority Order

#### 6. **DM-43: Vector Database Integration** (HIGH)
- **Why First:** Foundation for all GenAI features
- **Impact:** Enables RAG, similarity search, comparisons
- **Effort:** 16-24 hours
- **Dependencies:** None
- **Value:** Unlocks entire GenAI roadmap

#### 7. **DM-44: RAG Pipeline for Natural Language Analysis** (HIGH)
- **Why Second:** Transforms raw data into actionable coaching
- **Impact:** Professional, authoritative feedback
- **Effort:** 40-50 hours
- **Dependencies:** DM-43 (vector DB)
- **Value:** Core differentiator, coaching quality

#### 8. **DM-45: Semantic Search for Similar Swings** (MEDIUM)
- **Why Third:** Builds on vector DB, high user value
- **Impact:** "Pro Comps" feature, visual learning
- **Effort:** 24-32 hours
- **Dependencies:** DM-43 (vector DB)
- **Value:** Unique feature, engagement driver

#### 9. **DM-46: LLM Summaries for Swing Comparisons** (MEDIUM)
- **Why Fourth:** Enhances DM-45 with explanations
- **Impact:** Explains *why* swings are similar
- **Effort:** 16-24 hours
- **Dependencies:** DM-44 (LLM), DM-45 (search)
- **Value:** Educational, user understanding

#### 10. **DM-47: AI Coaching Chatbot** (MEDIUM)
- **Why Fifth:** Advanced feature, builds on RAG
- **Impact:** Interactive coaching, Q&A
- **Effort:** 40-56 hours
- **Dependencies:** DM-44 (RAG pipeline)
- **Value:** Engagement, retention

**Phase 2 Deliverables:**
- ✅ Vector DB storing all swings
- ✅ Natural language coaching feedback
- ✅ Pro swing comparisons with explanations
- ✅ Interactive AI coach chatbot

---

## Phase 3: Platform Expansion (Q3-Q4 2026)
**Goal:** Expand reach and add advanced features  
**Duration:** 12-16 weeks  
**Effort:** ~120-160 hours

### Priority Order

#### 11. **DM-31: React Web Application** (MEDIUM)
- **Why First:** Expands user base, desktop analysis
- **Impact:** Larger screens, better for coaches
- **Effort:** 40-56 hours
- **Dependencies:** None (parallel to mobile)
- **Value:** Market expansion, accessibility

#### 12. **DM-19: Pitching Analysis Mode** (MEDIUM)
- **Why Second:** New market segment
- **Impact:** Doubles addressable market (pitchers)
- **Effort:** 32-40 hours
- **Dependencies:** DM-15 (user profiles for mode selection)
- **Value:** Market expansion, revenue potential

#### 13. **DM-14: Text-to-Speech Feedback** (MEDIUM)
- **Why Third:** Accessibility, hands-free usage
- **Impact:** Better UX for solo practice
- **Effort:** 16-24 hours
- **Dependencies:** DM-44 (feedback text)
- **Value:** Accessibility, usability

#### 14. **DM-18: Native App Wrapper (EAS)** (MEDIUM)
- **Why Fourth:** Production deployment
- **Impact:** App Store presence, native performance
- **Effort:** 24-32 hours
- **Dependencies:** None (but benefits from all features)
- **Value:** Professional distribution, monetization

**Phase 3 Deliverables:**
- ✅ Web application for desktop users
- ✅ Pitching analysis mode
- ✅ Audio feedback for hands-free practice
- ✅ Native iOS/Android apps in stores

---

## Deferred / Future Consideration

### Low Priority (Phase 4+)

#### **DM-17: Progressive Web App** (LOW)
- **Why Deferred:** Overlaps with DM-31 (web app)
- **Reconsider:** After DM-31 is complete, evaluate PWA benefits
- **Effort:** 8-12 hours

#### **DM-40: Video Export with Overlay** (LOWEST)
- **Why Deferred:** Nice-to-have, complex implementation
- **Reconsider:** After Phase 3, if user demand is high
- **Effort:** 32-48 hours

#### **DM-53: YOLO Bat Detection Dataset** (LOW)
- **Why Deferred:** Research project, uncertain ROI
- **Reconsider:** If HSV tracking proves insufficient
- **Effort:** 80-120 hours (dataset creation + training)

---

## Dependency Map

```
Phase 1 (Parallel):
├─ DM-29 (Mobile Scaling) → Independent
├─ DM-28 (Frame Skipping) → Independent
├─ DM-38 (Video Scrubbing) → Independent
└─ DM-15 (User Profiles) → Enables DM-19

Phase 2 (Sequential):
DM-43 (Vector DB)
    ├─→ DM-44 (RAG Pipeline)
    │       ├─→ DM-47 (Chatbot)
    │       └─→ DM-46 (Comparison Summaries)
    └─→ DM-45 (Similarity Search)
            └─→ DM-46 (Comparison Summaries)

Phase 3 (Parallel):
├─ DM-31 (Web App) → Independent
├─ DM-19 (Pitching) → Needs DM-15
├─ DM-14 (TTS) → Needs DM-44
└─ DM-18 (Native) → Independent
```

---

## Risk Assessment

### High Risk
- **DM-43-47 (GenAI Suite):** LLM costs, quality control, hallucinations
  - *Mitigation:* Start with small datasets, strict prompts, budget monitoring

### Medium Risk
- **DM-15 (Auth):** Security, session management
  - *Mitigation:* Use proven auth provider (Supabase/Firebase)
- **DM-31 (Web App):** CORS, browser compatibility
  - *Mitigation:* Thorough testing, progressive enhancement

### Low Risk
- **DM-29, DM-28 (Performance):** Well-understood optimizations
- **DM-38 (Scrubbing):** Standard video player feature

---

## Success Metrics

### Phase 1
- Analysis success rate: >95% (up from ~80%)
- Average processing time: <30 seconds (down from 60s)
- User retention: +20%

### Phase 2
- Feedback quality score: >4.5/5
- Chatbot engagement: >40% of users
- Pro comp feature usage: >60% of users

### Phase 3
- Web users: 30% of total user base
- Pitching mode adoption: 20% of users
- App Store rating: >4.5 stars

---

## Recommended Next Steps

1. **Immediate:** Start DM-29 (Mobile Scaling) - highest impact, lowest risk
2. **Week 2:** Parallel DM-28 (Frame Skipping) for compounding performance gains
3. **Week 4:** Begin DM-38 (Video Scrubbing) for UX differentiation
4. **Week 8:** Start DM-15 (User Profiles) to enable personalization
5. **Week 12:** Transition to Phase 2 with DM-43 (Vector DB)

**Budget Allocation:**
- Phase 1: $0 (infrastructure optimization)
- Phase 2: $100-200 (LLM API costs, vector DB)
- Phase 3: $100 (Apple Developer, Google Play fees)

---

## Alternative Roadmap: "GenAI First"

If you want to prioritize AI differentiation over stability:

**Phase 1:** DM-43 → DM-44 → DM-45 → DM-46 (GenAI core)  
**Phase 2:** DM-29 → DM-28 → DM-38 (Performance & UX)  
**Phase 3:** DM-15 → DM-31 → DM-19 (Platform expansion)

**Pros:** Faster time-to-market for differentiating features  
**Cons:** Higher risk of system instability, potential user frustration

**Recommendation:** Stick with the balanced roadmap above for sustainable growth.
