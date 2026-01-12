import 'react-native-gesture-handler';
import React, { useState, useRef, useEffect, useContext } from 'react';
import { StyleSheet, Text, View, TouchableOpacity, ActivityIndicator, StatusBar, Platform } from 'react-native';
import { SafeAreaProvider, SafeAreaView } from 'react-native-safe-area-context';
import * as ImagePicker from 'expo-image-picker';
import { UploadCloud, Maximize2, Minimize2, AlertCircle, X, Zap, ChevronRight, ChevronLeft, Eye, EyeOff } from 'lucide-react-native';
import { useVideoPlayer, VideoView } from 'expo-video';
import UploadService from './src/services/UploadService.js';
import { VideoCompressionService } from './src/services/VideoCompressionService';
import SkeletonOverlay from './src/components/SkeletonOverlay';
import BatTrailOverlay from './src/components/BatTrailOverlay';
import Slider from '@react-native-community/slider';
import { Config } from './src/config.js';
import { UserProvider, UserContext } from './src/context/UserContext';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import LoginScreen from './src/screens/LoginScreen';
import SignupScreen from './src/screens/SignupScreen';
import ProfileScreen from './src/screens/ProfileScreen';
import SwingDetailScreen from './src/screens/SwingDetailScreen';
import { Home, User } from 'lucide-react-native';
import MainApp from './src/components/MainApp';

// --- MODERN THEME ---
const THEME = {
  bg: '#F8F9FA',      // Clean Off-White
  card: '#FFFFFF',    // Pure White
  primary: '#0F172A', // Navy/Slate (Text)
  accent: '#2563EB',  // Royal Blue (Action)
  error: '#EF4444',   // Red
  subtext: '#64748B', // Cool Gray
  border: '#E2E8F0'   // Light Gray
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: THEME.bg },

  // Header
  headerContainer: { paddingHorizontal: 24, paddingTop: 20, paddingBottom: 30 },
  badge: { flexDirection: 'row', alignItems: 'center', alignSelf: 'flex-start', backgroundColor: '#EFF6FF', paddingHorizontal: 10, paddingVertical: 4, borderRadius: 12, marginBottom: 12 },
  badgeText: { color: THEME.accent, fontSize: 12, fontWeight: '700', marginLeft: 6 },
  title: {
    fontSize: 34,
    fontWeight: 'bold', // '800' often fails on Android stock fonts
    color: THEME.primary,
    letterSpacing: 0.5
  },
  subtitle: { fontSize: 17, color: THEME.subtext, marginTop: 4, fontWeight: '500' },

  // Upload Card
  uploadCard: {
    backgroundColor: THEME.card,
    borderRadius: 24,
    padding: 32,
    alignItems: 'center',
    marginHorizontal: 24,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 10 },
    shadowOpacity: 0.08,
    shadowRadius: 20,
    elevation: 6, // Android Shadow
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.5)'
  },
  iconCircle: { width: 80, height: 80, borderRadius: 40, backgroundColor: '#F1F5F9', alignItems: 'center', justifyContent: 'center', marginBottom: 20 },
  ctaText: { fontSize: 20, fontWeight: '700', color: THEME.primary, marginBottom: 8 },
  ctaSubtext: { fontSize: 14, color: THEME.subtext, textAlign: 'center', marginBottom: 24, lineHeight: 20 },
  primaryButton: { backgroundColor: THEME.primary, paddingVertical: 16, paddingHorizontal: 32, borderRadius: 16, flexDirection: 'row', alignItems: 'center', width: '100%', justifyContent: 'center' },
  primaryButtonText: { color: '#FFF', fontSize: 16, fontWeight: '700', marginRight: 8 },

  // Loading State
  statusCard: { flex: 1, justifyContent: 'center', alignItems: 'center', padding: 40 },
  loadingText: { marginTop: 24, fontSize: 18, fontWeight: '700', color: THEME.primary },
  progressTrack: { width: '100%', height: 8, backgroundColor: '#E2E8F0', borderRadius: 4, marginTop: 16, overflow: 'hidden' },
  progressBar: { height: '100%', backgroundColor: THEME.accent },
  cancelBtn: { marginTop: 32, paddingVertical: 10, paddingHorizontal: 20 },
  cancelText: { color: THEME.subtext, fontWeight: '600' },

  // Results View
  resultsContainer: { flex: 1, padding: 20 },
  videoFrame: {
    width: '100%',
    backgroundColor: '#000',
    borderRadius: 24,
    overflow: 'hidden',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.2,
    shadowRadius: 12,
    elevation: 8,
    borderWidth: 1,
    borderColor: '#333'
  },

  // Bottom Action Bar
  actionBar: { flexDirection: 'row', marginTop: 20, gap: 12 },
  actionBtn: { flex: 1, backgroundColor: THEME.card, padding: 16, borderRadius: 16, alignItems: 'center', flexDirection: 'row', justifyContent: 'center', shadowColor: '#000', shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.05, shadowRadius: 4, elevation: 2 },
  actionBtnText: { color: THEME.primary, fontWeight: '700', marginLeft: 8 },

  // Floating Error Toast
  errorToast: {
    position: 'absolute',
    bottom: 40,
    left: 20,
    right: 20,
    backgroundColor: '#1E293B', // Dark Slate
    borderRadius: 16,
    padding: 16,
    flexDirection: 'row',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 10,
    zIndex: 999
  },
  errorTextContent: { flex: 1, marginLeft: 12 },
  errorTitle: { color: '#FFF', fontWeight: '700', fontSize: 14 },
  errorMsg: { color: '#94A3B8', fontSize: 12, marginTop: 2 },
  retryPill: { backgroundColor: THEME.accent, paddingVertical: 10, paddingHorizontal: 20, borderRadius: 12 },
  retryText: { color: '#FFF', fontWeight: '700', fontSize: 14 },

  // Compression Overlay (DM-29)
  compressionOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.85)',
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 1000,
  },
  compressionModal: {
    backgroundColor: THEME.card,
    borderRadius: 24,
    padding: 40,
    alignItems: 'center',
    minWidth: 240,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 10 },
    shadowOpacity: 0.3,
    shadowRadius: 20,
    elevation: 10,
  },
  compressionText: {
    fontSize: 18,
    fontWeight: '700',
    color: THEME.primary,
    marginTop: 20,
  },
  compressionProgress: {
    fontSize: 32,
    fontWeight: '800',
    color: THEME.accent,
    marginTop: 12,
  },
  compressionSubtext: {
    fontSize: 14,
    color: THEME.subtext,
    marginTop: 8,
  },

  // DM-59: Scrubbing Controls
  scrubControls: {
    backgroundColor: THEME.card,
    borderRadius: 16,
    padding: 16,
    marginHorizontal: 20,
    marginTop: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 3,
  },
  frameInfo: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 12,
  },
  frameText: {
    fontSize: 14,
    fontWeight: '600',
    color: THEME.primary,
  },
  timeText: {
    fontSize: 14,
    color: THEME.subtext,
  },
  scrubRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  stepButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: THEME.bg,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: THEME.border,
  },
  scrubSlider: {
    flex: 1,
    height: 40,
  },

  // Fullscreen
  fullscreenContainer: { position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: '#000', zIndex: 1000 },
  closeFab: { position: 'absolute', top: 60, right: 24, backgroundColor: 'rgba(255,255,255,0.2)', width: 44, height: 44, borderRadius: 22, alignItems: 'center', justifyContent: 'center' }
});

