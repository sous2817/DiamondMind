# DiamondMind - Product Requirements Document

**Version:** 1.0  
**Last Updated:** 2026-01-12  
**Status:** Active Development  
**Document Owner:** Product Team  

---

## Executive Summary

**DiamondMind** is an AI-powered baseball swing analysis platform that provides instant, professional-grade coaching feedback using computer vision and pose detection. The product democratizes expensive swing analysis technology, making it accessible to players of all levels through a simple mobile app.

**Key Value Proposition:**  
Turn any smartphone into a $10,000 swing analysis system in seconds.

---

## 1. Product Vision & Goals

### Vision Statement
Empower every baseball and softball player to improve their swing mechanics through instant, AI-driven feedback—anytime, anywhere.

### Mission
Democratize professional swing analysis by making it:
- **Accessible:** Free mobile app, no special equipment
- **Instant:** Results in under 60 seconds
- **Actionable:** Clear metrics and coaching insights
- **Accurate:** Professional-grade AI analysis

### Success Metrics
- **User Engagement:** >70% of users upload 2+ swings within first week
- **Analysis Quality:** >85% accuracy in pose detection (currently 38% bat detection, targeting 85%)
- **Performance:** <60 seconds end-to-end analysis time
- **Retention:** 40% weekly active users (WAU)
- **Platform Goals:** 10,000+ users by end of 2026

---

## 2. Target Users

### Primary Personas

**1. Youth Player (Ages 10-18)**
- **Needs:** Improve mechanics, track progress, impress scouts
- **Pain Points:** Expensive private coaching ($100+/hr), limited repetition feedback
- **Usage:** 3-5 swings per practice session, 2-3x per week

**2. Parent/Coach**
- **Needs:** Objective data to guide instruction, demonstrate improvement
- **Pain Points:** Subjective feedback, can't review swings in real-time
- **Usage:** Analyze team members, share with parents

**3. Amateur Adult Player**
- **Needs:** Self-improvement, competitive edge in leagues
- **Pain Points:** No access to professional coaching, want data-driven insights
- **Usage:** Pre-season training, troubleshooting swing issues

### Secondary Personas
- College/professional scouts looking for objective metrics
- Hitting instructors supplementing in-person coaching

---

## 3. Core Features

### 3.1 Swing Upload & Analysis (MVP - LIVE)

**User Story:** As a player, I want to upload a video of my swing and get instant analysis, so I can identify mechanical flaws.

**Functional Requirements:**
- ✅ Record or upload video from camera roll
- ✅ Support 720p+ video quality
- ✅ Process videos 5-60 seconds in length
- ✅ Real-time progress indication during upload
- ✅ Async processing with WebSocket updates
- ✅ Return analysis within 60 seconds

**Technical Implementation:**
- Mobile: Expo Camera API or ImagePicker
- Backend: FastAPI async upload → background task
- AI: MediaPipe pose detection (33 keypoints)
- Storage: Temporary video storage (auto-delete after 24hrs)

**Acceptance Criteria:**
- User can upload video in <10 seconds
- Analysis completes in <60 seconds for 30 fps video
- App shows progress ("Processing swing... 45%")
- Errors handled gracefully with retry option

### 3.2 Pose Visualization (MVP - LIVE)

**User Story:** As a player, I want to see my body position at key swing moments, so I understand my mechanics.

**Functional Requirements:**
- ✅ Display 33 pose landmarks overlaid on video
- ✅ Show bat trail visualization
- ✅ Highlight key swing phases (setup, stride, contact, follow-through)
- ✅ Playback controls (play, pause, frame-by-frame)
- ✅ Zoom and pan on detection

**Technical Implementation:**
- Render skeleton using React Native SVG
- Interpolate landmarks between frames for smooth animation
- Color-code landmarks (green = high confidence, yellow = medium, red = low)

**Acceptance Criteria:**
- Skeleton overlay matches body position >90% accuracy
- Playback is smooth (30 fps) on mid-range devices
- User can step through frame-by-frame
- Visualization loads in <3 seconds

### 3.3 Swing Metrics Dashboard (MVP - LIVE)

**User Story:** As a player, I want to see key metrics about my swing, so I know what to improve.

