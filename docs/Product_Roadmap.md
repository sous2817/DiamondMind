# DiamondMind Product Roadmap

**Last Updated:** 2026-01-11  
**Current Phase:** Platform Stabilization & Feature Completion

---

## Product Vision

**DiamondMind** is an AI-powered baseball swing analysis platform that provides instant, professional-grade coaching feedback through computer vision and natural language AI.

**Target Users:**
- Youth baseball players (10u-18u)
- College and adult players
- Coaches and trainers
- Parents supporting player development

---

## Current Status

### Completed (35+ features live)
- ✅ Core pose detection and skeleton overlay
- ✅ Video upload and async processing
- ✅ Real-time WebSocket progress
- ✅ Bat trail tracking (geometric)
- ✅ Frame-by-frame playback
- ✅ User authentication (Supabase)
- ✅ User profiles (age, handedness, height)
- ✅ Swing history management
- ✅ Custom swing metadata (titles/notes)
- ✅ Performance optimizations (frame skipping, async processing)
- ✅ Cloud database (PostgreSQL)
- ✅ Dockerized AI service

### In Progress
- 🚧 DM-15: User profile UI enhancements
- 🚧 Platform stability improvements

---

## Roadmap Phases

### Phase 1: Platform Stabilization (Q1 2026) - CURRENT

**Goal:** Complete core features and ensure production readiness

**Priorities:**
1. **Video Serving (DM-61)** - HIGH
   - Serve videos via HTTP for mobile streaming
   - Enable video playback in SwingDetailScreen
   - **Impact:** Better UX, proper video access

2. **Full Video Player (DM-60)** - MEDIUM
   - Add video playback to SwingDetailScreen
   - Include skeleton overlay and bat trail
   - **Impact:** Complete feature parity

3. **Native Video Compression (DM-58)** - HIGH
   - Implement real compression (post-Expo Go)
   - Reduce upload sizes 70-80%
   - **Impact:** Faster uploads, prevent crashes

**Success Metrics:**
- All core features production-ready
- Video playback working across all screens
- Upload success rate > 95%

---

### Phase 2: GenAI & Coaching (Q2 2026)

**Goal:** Transform raw data into actionable coaching with AI

**Priorities:**
1. **Vector Database (DM-43)** - HIGH
   - Store swings for semantic search
   - Foundation for all GenAI features
   - **Impact:** Enables advanced AI features

2. **RAG Pipeline (DM-44)** - HIGH
   - Natural language coaching feedback
   - Context-aware analysis
   - **Impact:** Professional coaching quality

3. **Semantic Search (DM-45)** - MEDIUM
   - Find similar swings ("Pro Comps")
   - Visual learning tool
   - **Impact:** Unique differentiator

4. **LLM Comparisons (DM-46)** - MEDIUM
   - AI-generated swing comparison summaries
   - Explain why swings are similar
   - **Impact:** Educational value

5. **AI Chatbot (DM-47)** - MEDIUM
   - Interactive Q&A about swings
   - Follow-up questions
   - **Impact:** Engagement and retention

**Success Metrics:**
- Feedback quality score > 4.5/5
- Chatbot engagement > 40% of users
- Pro comp feature usage > 60%

---

### Phase 3: Platform Expansion (Q3-Q4 2026)

**Goal:** Expand reach and add new modes

**Priorities:**
1. **React Web App (DM-31)** - MEDIUM
   - Desktop browser access
   - Larger screens for analysis
   - **Impact:** Market expansion

2. **Pitching Analysis (DM-19)** - MEDIUM
   - Separate mode for pitching mechanics
   - Different metrics and feedback
   - **Impact:** Doubles addressable market

3. **Native Mobile Apps (DM-18)** - MEDIUM
   - App Store and Play Store builds
   - Native performance
   - **Impact:** Professional distribution

4. **Text-to-Speech (DM-14)** - LOW
   - Audio coaching feedback
   - Hands-free practice
   - **Impact:** Accessibility

**Success Metrics:**
- Web users: 30% of total
- Pitching mode adoption: 20%
- App Store rating > 4.5 stars

---

## Feature Backlog (Prioritized)

