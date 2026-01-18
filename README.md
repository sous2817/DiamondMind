# DiamondMind ⚾

**AI-powered swing analysis that turns your phone into a hitting coach.**

## What It Does

DiamondMind analyzes baseball swing videos using computer vision. Upload a video from your phone, and get back:

- **Skeletal overlay** showing body mechanics throughout the swing
- **Bat tracking** with speed and path visualization
- **Phase breakdown** identifying load, stride, and contact timing
- **Swing metrics** for tracking improvement over time

Built for players who want data-driven feedback without expensive motion capture equipment.

## The Problem

Traditional swing analysis requires:
- Lab setups with specialized cameras ($10K+)
- Third-party software subscriptions ($50/month)
- Manual video review frame-by-frame

Most youth and amateur players can't access professional biomechanical analysis.

## The Solution

DiamondMind uses MediaPipe pose detection to extract 33 body landmarks from standard smartphone video. The analysis runs entirely in the cloud - no app downloads, no local processing power needed.

**Current capabilities:**
- Pose landmark extraction (33 points per frame)
- Real-time analysis with progress tracking
- Swing history and comparison
- Mobile-optimized video playback with synchronized overlay

**In development:**
- YOLO-based bat detection for accurate tracking in all lighting conditions
- Automated swing phase detection
- Bat speed calculation and velocity metrics
- Contact quality scoring (0-100 scale)

## Tech Stack

**Mobile:** React Native + Expo  
**Backend:** FastAPI (Python)  
**AI Service:** MediaPipe Pose Landmarker + YOLOv8 (Dockerized)  
**Infrastructure:** Render.com

The architecture splits heavy computer vision processing into a dedicated service to run reliably on free-tier cloud hosting.

## Current Status

**Working:**
- Video upload and cloud processing
- Skeletal overlay rendering
- WebSocket progress updates
- User authentication and swing history

**Active Development (DM-53):**
- Training YOLOv8 bat detection model on 5,596 annotated images
- Target: 70-85% mAP for production-grade tracking
- Expected completion: Q1 2026

## Getting Started

**Mobile App:**
```bash
cd diamondmind-mobile
npx expo start
```

**Note:** Backend services sleep after 15 minutes on free tier. First request may take 30-60 seconds while services wake up.

## Roadmap

1. **Complete YOLO bat detection** (replaces unreliable color-based tracking)
2. **Automated swing metrics** (speed, phase timing, swing plane)
3. **Comparison tools** (side-by-side analysis of multiple swings)
4. **Coaching insights** (AI-generated feedback and drill recommendations)

## Documentation

- **AI Context:** `docs/AI_CONTEXT.md` - Technical implementation details
- **Training Guide:** `ai-service/yolo-bat-detection/docs/TRAINING_OPTIMIZATION.md`
- **Project Structure:** `ai-service/yolo-bat-detection/PROJECT_STRUCTURE.md`

## Contributing

Check `docs/CONTEXT_DOC.md` for architectural decisions and tribal knowledge before making changes.

Built by a solo developer working to make swing analysis accessible to every player.