**Functional Requirements:**
- ✅ Display swing speed (mph)
- ✅ Show swing plane angle
- ✅ Calculate body rotation (hip, shoulder)
- ✅ Measure weight transfer
- ✅ Detect early/late stride timing
- ✅ Present metrics in simple, visual format

**Current Metrics:**
1. **Hip Rotation:** Angle change from stance to contact
2. **Shoulder Rotation:** Torso twist measurement
3. **Weight Transfer:** Left-to-right foot pressure shift
4. **Swing Plane:** Bat path angle (upper-cut vs level)
5. **Timing:** Stride vs swing initiation sync

**Future Metrics (Roadmap):**
- Bat speed (mph) - requires bat tracking upgrade
- Launch angle - requires ball contact detection
- Exit velocity - requires ball tracking

**Acceptance Criteria:**
- All 5 current metrics display within 2 seconds
- Metrics update smoothly during video playback
- Values are within ±5% of professional equipment

### 3.4 Swing History & Progress Tracking (IN PROGRESS)

**User Story:** As a player, I want to see my swing history, so I can track improvement over time.

**Functional Requirements:**
- [ ] List view of all past swings with thumbnails
- [ ] Filter by date range
- [ ] Compare two swings side-by-side
- [ ] Track metric trends over time (graphs)
- [ ] Tag swings (e.g., "Tee work", "Live BP", "Game")

**Technical Implementation:**
- PostgreSQL: User-swing relationship with metadata
- Mobile: Infinite scroll list with lazy loading
- Charts: React Native Chart Kit

**Acceptance Criteria:**
- Load 50 swings in <2 seconds
- Side-by-side comparison shows metrics diff
- Trend graphs show 30-day rolling average

### 3.5 AI-Powered Coaching Insights (PLANNED)

**User Story:** As a player, I want personalized coaching tips based on my swing data, so I know exactly what to fix.

**Functional Requirements:**
- [ ] Analyze swing mechanics and detect issues
- [ ] Provide 3-5 actionable coaching cues per swing
- [ ] Prioritize issues by severity
- [ ] Show reference videos of correct technique
- [ ] Track improvement on specific issues over time

**Example Insights:**
- "Your hips are rotating late. Focus on starting rotation before foot plant."
- "Weight is staying on back foot. Try 60/40 weight transfer at contact."
- "Bat path is dropping below shoulder plane. Keep hands above ball."

**Technical Implementation:**
- Rule-based analysis engine (v1)
- Machine learning model (v2) trained on pro swings
- LLM integration for natural language coaching

**Acceptance Criteria:**
- Insights generated in <5 seconds
- 80%+ users find insights "helpful" (survey)
- Insights match professional coach feedback >70% of time

### 3.6 User Accounts & Authentication (LIVE)

**User Story:** As a user, I want to create an account, so my swing data is saved and accessible across devices.

**Functional Requirements:**
- ✅ Email/password registration
- ✅ Third-party auth (Google, Apple)
- ✅ Secure JWT token-based authentication
- ✅ Password reset flow
- ✅ Profile management (name, age, position, handedness)

**Technical Implementation:**
- Supabase Auth for user management
- JWT tokens for API authorization
- Mobile: SecureStore for token persistence

**Acceptance Criteria:**
- Account creation in <30 seconds
- Login persists across app restarts
- Password reset email received in <2 minutes

---

## 4. Technical Requirements

### 4.1 Performance

| Metric | Target | Current |
|--------|--------|---------|
| Video upload time | <10s (10MB file) | ✅ ~5s |
| Analysis processing | <60s | ✅ ~30-45s |
| App launch time (cold) | <3s | ✅ ~2s |
| Swing list load | <2s (50 items) | ⚠️ Not implemented |
| API response time (p95) | <500ms | ✅ ~200ms |

### 4.2 Scalability

**Current Capacity:**
- API Gateway: 1 instance, 512MB RAM (Render free tier)
- AI Worker: 1 instance, 512MB RAM (Docker on Render)
- Database: PostgreSQL, 256MB storage

**Scaling Plan:**
- **100 users:** Current setup sufficient
- **1,000 users:** Add horizontal AI worker scaling (queue-based)
- **10,000+ users:** Migrate to paid tier, CDN for videos, Redis cache

### 4.3 Reliability

**Uptime SLA:** 99% (excluding planned maintenance)