### High Priority
- Video HTTP serving (DM-61)
- Native video compression (DM-58)
- Vector database integration (DM-43)
- RAG pipeline (DM-44)

### Medium Priority
- Full video player in detail screen (DM-60)
- Semantic search (DM-45)
- LLM swing comparisons (DM-46)
- AI coaching chatbot (DM-47)
- React web app (DM-31)
- Pitching analysis mode (DM-19)
- Native mobile wrapper (DM-18)
- Text-to-speech feedback (DM-14)

### Low Priority
- Progressive Web App (DM-17)
- YOLO bat detection dataset (DM-53)

### Deferred
- Video export with overlay (DM-40) - Complex, uncertain ROI

---

## Dependencies

```
Phase 1 (Parallel):
├─ DM-61 (Video Serving) → Independent
├─ DM-60 (Video Player) → Needs DM-61
└─ DM-58 (Compression) → Independent

Phase 2 (Sequential):
DM-43 (Vector DB)
    ├─→ DM-44 (RAG Pipeline)
    │       ├─→ DM-47 (Chatbot)
    │       └─→ DM-46 (Comparison Summaries)
    └─→ DM-45 (Similarity Search)
            └─→ DM-46 (Comparison Summaries)

Phase 3 (Parallel):
├─ DM-31 (Web App) → Independent
├─ DM-19 (Pitching) → Independent
├─ DM-18 (Native) → Independent
└─ DM-14 (TTS) → Needs DM-44
```

---

## Risk Assessment

### High Risk
- **GenAI Features (DM-43-47):** LLM costs, quality control, hallucinations
  - *Mitigation:* Start small, strict prompts, budget monitoring

### Medium Risk
- **Native Compression (DM-58):** Platform-specific implementation
  - *Mitigation:* Use proven libraries, thorough testing
- **Web App (DM-31):** CORS, browser compatibility
  - *Mitigation:* Progressive enhancement, testing

### Low Risk
- **Video Serving (DM-61):** Well-understood pattern
- **Video Player (DM-60):** Reuse existing components

---

## Success Criteria

### Platform Health
- Uptime > 99%
- Analysis success rate > 95%
- Average processing time < 30s
- User retention > 60%

### Feature Adoption
- Profile completion rate > 70%
- Swing history usage > 80%
- Frame-by-frame usage > 50%

### Growth Metrics
- Monthly active users: 100+ (Q2), 500+ (Q4)
- Swings analyzed: 1000+ (Q2), 5000+ (Q4)
- User satisfaction: > 4.5/5

---

## Next Steps

**Immediate (Next 2 weeks):**
1. Complete DM-15 profile UI
2. Start DM-61 (Video HTTP serving)
3. Plan DM-58 (Native compression)

**Short Term (Next month):**
1. Deploy DM-61 and DM-60
2. Begin DM-58 implementation
3. Research vector database options (DM-43)

**Medium Term (Q2 2026):**
1. Complete Phase 1 features
2. Begin GenAI implementation
3. Gather user feedback for Phase 3 priorities

---

## Budget Considerations

### Phase 1: $0
- Infrastructure optimization only
- Use existing free tiers

### Phase 2: $100-200
- LLM API costs (OpenAI/Anthropic)
- Vector database (Pinecone/Weaviate)

### Phase 3: $100-300
- Apple Developer account ($99/year)
- Google Play account ($25 one-time)
- Potential hosting upgrades

**Total Estimated:** $200-500 for full roadmap

---

## Alternative Strategies

### "GenAI First" Approach
Prioritize AI differentiation over stability:
- **Phase 1:** DM-43 → DM-44 → DM-45 → DM-46 (GenAI core)
- **Phase 2:** DM-61 → DM-60 → DM-58 (Platform features)
- **Phase 3:** DM-31 → DM-19 → DM-18 (Expansion)

**Pros:** Faster time-to-market for differentiating features  
**Cons:** Higher risk, potential stability issues  
**Recommendation:** Stick with balanced roadmap for sustainable growth

---

## Related Documentation

- **Features:** See `FEATURES.md` for detailed feature documentation
- **Technical:** See `CONTEXT_DOC.md` for implementation details
- **JIRA:** See `completebacklog_20260111.json` for full ticket list
