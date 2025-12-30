import React, { useState, useRef, useEffect } from 'react';
import { StyleSheet, Text, View, TouchableOpacity, ActivityIndicator, StatusBar, Platform } from 'react-native';
import { SafeAreaProvider, SafeAreaView } from 'react-native-safe-area-context';
import * as ImagePicker from 'expo-image-picker';
import { UploadCloud, Maximize2, Minimize2, AlertCircle, X, Download, Zap, ChevronRight } from 'lucide-react-native';
import { useVideoPlayer, VideoView } from 'expo-video';
import UploadService from './src/services/UploadService.js';
import SkeletonOverlay from './src/components/SkeletonOverlay';
import { captureRef } from 'react-native-view-shot';
import * as Sharing from 'expo-sharing';
import { Config } from './src/config.js';

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
  retryPill: { backgroundColor: 'rgba(255,255,255,0.1)', paddingHorizontal: 12, paddingVertical: 6, borderRadius: 8 },
  retryText: { color: '#FFF', fontSize: 12, fontWeight: '700' },

  // Fullscreen
  fullscreenContainer: { position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: '#000', zIndex: 1000 },
  closeFab: { position: 'absolute', top: 60, right: 24, backgroundColor: 'rgba(255,255,255,0.2)', width: 44, height: 44, borderRadius: 22, alignItems: 'center', justifyContent: 'center' }
});

export default function App() {
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
  const viewShotRef = useRef(null);
  const [isExporting, setIsExporting] = useState(false);

  // ⚡️ FIX: Logic moved inside the hook to avoid race conditions
  const player = useVideoPlayer(videoUri, (p) => {
    p.loop = true;
    p.timeUpdateEventInterval = 0.016;
    if (videoUri) {
      p.play();
    }
  });

  const handleExport = async () => {
    setIsExporting(true);
    try {
      const uri = await captureRef(viewShotRef, { format: 'png', quality: 0.8 });
      await Sharing.shareAsync(uri);
    } catch (err) {
      console.error("Export Failed:", err);
    } finally {
      setIsExporting(false);
    }
  };

  useEffect(() => {
    if (!player || !videoUri || !result) return;
    const sub = player.addListener('timeUpdate', (payload) => {
      if (result?.frames) {
        const frame = result.frames.find(f => f.timestamp >= payload.currentTime * 1000);
        if (frame) setCurrentFrameData(frame.landmarks);
      }
    });
    return () => sub.remove();
  }, [player, videoUri, result]);

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
    };

    try {
      // Note: "Starting upload..." log is handled inside UploadService.js
      const data = await UploadService.uploadSwingVideo(uri, jobId, abortControllerRef.current.signal);
      if (data) setResult(data);
      // Note: "Analysis complete..." log is handled inside UploadService.js
    } catch (err) {
      console.error("❌ UPLOAD FAILED:", err);
      if (err.message !== 'canceled') {
        const msg = err.response?.data?.detail || err.message || "Connection timed out. Check server status.";
        setError(msg);
      }
    } finally {
      setLoading(false);
      ws.close();
    }
  };

  const pickVideo = async () => {
    let res = await ImagePicker.launchImageLibraryAsync({ mediaTypes: ['videos'], quality: 1 });
    if (res.canceled) return;
    const asset = res.assets[0];

    // Reset state
    setResult(null);
    setError(null);

    setVideoDimensions({ width: asset.width, height: asset.height });
    setSelectedFile(asset.fileName || "swing.mp4");

    // ⚡️ FIX: Only set state here. The useVideoPlayer hook handles the play command.
    setVideoUri(asset.uri);

    handleUpload(asset.uri);
  };

  const handleReset = () => {
    setResult(null);
    setVideoUri(null);
    setProgress(0);
    setCurrentFrameData(null);
    setIsFullscreen(false);
    setError(null);
  };

  const videoRatio = player.src?.width ? player.src.width / player.src.height : 1.77;

  return (
    <SafeAreaProvider>
      <StatusBar barStyle="dark-content" backgroundColor={THEME.bg} />

      {/* --- Fullscreen Mode --- */}
      {result && isFullscreen && (
        <View style={styles.fullscreenContainer}>
          <View style={{ flex: 1 }} onLayout={(e) => setFullscreenDimensions(e.nativeEvent.layout)}>
            <VideoView player={player} style={StyleSheet.absoluteFill} contentMode="contain" />
            <View style={StyleSheet.absoluteFill} pointerEvents="none">
              <SkeletonOverlay
                landmarks={currentFrameData}
                videoWidth={videoDimensions.width}
                videoHeight={videoDimensions.height}
                containerWidth={fullscreenDimensions.width}
                containerHeight={fullscreenDimensions.height}
              />
            </View>
            <TouchableOpacity style={styles.closeFab} onPress={() => setIsFullscreen(false)}>
              <Minimize2 size={24} color="#FFF" />
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
                  ref={viewShotRef}
                  style={[styles.videoFrame, { aspectRatio: videoRatio }]}
                  onLayout={(e) => setContainerDimensions(e.nativeEvent.layout)}
                >
                  <VideoView player={player} style={StyleSheet.absoluteFill} contentMode="contain" />
                  <View style={StyleSheet.absoluteFill} pointerEvents="none">
                    <SkeletonOverlay
                      landmarks={currentFrameData}
                      videoWidth={videoDimensions.width}
                      videoHeight={videoDimensions.height}
                      containerWidth={containerDimensions.width}
                      containerHeight={containerDimensions.height}
                    />
                  </View>
                  <TouchableOpacity
                    style={{ position: 'absolute', bottom: 16, right: 16, backgroundColor: 'rgba(0,0,0,0.6)', padding: 8, borderRadius: 20 }}
                    onPress={() => setIsFullscreen(true)}
                  >
                    <Maximize2 size={20} color="#FFF" />
                  </TouchableOpacity>
                </View>

                {/* Action Buttons */}
                <View style={styles.actionBar}>
                  <TouchableOpacity style={styles.actionBtn} onPress={handleReset}>
                    <X size={20} color={THEME.primary} />
                    <Text style={styles.actionBtnText}>New Swing</Text>
                  </TouchableOpacity>

                  <TouchableOpacity
                    style={[styles.actionBtn, { backgroundColor: THEME.accent }]}
                    onPress={handleExport}
                    disabled={isExporting}
                  >
                    {isExporting ? (
                      <ActivityIndicator color="#FFF" />
                    ) : (
                      <>
                        <Download size={20} color="#FFF" />
                        <Text style={[styles.actionBtnText, { color: '#FFF' }]}>Save Analysis</Text>
                      </>
                    )}
                  </TouchableOpacity>
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

        </SafeAreaView>
      )}
    </SafeAreaProvider>
  );
}