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

function MainApp() {
  const { logout, user } = useContext(UserContext);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const [progress, setProgress] = useState(0);
  const [videoUri, setVideoUri] = useState(null);
  const [currentFrameData, setCurrentFrameData] = useState(null);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const abortControllerRef = useRef(null);
  const [videoDimensions, setVideoDimensions] = useState({ width: 0, height: 0 });
  const [containerDimensions, setContainerDimensions] = useState({ width: 0, height: 0 });
  const [fullscreenDimensions, setFullscreenDimensions] = useState({ width: 0, height: 0 });
  const [showOverlay, setShowOverlay] = useState(true);
  const [showBatTrail, setShowBatTrail] = useState(true);
  const [showSkeleton, setShowSkeleton] = useState(true);
  const [isCompressing, setIsCompressing] = useState(false);
  const [compressionProgress, setCompressionProgress] = useState(0);
  const [isScrubbing, setIsScrubbing] = useState(false);
  const [scrubPosition, setScrubPosition] = useState(0); // 0-1 range

  // ⚡️ PERFORMANCE: Track current frame index to avoid redundant state updates
  const currentFrameIndexRef = useRef(-1);

  // ⚡️ FIX: Logic moved inside the hook to avoid race conditions
  const player = useVideoPlayer(videoUri, (p) => {
    p.loop = true;
    p.timeUpdateEventInterval = 0.016;
    if (videoUri) {
      p.play();
    }
  });

  useEffect(() => {
    if (!player || !videoUri || !result || isScrubbing) return;
    const sub = player.addListener('timeUpdate', (payload) => {
      if (result?.frames && result.fps) {
        // ⚡️ OPTIMIZATION: Use O(1) direct index access instead of O(N) .find()
        // This eliminates the "loop over all frames" jitter
        const frameIndex = Math.floor(payload.currentTime * result.fps);

        // ⚡️ PERFORMANCE FIX: Only update state if frame actually changed
        // This reduces state updates from 60/sec to video FPS (~30/sec)
        if (frameIndex !== currentFrameIndexRef.current && frameIndex < result.frames.length) {
          currentFrameIndexRef.current = frameIndex;
          const frame = result.frames[frameIndex];

          if (frame) {
            setCurrentFrameData(frame.landmarks);
          }

          // DM-59: Update scrub position
          const position = payload.currentTime / (player.duration || 1);
          setScrubPosition(position);
        }
      }
    });
    return () => sub.remove();
  }, [player, videoUri, result, isScrubbing]);

  // DM-59: Scrubbing functions
  const handleScrubChange = (value) => {
    setScrubPosition(value);

    if (player && result) {
      const targetTime = value * (player.duration || 0);
      player.currentTime = targetTime;

      // Update frame data immediately
      const frameIndex = Math.floor(targetTime * result.fps);
      if (frameIndex >= 0 && frameIndex < result.frames.length) {
        currentFrameIndexRef.current = frameIndex;
        const frame = result.frames[frameIndex];
        if (frame) {
          setCurrentFrameData(frame.landmarks);
        }
      }
    }
  };

  const handleScrubComplete = () => {
    setIsScrubbing(false);
  };

  const stepForward = () => {
    if (!player || !result) return;

    const currentFrame = currentFrameIndexRef.current;
    const nextFrame = Math.min(currentFrame + 1, result.total_frames - 1);

    // Prevent timeUpdate listener from interfering
    setIsScrubbing(true);

    const targetTime = nextFrame / result.fps;
    player.currentTime = targetTime;
    player.pause();

    // Update scrub position
    const position = targetTime / (player.duration || 1);
    setScrubPosition(position);

    // Update frame data immediately
    if (nextFrame < result.frames.length) {
      currentFrameIndexRef.current = nextFrame;
      const frame = result.frames[nextFrame];
      if (frame) {
        setCurrentFrameData(frame.landmarks);
      }
    }

    // Re-enable timeUpdate listener after video has settled
    setTimeout(() => setIsScrubbing(false), 300);
  };

  const stepBackward = () => {
    if (!player || !result) return;

    const currentFrame = currentFrameIndexRef.current;
    const prevFrame = Math.max(currentFrame - 1, 0);

    // Prevent timeUpdate listener from interfering
    setIsScrubbing(true);

    const targetTime = prevFrame / result.fps;
    player.currentTime = targetTime;
    player.pause();

    // Update scrub position
    const position = targetTime / (player.duration || 1);
    setScrubPosition(position);

    // Update frame data immediately
    if (prevFrame >= 0 && prevFrame < result.frames.length) {
      currentFrameIndexRef.current = prevFrame;
      const frame = result.frames[prevFrame];
      if (frame) {
        setCurrentFrameData(frame.landmarks);
      }
    }

    // Re-enable timeUpdate listener after video has settled
    setTimeout(() => setIsScrubbing(false), 300);
  };

  const formatTime = (seconds) => {
    if (!seconds || isNaN(seconds)) return '0:00';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  // ✅ ALIGNMENT FIX: Update video dimensions from player source
  // This ensures we use the EXACT dimensions MediaPipe analyzed
  useEffect(() => {
    if (player?.src?.width && player?.src?.height) {
      setVideoDimensions({
        width: player.src.width,
        height: player.src.height
      });
    }
  }, [player]);

  // Calculate attack angle from bat trail data
  const calculateAttackAngle = () => {
    if (!result?.frames) return null;

    const batPositions = result.frames
      .map((frame, idx) => ({ ...frame.bat_position, frameIndex: idx }))
      .filter(pos => pos.x !== undefined && pos.y !== undefined);

    if (batPositions.length < 15) return null; // Need enough data points

    // Find contact point (lowest Y value, highest point in screen coords)
    const contactIdx = batPositions.reduce((minIdx, pos, idx) =>
      pos.y < batPositions[minIdx].y ? idx : minIdx, 0);

    const contactFrame = batPositions[contactIdx];

    // Get positions 5 frames before and after contact
    const beforeIdx = Math.max(0, contactIdx - 5);
    const afterIdx = Math.min(batPositions.length - 1, contactIdx + 5);

    const beforePos = batPositions[beforeIdx];
    const afterPos = batPositions[afterIdx];

    // Calculate angle (in degrees)
    // Positive angle = upward swing, Negative = downward
    const deltaY = afterPos.y - beforePos.y;
    const deltaX = afterPos.x - beforePos.x;
    const angleRad = Math.atan2(deltaY, deltaX);
    const angleDeg = angleRad * (180 / Math.PI);

    return Math.round(angleDeg);
  };

  const attackAngle = result ? calculateAttackAngle() : null;

  const handleUpload = async (uri) => {
    setLoading(true);
    setError(null);
    setProgress(0);

    abortControllerRef.current = new AbortController();
    const jobId = Math.random().toString(36).substring(7);

    // ✅ LOG: Connection Attempt (Section 14)
    console.log(`📡 WebSocket connecting to job: ${jobId}`);

    // Use centralized config
    const ws = new WebSocket(`${Config.WS_BASE_URL}/ws/progress/${jobId}`);

    // ✅ HEARTBEAT: Send a ping every 25s to keep the Read timeout from triggering on the LB
    // Render/Nginx closes connections if no data flows from Client -> Server for 60-100s.
    const pingInterval = setInterval(() => {
      if (ws.readyState === WebSocket.OPEN) {
        console.log("💓 Sending Ping...");
        ws.send(JSON.stringify({ type: "ping" }));
      }
    }, 25000);

    // ✅ LOG: Connection Success (Section 14)
    ws.onopen = () => {
      console.log("✅ WebSocket connected");
    };

    ws.onmessage = (e) => {
      const data = JSON.parse(e.data);
      if (data.progress) {
        // ✅ LOG: Progress Update (Section 14)
        console.log(`📊 Progress update: ${data.progress}%`);
        setProgress(data.progress);
      }

      // ⚡️ ASYNC Handling: Result comes via WebSocket now
      if (data.result) {
        console.log("✅ Received Result via WebSocket");
        setResult(data.result);
        setLoading(false);
        clearInterval(pingInterval);
        ws.close();
      }

      // ⚡️ ASYNC Handling: Errors via WebSocket
      if (data.error) {
        console.error("❌ Received Error via WebSocket:", data.error);
        setError(data.error);
        setLoading(false);
        clearInterval(pingInterval);
        ws.close();
      }
    };

    ws.onclose = () => {
      console.log("🔌 WebSocket closed");
      clearInterval(pingInterval);
    };

    try {
      // Note: "Starting upload..." log is handled inside UploadService.js
      const data = await UploadService.uploadSwingVideo(uri, jobId, user?.id, abortControllerRef.current.signal);

      // If sync response contains result (legacy behavior or fast response)
      if (data && data.frames) {
        setResult(data);
        setLoading(false);
        clearInterval(pingInterval);
        ws.close();
      } else {
        // ⏳ Async Mode: Server said "Processing", so we wait.
        // Do NOT set loading to false here.
        console.log("⏳ Upload accepted, waiting for AI processing...");
      }

    } catch (err) {
      console.error("❌ UPLOAD FAILED:", err);
      if (err.message !== 'canceled') {
        const msg = err.response?.data?.detail || err.message || "Connection timed out. Check server status.";
        setError(msg);
      }
      setLoading(false);
      clearInterval(pingInterval);
      ws.close();
    }
  };

  const pickVideo = async () => {
    try {
      let res = await ImagePicker.launchImageLibraryAsync({ mediaTypes: ['videos'], quality: 1 });
      if (res.canceled) return;
      const asset = res.assets[0];

      // Reset state
      setResult(null);
      setError(null);

      const originalUri = asset.uri;
      console.log('📹 Video selected:', originalUri);

      // Show compression UI
      setIsCompressing(true);
      setCompressionProgress(0);

      // Compress video
      const compressedUri = await VideoCompressionService.compressVideo(
        originalUri,
        (progress) => setCompressionProgress(progress)
      );

      setIsCompressing(false);

      // Set initial dimensions from asset (will be updated by player when loaded)
      setVideoDimensions({ width: asset.width, height: asset.height });
      setSelectedFile(asset.fileName || "swing.mp4");

      // ⚡️ FIX: Only set state here. The useVideoPlayer hook handles the play command.
      setVideoUri(compressedUri);

      handleUpload(compressedUri);

      // Cleanup old temp files (non-blocking)
      VideoCompressionService.cleanupTempFiles();

    } catch (error) {
      console.error('❌ Video processing failed:', error);
      setIsCompressing(false);
      setError('Failed to process video. Please try again.');
    }
  };

  const handleReset = () => {
    setResult(null);
    setVideoUri(null);
    setProgress(0);
    setCurrentFrameData(null);
    setIsFullscreen(false);
    setError(null);
    setShowOverlay(true); // Reset overlay to visible
    setShowBatTrail(true); // Reset bat trail to visible
    currentFrameIndexRef.current = -1; // Reset frame tracking
  };

  const videoRatio = player.src?.width ? player.src.width / player.src.height : 1.77;

  return (
    <UserProvider>
      <SafeAreaProvider>
        <StatusBar barStyle="dark-content" backgroundColor={THEME.bg} />

        {/* --- Fullscreen Mode --- */}
        {result && isFullscreen && (
          <View style={styles.fullscreenContainer}>
            <View style={{ flex: 1 }} onLayout={(e) => setFullscreenDimensions(e.nativeEvent.layout)}>
              <VideoView player={player} style={StyleSheet.absoluteFill} contentMode="contain" />
              <View style={StyleSheet.absoluteFill} pointerEvents="none">
                {showOverlay && (
                  <SkeletonOverlay
                    landmarks={currentFrameData}
                    videoWidth={videoDimensions.width}
                    videoHeight={videoDimensions.height}
                    containerWidth={fullscreenDimensions.width}
                    containerHeight={fullscreenDimensions.height}
                  />
                )}
              </View>
              {showBatTrail && (
                <BatTrailOverlay
                  frames={result.frames}
                  currentFrameIndex={currentFrameIndexRef.current}
                  videoWidth={videoDimensions.width}
                  videoHeight={videoDimensions.height}
                  containerWidth={fullscreenDimensions.width}
                  containerHeight={fullscreenDimensions.height}
                />
              )}
              <TouchableOpacity style={styles.closeFab} onPress={() => setIsFullscreen(false)}>
                <Minimize2 size={24} color="#FFF" />
              </TouchableOpacity>
              <TouchableOpacity
                style={{ position: 'absolute', top: 60, left: 24, backgroundColor: 'rgba(255,255,255,0.2)', width: 44, height: 44, borderRadius: 22, alignItems: 'center', justifyContent: 'center' }}
                onPress={() => setShowOverlay(!showOverlay)}
              >
                {showOverlay ? <Eye size={24} color="#FFF" /> : <EyeOff size={24} color="#FFF" />}
              </TouchableOpacity>
              <TouchableOpacity
                style={{ position: 'absolute', top: 110, left: 24, backgroundColor: 'rgba(255,255,255,0.2)', width: 44, height: 44, borderRadius: 22, alignItems: 'center', justifyContent: 'center' }}
                onPress={() => setShowBatTrail(!showBatTrail)}
              >
                <Text style={{ color: '#FFF', fontSize: 20, fontWeight: 'bold' }}>🏏</Text>
              </TouchableOpacity>
            </View>
          </View>
        )}

        {/* --- Main Interface --- */}
        {!isFullscreen && (
          <SafeAreaView style={styles.container}>

            {/* Header */}
            <View style={styles.headerContainer}>
              <View style={styles.badge}>
                <Zap size={12} color={THEME.accent} fill={THEME.accent} />
                <Text style={styles.badgeText}>AI POWERED</Text>
              </View>
              <Text style={styles.title}>DiamondMind</Text>
              <Text style={styles.subtitle}>Pro-Level Swing Analysis</Text>
            </View>

            {/* Content Area */}
            <View style={{ flex: 1 }}>

              {/* 1. Upload Card (Empty State) */}
              {!loading && !result && (
                <View style={styles.uploadCard}>
                  <View style={styles.iconCircle}>
                    <UploadCloud size={32} color={THEME.accent} />
                  </View>
                  <Text style={styles.ctaText}>Analyze a Swing</Text>
                  <Text style={styles.ctaSubtext}>Select a video from your gallery to generate a skeletal frame analysis.</Text>

                  <TouchableOpacity style={styles.primaryButton} onPress={pickVideo}>
                    <Text style={styles.primaryButtonText}>Open Gallery</Text>
                    <ChevronRight size={20} color="#FFF" />
                  </TouchableOpacity>
                </View>
              )}

              {/* 2. Loading State */}
              {loading && (
                <View style={styles.statusCard}>
                  <ActivityIndicator size="large" color={THEME.accent} />
                  <Text style={styles.loadingText}>Analyzing Swing...</Text>
                  <View style={styles.progressTrack}>
                    <View style={[styles.progressBar, { width: `${progress}%` }]} />
                  </View>
                  <Text style={{ marginTop: 8, color: THEME.subtext, fontSize: 12 }}>
                    Uploading & Processing: {progress}%
                  </Text>

                  <TouchableOpacity style={styles.cancelBtn} onPress={() => { abortControllerRef.current?.abort(); setLoading(false); }}>
                    <Text style={styles.cancelText}>Cancel</Text>
                  </TouchableOpacity>
                </View>
              )}

              {/* 3. Success / Results View */}
              {result && (
                <View style={styles.resultsContainer}>
                  <View
                    style={[styles.videoFrame, { aspectRatio: videoRatio }]}
                    onLayout={(e) => setContainerDimensions(e.nativeEvent.layout)}
                  >
                    <VideoView player={player} style={StyleSheet.absoluteFill} contentMode="contain" />
                    <View style={StyleSheet.absoluteFill} pointerEvents="none">
                      {showOverlay && (
                        <SkeletonOverlay
                          landmarks={currentFrameData}
                          videoWidth={videoDimensions.width}
                          videoHeight={videoDimensions.height}
                          containerWidth={containerDimensions.width}
                          containerHeight={containerDimensions.height}
                        />
                      )}
                    </View>
                    {showBatTrail && (
                      <BatTrailOverlay
                        frames={result.frames}
                        currentFrameIndex={currentFrameIndexRef.current}
                        videoWidth={videoDimensions.width}
                        videoHeight={videoDimensions.height}
                        containerWidth={containerDimensions.width}
                        containerHeight={containerDimensions.height}
                      />
                    )}
                    <TouchableOpacity
                      style={{ position: 'absolute', bottom: 16, left: 16, backgroundColor: 'rgba(0,0,0,0.6)', padding: 8, borderRadius: 20 }}
                      onPress={() => setShowOverlay(!showOverlay)}
                    >
                      {showOverlay ? <Eye size={20} color="#FFF" /> : <EyeOff size={20} color="#FFF" />}
                    </TouchableOpacity>
                    <TouchableOpacity
                      style={{ position: 'absolute', bottom: 16, left: 60, backgroundColor: 'rgba(0,0,0,0.6)', padding: 8, borderRadius: 20 }}
                      onPress={() => setShowBatTrail(!showBatTrail)}
                    >
                      <Text style={{ color: '#FFF', fontSize: 16, fontWeight: 'bold' }}>🏏</Text>
                    </TouchableOpacity>
                    <TouchableOpacity
                      style={{ position: 'absolute', bottom: 16, right: 16, backgroundColor: 'rgba(0,0,0,0.6)', padding: 8, borderRadius: 20 }}
                      onPress={() => setIsFullscreen(true)}
                    >
                      <Maximize2 size={20} color="#FFF" />
                    </TouchableOpacity>
                  </View>

                  {/* DM-59: Video Scrubbing Controls */}
                  {videoUri && player && (
                    <View style={styles.scrubControls}>
                      {/* Frame Info */}
                      <View style={styles.frameInfo}>
                        <Text style={styles.frameText}>
                          Frame {currentFrameIndexRef.current + 1} / {result.total_frames}
                        </Text>
                        <Text style={styles.timeText}>
                          {formatTime(player.currentTime)} / {formatTime(player.duration)}
                        </Text>
                      </View>

                      {/* Step Controls + Slider */}
                      <View style={styles.scrubRow}>
                        {/* Step Backward */}
                        <TouchableOpacity
                          style={styles.stepButton}
                          onPress={stepBackward}
                        >
                          <ChevronLeft size={24} color={THEME.primary} />
                        </TouchableOpacity>

                        {/* Slider */}
                        <Slider
                          style={styles.scrubSlider}
                          minimumValue={0}
                          maximumValue={1}
                          value={scrubPosition}
                          onValueChange={handleScrubChange}
                          onSlidingStart={() => {
                            setIsScrubbing(true);
                            player.pause();
                          }}
                          onSlidingComplete={handleScrubComplete}
                          minimumTrackTintColor={THEME.accent}
                          maximumTrackTintColor={THEME.border}
                          thumbTintColor={THEME.accent}
                        />

                        {/* Step Forward */}
                        <TouchableOpacity
                          style={styles.stepButton}
                          onPress={stepForward}
                        >
                          <ChevronRight size={24} color={THEME.primary} />
                        </TouchableOpacity>
                      </View>
                    </View>
                  )}

                  {/* Attack Angle Metric */}
                  {attackAngle !== null && (
                    <View style={{ marginTop: 16, backgroundColor: THEME.card, padding: 16, borderRadius: 16, shadowColor: '#000', shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.05, shadowRadius: 4, elevation: 2 }}>
                      <Text style={{ fontSize: 14, color: THEME.subtext, fontWeight: '600', marginBottom: 4 }}>Attack Angle</Text>
                      <Text style={{ fontSize: 28, color: THEME.primary, fontWeight: 'bold' }}>{attackAngle}°</Text>
                      <Text style={{ fontSize: 12, color: THEME.subtext, marginTop: 4 }}>
                        {attackAngle > 0 ? '↗ Upward swing' : attackAngle < 0 ? '↘ Downward swing' : '→ Level swing'}
                      </Text>
                    </View>
                  )}

                  {/* Action Buttons */}
                  <View style={styles.actionBar}>
                    <TouchableOpacity style={styles.actionBtn} onPress={handleReset}>
                      <X size={20} color={THEME.primary} />
                      <Text style={styles.actionBtnText}>New Swing</Text>
                    </TouchableOpacity>
                    {/* Download button removed as requested */}
                  </View>
                </View>
              )}
            </View>

            {/* --- Unified Floating Error Toast (Bottom) --- */}
            {error && (
              <View style={styles.errorToast}>
                <AlertCircle size={24} color="#EF4444" />
                <View style={styles.errorTextContent}>
                  <Text style={styles.errorTitle}>Analysis Failed</Text>
                  <Text style={styles.errorMsg} numberOfLines={1}>{error}</Text>
                </View>
                <TouchableOpacity style={styles.retryPill} onPress={pickVideo}>
                  <Text style={styles.retryText}>RETRY</Text>
                </TouchableOpacity>
                <TouchableOpacity style={{ marginLeft: 12 }} onPress={() => setError(null)}>
                  <X size={18} color="#64748B" />
                </TouchableOpacity>
              </View>
            )}

            {/* Compression Progress Overlay */}
            {isCompressing && (
              <View style={styles.compressionOverlay}>
                <View style={styles.compressionModal}>
                  <ActivityIndicator size="large" color={THEME.accent} />
                  <Text style={styles.compressionText}>
                    Optimizing Video...
                  </Text>
                  <Text style={styles.compressionProgress}>
                    {compressionProgress}%
                  </Text>
                  <Text style={styles.compressionSubtext}>
                    Preparing for upload
                  </Text>
                </View>
              </View>
            )}

          </SafeAreaView>
        )}
      </SafeAreaProvider>
    </UserProvider>
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