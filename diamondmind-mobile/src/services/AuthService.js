/**
 * AuthService - Supabase Authentication Integration (DM-15)
 * Handles user signup, login, logout, and session management via Supabase Auth.
 */
import AsyncStorage from '@react-native-async-storage/async-storage';
import axios from 'axios';
import { Config } from '../config';
import { supabase } from '../config/supabaseConfig';

const USER_SESSION_KEY = 'user_session';
const PROFILE_KEY = 'user_profile';

export const AuthService = {
    /**
     * Sign up a new user with Supabase Auth
     * @param {string} email - User email
     * @param {string} password - User password
     * @returns {Promise<Object>} User object with session
     */
    async signup(email, password) {
        try {
            console.log('🔐 Signing up with Supabase:', email);

            // Sign up with Supabase (email confirmation disabled for MVP)
            const { data, error } = await supabase.auth.signUp({
                email,
                password,
                options: {
                    emailRedirectTo: undefined, // No email confirmation
                }
            });

            if (error) {
                console.error('❌ Supabase signup failed:', error.message);
                throw new Error(error.message);
            }

            if (!data.user || !data.session) {
                throw new Error('Signup failed: No user or session returned');
            }

            console.log('✅ Supabase signup successful:', data.user.email);

            // Save session to AsyncStorage
            await this.saveUserSession(data.session);

            // Return user object
            return {
                id: data.user.id,
                email: data.user.email,
                session: data.session
            };
        } catch (error) {
            console.error('❌ Signup failed:', error.message);
            throw error;
        }
    },

    /**
     * Login existing user with Supabase Auth
     * @param {string} email - User email
     * @param {string} password - User password
     * @returns {Promise<Object>} User object with session
     */
    async login(email, password) {
        try {
            console.log('🔐 Logging in with Supabase:', email);

            const { data, error } = await supabase.auth.signInWithPassword({
                email,
                password
            });

            if (error) {
                console.error('❌ Supabase login failed:', error.message);
                throw new Error(error.message);
            }

            if (!data.user || !data.session) {
                throw new Error('Login failed: No user or session returned');
            }

            console.log('✅ Supabase login successful:', data.user.email);

            // Save session to AsyncStorage
            await this.saveUserSession(data.session);

            // Fetch profile from backend
            const profile = await this.fetchProfile(data.session.access_token);

            return {
                id: data.user.id,
                email: data.user.email,
                session: data.session,
                profile
            };
        } catch (error) {
            console.error('❌ Login failed:', error.message);
            throw error;
        }
    },

    /**
     * Logout current user
     */
    async logout() {
        try {
            console.log('🚪 Logging out...');

            // Sign out from Supabase
            const { error } = await supabase.auth.signOut();

            if (error) {
                console.error('⚠️ Supabase logout error:', error.message);
            }

            // Clear AsyncStorage
            await AsyncStorage.removeItem(USER_SESSION_KEY);
            await AsyncStorage.removeItem(PROFILE_KEY);

            console.log('✅ Logout successful');
        } catch (error) {
            console.error('❌ Logout failed:', error);
            throw error;
        }
    },

    /**
     * Get current user session from Supabase
     * @returns {Promise<Object|null>} User object with session or null
     */
    async getCurrentUser() {
        try {
            // Try to get session from Supabase
            const { data: { session }, error } = await supabase.auth.getSession();

            if (error) {
                console.error('❌ Failed to get session:', error.message);
                return null;
            }

            if (!session) {
                console.log('📱 No active session found');
                return null;
            }

            console.log('📱 Loaded session for:', session.user.email);

            // Fetch profile from backend
            const profile = await this.fetchProfile(session.access_token);

            return {
                id: session.user.id,
                email: session.user.email,
                session,
                profile
            };
        } catch (error) {
            console.error('❌ Failed to load user:', error);
            return null;
        }
    },

    /**
     * Get access token for API requests
     * @returns {Promise<string|null>} JWT access token
     */
    async getAccessToken() {
        try {
            const { data: { session } } = await supabase.auth.getSession();
            return session?.access_token || null;
        } catch (error) {
            console.error('❌ Failed to get access token:', error);
            return null;
        }
    },

    /**
     * Fetch user profile from backend
     * @param {string} accessToken - Supabase JWT token
     * @returns {Promise<Object|null>} User profile object
     */
    async fetchProfile(accessToken) {
        try {
            const response = await axios.get(
                `${Config.API_BASE_URL}/api/profile`,
                {
                    headers: {
                        'Authorization': `Bearer ${accessToken}`
                    }
                }
            );

            console.log('✅ Profile fetched:', response.data.username);

            // Save profile to AsyncStorage
            await AsyncStorage.setItem(PROFILE_KEY, JSON.stringify(response.data));

            return response.data;
        } catch (error) {
            console.error('⚠️ Failed to fetch profile:', error.response?.data || error.message);
            return null;
        }
    },

    /**
     * Update user profile
     * @param {Object} updates - Profile fields to update (age_group, handedness, height_cm)
     * @returns {Promise<Object>} Updated profile
     */
    async updateProfile(updates) {
        try {
            const accessToken = await this.getAccessToken();

            if (!accessToken) {
                throw new Error('Not authenticated');
            }

            const response = await axios.patch(
                `${Config.API_BASE_URL}/api/profile`,
                null,
                {
                    params: updates,
                    headers: {
                        'Authorization': `Bearer ${accessToken}`
                    }
                }
            );

            console.log('✅ Profile updated');

            // Save updated profile to AsyncStorage
            await AsyncStorage.setItem(PROFILE_KEY, JSON.stringify(response.data));

            return response.data;
        } catch (error) {
            console.error('❌ Profile update failed:', error.response?.data || error.message);
            throw error;
        }
    },

    /**
     * Save user session to AsyncStorage
     * @param {Object} session - Supabase session object
     */
    async saveUserSession(session) {
        try {
            await AsyncStorage.setItem(USER_SESSION_KEY, JSON.stringify(session));
            console.log('💾 Session saved');
        } catch (error) {
            console.error('❌ Failed to save session:', error);
            throw error;
        }
    }
};
