import React, { useState, useRef, useEffect } from 'react';
import { StyleSheet, Text, View, TouchableOpacity, ActivityIndicator, LogBox } from 'react-native';
import { SafeAreaProvider, SafeAreaView } from 'react-native-safe-area-context';
import * as ImagePicker from 'expo-image-picker';
import { UploadCloud, Maximize2, Minimize2, AlertCircle, XCircle } from 'lucide-react-native';
import { useVideoPlayer, VideoView } from 'expo-video';
import UploadService from './src/services/UploadService.js';
import SkeletonOverlay from './src/components/SkeletonOverlay';

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F2F2F7', padding: 20 },
  header: { alignItems: 'center', marginTop: 20, marginBottom: 40 },
  title: { fontSize: 32, fontWeight: '900', color: '#1C1C1E' },
  subtitle: { fontSize: 16, color: '#8E8E93' },
  uploadCard: { backgroundColor: '#FFF', borderRadius: 20, padding: 40, alignItems: 'center', borderStyle: 'dashed', borderWidth: 2, borderColor: '#007AFF' },
  uploadText: { marginTop: 15, fontSize: 18, fontWeight: '600' },
  statusCard: { backgroundColor: '#FFF', borderRadius: 20, padding: 30, alignItems: 'center' },
  loadingText: { marginTop: 20, fontSize: 16, fontWeight: '700' },
  progressContainer: { width: '100%', height: 10, backgroundColor: '#E5E5EA', borderRadius: 5, overflow: 'hidden', marginVertical: 15 },
  progressBar: { height: '100%', backgroundColor: '#007AFF' },
  progressText: { fontSize: 14, fontWeight: '600', color: '#007AFF', marginBottom: 5 },
  successCard: { backgroundColor: '#FFF', borderRadius: 20, padding: 20 },
  // Removed hardcoded aspectRatio to allow dynamic sizing
  videoWrapper: { width: '100%', backgroundColor: '#000', borderRadius: 15, overflow: 'hidden', position: 'relative' },
  resetButton: { marginTop: 20, backgroundColor: '#007AFF', padding: 15, borderRadius: 12, alignItems: 'center' },
  resetButtonText: { color: '#FFF', fontWeight: '700' },
  fullscreenContainer: { position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: '#000', zIndex: 1000 },
  fullscreenVideoWrapper: { flex: 1, width: '100%', height: '100%', justifyContent: 'center', alignItems: 'center' },
  modernExpandButton: { position: 'absolute', backgroundColor: 'rgba(28, 28, 30, 0.8)', alignItems: 'center', justifyContent: 'center', zIndex: 1001 },
  errorCard: { backgroundColor: '#FFF', borderRadius: 20, padding: 20, alignItems: 'center' },
  errorText: { color: '#1C1C1E', fontWeight: '600', marginVertical: 10 },
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

  const player = useVideoPlayer(videoUri, (p) => {
    p.loop = true;
    p.timeUpdateEventInterval = 0.016;
    p.play();
  });

  useEffect(() => {
    if (!player || !videoUri || !result) return;
    const subscription = player.addListener('timeUpdate', (payload) => {
      if (result?.frames) {
        const currentTimeMs = payload.currentTime * 1000;
        const frame = result.frames.find(f => f.timestamp >= currentTimeMs);
        if (frame) setCurrentFrameData(frame.landmarks);
      }
    });
    return () => subscription.remove();
  }, [player, videoUri, result]);

  const handleUpload = async (uri) => {
    setLoading(true); setError(null); setProgress(0);
    abortControllerRef.current = new AbortController();
    const jobId = Math.random().toString(36).substring(7);
    const ws = new WebSocket(`wss://diamondmind-vg35.onrender.com/ws/progress/${jobId}`);
    ws.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data);
        if (data.progress) setProgress(data.progress);
      } catch (err) { console.error("WS Error", err); }
    };
    try {
      const data = await UploadService.uploadSwingVideo(uri, jobId, abortControllerRef.current.signal);
      if (data) setResult(data);
    } catch (err) {
      if (err.message !== 'canceled') setError("Analysis failed.");
    } finally {
      setLoading(false); ws.close();
    }
  };

  const pickVideo = async () => {
    let pickerResult = await ImagePicker.launchImageLibraryAsync({ mediaTypes: ['videos'], quality: 1 });
    if (pickerResult.canceled) return;
    const asset = pickerResult.assets[0];

    // Store video dimensions
    setVideoDimensions({ width: asset.width, height: asset.height });

    setVideoUri(asset.uri);
    player.replace(asset.uri);
    player.play();
    handleUpload(asset.uri);
  };

  const handleReset = () => {
    setResult(null); setVideoUri(null); setProgress(0);
    setCurrentFrameData(null); setIsFullscreen(false);
  };

  // Helper to get dynamic aspect ratio
  const videoRatio = player.src?.width ? player.src.width / player.src.height : 1.77;

  return (
    <SafeAreaProvider>
      {/* 1. FULLSCREEN LAYER */}
      {result && isFullscreen && (
        <View style={styles.fullscreenContainer}>
          <View
            style={styles.fullscreenVideoWrapper}
            onLayout={(e) => {
              const { width, height } = e.nativeEvent.layout;
              setFullscreenDimensions({ width, height });
            }}
          >
            <VideoView
              player={player}
              style={StyleSheet.absoluteFill}
              contentMode="contain"
            />
            <View style={StyleSheet.absoluteFill} pointerEvents="none">
              <SkeletonOverlay
                landmarks={currentFrameData}
                videoWidth={videoDimensions.width}
                videoHeight={videoDimensions.height}
                containerWidth={fullscreenDimensions.width}
                containerHeight={fullscreenDimensions.height}
              />
            </View>

            <TouchableOpacity
              style={[styles.modernExpandButton, { bottom: 60, right: 24, width: 50, height: 50, borderRadius: 25 }]}
              onPress={() => setIsFullscreen(false)}
            >
              <Minimize2 size={22} color="#FFF" />
            </TouchableOpacity>
          </View>
        </View>
      )}

      {/* 2. MAIN APP LAYER */}
      {!isFullscreen && (
        <SafeAreaView style={styles.container}>
          <View style={styles.header}>
            <Text style={styles.title}>DiamondMind</Text>
            <Text style={styles.subtitle}>Baseball Swing Analysis</Text>
          </View>

          {!loading && !result && (
            <TouchableOpacity style={styles.uploadCard} onPress={pickVideo}>
              <UploadCloud size={48} color="#007AFF" />
              <Text style={styles.uploadText}>Select Swing from Gallery</Text>
            </TouchableOpacity>
          )}

          {loading && (
            <View style={styles.statusCard}>
              <ActivityIndicator size="large" color="#007AFF" />
              <View style={styles.progressContainer}>
                <View style={[styles.progressBar, { width: `${progress}%` }]} />
              </View>
              <Text style={styles.progressText}>{progress}% Complete</Text>
            </View>
          )}

          {result && (
            <View style={styles.successCard}>
              {/* REPLACE THIS ENTIRE SECTION */}
              <View
                style={[styles.videoWrapper, { aspectRatio: videoRatio }]}
                onLayout={(e) => {
                  const { width, height } = e.nativeEvent.layout;
                  setContainerDimensions({ width, height });
                }}
              >
                <VideoView
                  player={player}
                  style={StyleSheet.absoluteFill}
                  contentMode="contain"
                />
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
                  style={[styles.modernExpandButton, { bottom: 10, right: 10, width: 40, height: 40, borderRadius: 20 }]}
                  onPress={() => setIsFullscreen(true)}
                >
                  <Maximize2 size={18} color="#FFF" />
                </TouchableOpacity>
              </View>
              {/* END REPLACEMENT */}

              <TouchableOpacity style={styles.resetButton} onPress={handleReset}>
                <Text style={styles.resetButtonText}>Analyze New Swing</Text>
              </TouchableOpacity>
            </View>
          )}

          {error && (
            <View style={styles.errorCard}>
              <AlertCircle size={24} color="#FF3B30" />
              <Text style={styles.errorText}>{error}</Text>
            </View>
          )}
        </SafeAreaView>
      )}
    </SafeAreaProvider>
  );
}