// Single Source of Truth for API URLs
// Change this ONE place to update both WebSocket and HTTP connections.

const LIVE_BACKEND_URL = "diamondmind-backend-yalf.onrender.com";

export const Config = {
    // HTTP URL (e.g., https://diamondmind-backend-yalf.onrender.com)
    API_BASE_URL: `https://${LIVE_BACKEND_URL}`,

    // WebSocket URL (e.g., wss://diamondmind-backend-yalf.onrender.com)
    WS_BASE_URL: `wss://${LIVE_BACKEND_URL}`,

    // Supabase Configuration (DM-15)
    SUPABASE_URL: "https://zgwxrfetbplatwpimmec.supabase.co",
    SUPABASE_ANON_KEY: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inpnd3hyZmV0YnBsYXR3cGltbWVjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njc5ODU1NTksImV4cCI6MjA4MzU2MTU1OX0.pK7OCmcF6Do7Qb0OMINCTNVY_6M1b09-Ir-fw967gEg",
};