**Error Handling:**
- Retry logic for network failures (3 attempts)
- Graceful degradation (offline mode for viewing past swings)
- User-friendly error messages ("Analysis failed. Retrying...")

**Monitoring:**
- Sentry for error tracking
- Render logs for backend monitoring
- Analytics dashboard for user metrics

### 4.4 Security

**Data Protection:**
- Videos deleted after 24 hours (GDPR compliance)
- User data encrypted at rest (PostgreSQL)
- HTTPS for all API communication
- JWT tokens expire after 24 hours

**Authentication:**
- Supabase Auth (SOC 2 compliant)
- Password hashing (bcrypt)
- Rate limiting on API endpoints (100 requests/min/user)

**Privacy:**
- No video sharing without explicit consent
- Analytics anonymized
- COPPA compliant (parental consent for <13)

---

## 5. AI/ML Specifications

### 5.1 Pose Detection (Current - MediaPipe)

**Model:** MediaPipe Pose v2  
**Accuracy:** 95%+ for landmark detection  
**Performance:** 14-20 fps on CPU  
**Output:** 33 keypoints (x, y, z, visibility)

**Limitations:**
- Struggles with:
  - Heavy motion blur (fast swings)
  - Occluded body parts
  - Low-light conditions
  - Side-angle views (not front-facing)

**Improvement Plan:**
- Add motion blur compensation
- Multi-angle support (side view analysis)
- Fine-tune model on baseball swing dataset

### 5.2 Bat Detection (In Progress - YOLOv8)

**Current Status:** v2 trained (725 images)
- Model: YOLOv8n (3M parameters)
- mAP@50: 38% (baseline)
- Precision: 64.6%
- Inference: 3.5ms/frame

**Target:** 85%+ mAP for production

**Dataset Needs:**
- 2,000+ annotated images
- Diverse bat types (wood, metal, colors)
- Various lighting conditions
- Multiple camera angles

**Timeline:**
- Q1 2026: Collect 2,000+ images via Label Studio
- Q2 2026: Train v3 model, integrate into pose_engine
- Q3 2026: Replace geometric bat tracking with YOLO

---

## 6. User Experience & Design

### 6.1 Design Principles

1. **Simplicity First:** One-tap upload, zero configuration
2. **Instant Feedback:** Show progress at every step
3. **Visual Learning:** More diagrams, less text
4. **Mobile-Optimized:** Touch-friendly, works on small screens

### 6.2 Key User Flows

**Upload & Analyze Flow:**
1. Open app → See upload button (prominent)
2. Tap "Record Swing" → Camera opens
3. Record swing → Tap stop
4. Confirm video → "Analyze Swing"
5. Upload starts → Progress bar (0-100%)
6. "Processing swing..." → WebSocket updates ("50% complete")
7. Analysis complete → Results screen
8. View swing visualization → Swipe for metrics

**Target Time:** 90 seconds from open app → view results

### 6.3 Mobile UI/UX Requirements

**Must-Have:**
- Dark mode support (reduce eye strain)
- Offline mode for viewing past swings
- Haptic feedback for key actions
- Onboarding tutorial (skip-able)

**Nice-to-Have:**
- AR overlay for real-time swing tips
- Voice coaching (audio feedback)
- Social sharing (blur face for privacy)

---

## 7. Business Model & Monetization

### 7.1 Pricing Strategy

**Freemium Model:**

**Free Tier:**
- 10 swing analyses per month
- Basic metrics (5)
- Swing history (30 days)
- Ad-supported

**Pro Tier ($9.99/month or $79.99/year):**
- Unlimited analyses
- Advanced metrics (bat speed, launch angle)
- Coaching insights (AI-generated)
- Swing history (unlimited)
- Export data (CSV)
- Ad-free

**Team/Coach Tier ($29.99/month):**
- All Pro features
- Manage 15 players
- Team analytics dashboard
- Shared swing library

### 7.2 Revenue Projections (Conservative)

**Year 1 (2026):**
- 10,000 users @ 5% conversion = 500 Pro users
- Revenue: $59,940/year (~$5,000/month)

**Year 2 (2027):**
- 50,000 users @ 7% conversion = 3,500 Pro users
- Revenue: $419,580/year (~$35,000/month)