const AuthStack = createStackNavigator();

function AuthNavigator() {
  return (
    <NavigationContainer>
      <AuthStack.Navigator
        screenOptions={{
          headerShown: false
        }}
      >
        <AuthStack.Screen name="Login" component={LoginScreen} />
        <AuthStack.Screen name="Signup" component={SignupScreen} />
      </AuthStack.Navigator>
    </NavigationContainer>
  );
}

const MainTabs = createBottomTabNavigator();
const ProfileStack = createStackNavigator();

// Profile Stack Navigator (for nested navigation to SwingDetailScreen)
function ProfileStackNavigator() {
  return (
    <ProfileStack.Navigator>
      <ProfileStack.Screen
        name="ProfileHome"
        component={ProfileScreen}
        options={{ headerShown: false }}
      />
      <ProfileStack.Screen
        name="SwingDetail"
        component={SwingDetailScreen}
        options={{
          title: 'Swing Details',
          headerBackTitle: 'Back'
        }}
      />
    </ProfileStack.Navigator>
  );
}

function MainTabNavigator() {
  return (
    <MainTabs.Navigator
      screenOptions={{
        headerShown: false,
        tabBarActiveTintColor: THEME.accent,
        tabBarInactiveTintColor: THEME.subtext,
        tabBarStyle: {
          backgroundColor: THEME.card,
          borderTopColor: THEME.border,
          paddingBottom: Platform.OS === 'ios' ? 20 : 8,
          paddingTop: 8,
          height: Platform.OS === 'ios' ? 85 : 60,
        },
      }}
    >
      <MainTabs.Screen
        name="Upload"
        component={MainApp}
        options={{
          tabBarIcon: ({ color, size }) => <Home size={size} color={color} />,
        }}
      />
      <MainTabs.Screen
        name="Profile"
        component={ProfileStackNavigator}
        options={{
          tabBarIcon: ({ color, size }) => <User size={size} color={color} />,
        }}
      />
    </MainTabs.Navigator>
  );
}

export default function App() {
  return (
    <UserProvider>
      <AppContent />
    </UserProvider>
  );
}

function AppContent() {
  const { user, loading } = useContext(UserContext);

  console.log('AppContent render - user:', user, 'loading:', loading);

  if (loading) {
    return (
      <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#F8F9FA' }}>
        <ActivityIndicator size="large" color="#2563EB" />
        <Text style={{ marginTop: 16, color: '#64748B' }}>Loading...</Text>
      </View>
    );
  }

  if (!user) {
    console.log('No user, rendering AuthNavigator');
    return <AuthNavigator />;
  }

  console.log('User logged in, rendering MainTabNavigator');
  return (
    <NavigationContainer>
      <SafeAreaView style={{ flex: 1, backgroundColor: THEME.bg }} edges={['bottom']}>
        <MainTabNavigator />
      </SafeAreaView>
    </NavigationContainer>
  );
}