/**
 * Supabase client configuration for DiamondMind mobile app.
 * Provides authentication and user management via Supabase Auth.
 */
import { createClient } from '@supabase/supabase-js';
import { Config } from '../config';

// Initialize Supabase client with anon key (safe for client-side)
export const supabase = createClient(
    Config.SUPABASE_URL,
    Config.SUPABASE_ANON_KEY,
    {
        auth: {
            // Disable email confirmation for faster onboarding (can enable later)
            autoRefreshToken: true,
            persistSession: true,
            detectSessionInUrl: false
        }
    }
);

console.log('✅ Supabase client initialized:', Config.SUPABASE_URL);