### 7.3 Key Partnerships

**Target Partners:**
- Youth baseball leagues (referral programs)
- Hitting instructors (coach tier discounts)
- Baseball equipment brands (sponsorships)

---

## 8. Product Roadmap

### Q1 2026 (Current)**
- [x] MVP: Upload, analyze, visualize swings
- [x] User accounts & authentication
- [x] Basic metrics (5)
- [ ] Swing history & comparison
- [ ] YOLO bat detection v3 (85%+ mAP)

### Q2 2026
- [ ] AI coaching insights (v1 - rule-based)
- [ ] Advanced metrics (bat speed, exit velocity)
- [ ] Social features (share swings, leaderboards)
- [ ] Freemium monetization launch

### Q3 2026
- [ ] Multi-angle analysis (side view support)
- [ ] Team/coach dashboard
- [ ] iOS app launch (currently Android-first)
- [ ] Video trimming/editing tools

### Q4 2026
- [ ] AI coaching v2 (ML-powered)
- [ ] AR real-time feedback mode
- [ ] Integration with wearables (batting sensor data)
- [ ] 10,000 active users milestone

---

## 9. Success Criteria & KPIs

### Product-Market Fit Signals
- **Retention:** 40% weekly active users (WAU)
- **NPS Score:** >50 (currently unmeasured)
- **Viral Coefficient:** 1.2+ (users inviting others)
- **Pro Conversion:** 5%+ free → paid

### Technical Health
- **Uptime:** 99%+
- **API Latency (p95):** <500ms
- **Analysis Success Rate:** >95%
- **Bat Detection Accuracy:** >85% mAP

### User Satisfaction
- **App Store Rating:** 4.5+ stars
- **Support Tickets:** <5% of weekly active users
- **Feature Request Volume:** Growing month-over-month

---

## 10. Risks & Mitigation

### Technical Risks

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| AI model accuracy insufficient | High | Medium | Collect 2,000+ training images, use ensemble models |
| Serverless cold starts slow | Medium | High | Keep-alive pings, migrate to reserved instances |
| Video processing costs exceed budget | High | Low | Compress videos, limit free tier uploads |

### Business Risks

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Low user adoption | High | Medium | Invest in marketing, partnerships with leagues |
| Competitors with better tech | High | Low | Focus on UX, coach partnerships, community |
| Privacy concerns (COPPA) | Medium | Low | Clear parental consent, auto-delete videos |

### Market Risks

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Baseball declining popularity | Low | Very Low | Expand to softball, cricket (similar swing mechanics) |
| Professional coaches resist AI | Medium | Medium | Position as coaching supplement, not replacement |

---

## 11. Open Questions & Decisions Needed

### Product Questions
1. **Should we allow video sharing/social features?**  
   - Privacy concerns vs. viral growth potential
   - Decision needed by: Q2 2026

2. **What's the minimum viable accuracy for bat detection?**  
   - Current: 38% mAP, Target: 85%, Acceptable: 70%?
   - Decision needed by: Q1 2026

3. **Should we support pitching analysis too?**  
   - Expands market but dilutes focus
   - Decision needed by: Q3 2026

### Technical Questions
1. **When to migrate from free tier to paid hosting?**  
   - Trigger: >1,000 users or >$100/month cost?
   - Decision needed by: Q2 2026

2. **Should we build native iOS app or continue with Expo?**  
   - Trade-off: Development speed vs performance
   - Decision needed by: Q2 2026

---

## 12. Appendices

### A. Glossary

- **mAP:** Mean Average Precision (model accuracy metric)
- **MediaPipe:** Google's pose detection framework
- **YOLO:** You Only Look Once (object detection model)
- **Landmark:** Body keypoint (e.g., wrist, elbow, shoulder)
- **Swing Plane:** Angle of bat path through strike zone

### B. References

- Technical docs: `docs/AI_CONTEXT.md`, `docs/CONTEXT_DOC.md`
- Feature list: `docs/FEATURES.md`
- Roadmap: `docs/PRODUCT_ROADMAP.md`
- JIRA: DiamondMind board ([link])

### C. Change Log

- **2026-01-12 v1.0:** Initial PRD creation

---

**Document Status:** Living document, updated quarterly or as major features ship.

**Next Review:** April 2026
