/**
 * UserContext - Global user state management with Supabase Auth (DM-15)
 * Manages user authentication state and profile data across the app.
 */
import React, { createContext, useState, useEffect } from 'react';
import { AuthService } from '../services/AuthService';
import { supabase } from '../config/supabaseConfig';

export const UserContext = createContext();

export const UserProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [profile, setProfile] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadUser();

        // Listen to Supabase auth state changes
        const { data: { subscription } } = supabase.auth.onAuthStateChange(async (event, session) => {
            console.log('🔄 Auth state changed:', event);

            if (event === 'SIGNED_IN' && session) {
                // User signed in
                const profile = await AuthService.fetchProfile(session.access_token);
                setUser({
                    id: session.user.id,
                    email: session.user.email,
                    session
                });
                setProfile(profile);
            } else if (event === 'SIGNED_OUT') {
                // User signed out
                setUser(null);
                setProfile(null);
            } else if (event === 'TOKEN_REFRESHED' && session) {
                // Token refreshed - update session
                setUser(prev => prev ? { ...prev, session } : null);
            }
        });

        // Cleanup subscription on unmount
        return () => {
            subscription.unsubscribe();
        };
    }, []);

    const loadUser = async () => {
        console.log('🔄 Loading user session...');
        const userData = await AuthService.getCurrentUser();

        if (userData) {
            setUser({
                id: userData.id,
                email: userData.email,
                session: userData.session
            });
            setProfile(userData.profile);
        }

        setLoading(false);
        console.log('✅ User context initialized:', userData ? userData.email : 'No user');
    };

    const login = async (email, password) => {
        const userData = await AuthService.login(email, password);
        setUser({
            id: userData.id,
            email: userData.email,
            session: userData.session
        });
        setProfile(userData.profile);
        return userData;
    };

    const signup = async (email, password) => {
        const userData = await AuthService.signup(email, password);
        setUser({
            id: userData.id,
            email: userData.email,
            session: userData.session
        });
        // Profile will be created automatically by backend on first API call
        return userData;
    };

    const logout = async () => {
        await AuthService.logout();
        setUser(null);
        setProfile(null);
    };

    const updateProfile = async (updates) => {
        const updatedProfile = await AuthService.updateProfile(updates);
        setProfile(updatedProfile);
        return updatedProfile;
    };

    return (
        <UserContext.Provider value={{
            user,
            profile,
            setUser,
            setProfile,
            loading,
            login,
            signup,
            logout,
            updateProfile
        }}>
            {children}
        </UserContext.Provider>
    );
};
