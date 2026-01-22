// Single Source of Truth for API URLs
// Change this ONE place to update both WebSocket and HTTP connections.

// PRODUCTION (Render)
// const LIVE_BACKEND_URL = "diamondmind-backend-yalf.onrender.com";

// LOCAL DEVELOPMENT
// For Expo: Use your computer's local IP (find with `ipconfig` on Windows)
// OR use localhost if running on same machine/emulator
const LOCAL_BACKEND_URL = "192.168.50.160:8000";  // Your computer's IP

export const Config = {
    // HTTP URL (e.g., http://localhost:8000)
    API_BASE_URL: `http://${LOCAL_BACKEND_URL}`,

    // WebSocket URL (e.g., ws://localhost:8000)
    WS_BASE_URL: `ws://${LOCAL_BACKEND_URL}`,

    // Supabase Configuration (DM-15)
    SUPABASE_URL: "https://zgwxrfetbplatwpimmec.supabase.co",
    SUPABASE_ANON_KEY: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inpnd3hyZmV0YnBsYXR3cGltbWVjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njc5ODU1NTksImV4cCI6MjA4MzU2MTU1OX0.pK7OCmcF6Do7Qb0OMINCTNVY_6M1b09-Ir-fw967gEg",
};