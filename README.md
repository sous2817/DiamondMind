DiamondMind ⚾️

AI-Driven Baseball Swing Analysis (Mobile & Cloud)

Moneyball in your pocket. My specialized computer vision pipeline that extracts skeletal biomechanics from simple smartphone video.

🏗 The Architecture ("How I survive the Free Tier")

This isn't a simple CRUD app. To run heavy computer vision (MediaPipe) without crashing my free-tier cloud instances (512MB RAM limit), I had to split the stack into a Microservices Triad:

Mobile App (Client): React Native (Expo SDK 52). I use this for video capture, compression, and rendering the overlay.

API Gateway (Orchestrator): Python FastAPI. This is my traffic controller. It streams data; I designed it to never load full videos into memory.

AI Worker (The Muscle): Python 3.12 + MediaPipe (Docker). A dedicated worker that processes frames and spits out coordinates.

🔄 Data Flow

Mobile → (Multipart Stream) → API Gateway → (Stream) → AI Worker → JSON Result

☠️ "Tribal Knowledge" (READ THIS BEFORE CODING)

These are the non-negotiable rules of this repo. I learned these the hard way. Do not refactor these "fixes" unless you want to break production.

1. The "Legacy" Upload Fix

Expo SDK 52 broke standard background uploads. I explicitly use the legacy filesystem to get around this.

Rule: Must use import * as FileSystem from 'expo-file-system/legacy';

Rule: uploadType must be 1 (Integer), not the Enum.

2. The "Response Format" Rule

The Mobile App's skeleton overlay is dumb. It expects landmarks in a specific array order (0-32).

Rule: The AI Service MUST return landmarks as an Array, never as named objects (e.g., {"NOSE": ...} is forbidden).

3. The "Streaming" Mandate

My backend runs on a potato (Render Free Tier).

Rule: I never write await file.read() in the backend. I use generators to stream chunks to the AI service. If I load a 50MB video into RAM, the server will crash.

4. The "Race Condition" Check

The new Expo Video player is fast but sensitive.

Rule: I don't manually call .play() immediately after setting state. I use the useVideoPlayer hook to handle the lifecycle to avoid the java.lang.Integer crash.

🚀 Quick Start (Hybrid Mode)

The best way I've found to develop is running the App locally while pointing to the Cloud Backend.

Clone the Repo (I set it up for a Windows/Monorepo environment).

Check Config: I ensure diamondmind-mobile/src/config.js points to the Live URL.

Run Mobile:

cd diamondmind-mobile
npx expo start


Wake the Servers:

Since I'm on the Free Tier, services sleep after 15 mins.

Action: I hit the backend URL (/docs) in my browser to wake them up before testing.

🛠 Tech Stack

Frontend: React Native, Expo, NativeWind (Tailwind), Lucide Icons.

Backend: FastAPI, Uvicorn, Websockets (for real-time progress bars).

AI: MediaPipe Pose Landmarker, OpenCV (Headless).

Infra: Docker, Render.com.

🛑 Troubleshooting 

"Timeout Error": The server is cold. I go wake it up and wait 60 seconds.

"Skeleton not showing": I check the console. If frames_with_person is 0, the lighting was bad or the AI returned a Dictionary instead of an Array.

"Black Bar at Bottom": That's the Expo LogBox. I suppressed it in Prod, but if it pops up, I check my console.error logs.

Maintained by the Engineer. Always check DiamondMind_Master_Context.md before starting a new ticket.
