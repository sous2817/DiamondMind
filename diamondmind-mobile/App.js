import React, { useState, useRef, useEffect } from 'react';
import { StyleSheet, Text, View, TouchableOpacity, ActivityIndicator, LogBox } from 'react-native';
import { SafeAreaProvider, SafeAreaView } from 'react-native-safe-area-context';
import * as ImagePicker from 'expo-image-picker';
import { CheckCircle2, AlertCircle, UploadCloud, XCircle, Maximize2, Minimize2 } from 'lucide-react-native';
import { useVideoPlayer, VideoView } from 'expo-video';
import UploadService from './src/services/UploadService.js';
import SkeletonOverlay from './src/components/SkeletonOverlay';

export default function App() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const [progress, setProgress] = useState(0);
  const abortControllerRef = useRef(null);
  const [currentFrameData, setCurrentFrameData] = useState(null);
  const [videoUri, setVideoUri] = useState(null);
  const [videoLayout, setVideoLayout] = useState({ width: 0, height: 0 });
  const [naturalSize, setNaturalSize] = useState(null);
  const [isFullscreen, setIsFullscreen] = useState(false);

  // 1. Hook correctly placed at the top level
  const player = useVideoPlayer(videoUri, (p) => {
    p.loop = true;
    p.timeUpdateEventInterval = 0.016; // Your 60fps fix
    p.play();
  });

  // 2. Corrected useEffect with Guard Clause
  useEffect(() => {
    if (!player || !videoUri || !result) return;

    const subscription = player.addListener('timeUpdate', (payload) => {
      // Sync naturalSize for skeleton math
      if (!naturalSize && player.src?.width) {
        setNaturalSize({ width: player.src.width, height: player.src.height });
      }

      if (result?.frames) {
        const currentTimeMs = payload.currentTime * 1000;
        const frame = result.frames.find(f => f.timestamp >= currentTimeMs);
        if (frame) {
          setCurrentFrameData(frame.landmarks);
        }
      }
    });

    return () => subscription.remove();
  }, [player, videoUri, result, naturalSize]);

  const pickVideo = async () => {
    let pickerResult = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ['videos'],
      allowsEditing: true,
      quality: 1,
    });

    if (pickerResult.canceled) return;

    const asset = pickerResult.assets[0];
    setSelectedFile(asset.fileName || "swing_video.mp4");
    setVideoUri(asset.uri);

    // 3. Imperative update for the new engine
    player.replace(asset.uri);
    player.play();

    handleUpload(asset.uri);
  };

  const handleUpload = async (uri) => {
    setLoading(true);
    setError(null);
    setProgress(0);
    abortControllerRef.current = new AbortController();
    const jobId = Math.random().toString(36).substring(7);
    const ws = new WebSocket(`wss://diamondmind-vg35.onrender.com/ws/progress/${jobId}`);

    ws.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data);
        if (data.progress) setProgress(data.progress);
      } catch (err) { console.error("WS Message Error:", err); }
    };

    try {
      const data = await UploadService.uploadSwingVideo(uri, jobId, abortControllerRef.current.signal);
      if (data) setResult(data);
    } catch (err) {
      if (err.message !== 'canceled') setError("Analysis failed or timed out.");
    } finally {
      setLoading(false);
      ws.close();
    }
  };

  const handleReset = () => {
    setResult(null);
    setSelectedFile(null);
    setProgress(0);
    setCurrentFrameData(null);
    setVideoUri(null);
    setVideoLayout({ width: 0, height: 0 });
    setNaturalSize(null);
    setIsFullscreen(false);
  };

  return (
    <SafeAreaProvider>
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
            <Text style={styles.loadingText}>Analyzing: {selectedFile}</Text>
            <View style={styles.progressContainer}><View style={[styles.progressBar, { width: `${progress}%` }]} /></View>
            <Text style={styles.progressText}>{progress}% Complete</Text>
            <TouchableOpacity style={styles.cancelButton} onPress={() => abortControllerRef.current?.abort()}>
              <XCircle size={20} color="#FF3B30" /><Text style={styles.cancelButtonText}>Cancel</Text>
            </TouchableOpacity>
          </View>
        )}

        {result && (
          <View style={isFullscreen ? styles.fullscreenContainer : styles.successCard}>
            {isFullscreen && <SafeAreaView style={{ flex: 0, backgroundColor: '#000' }} />}
            <View
              style={isFullscreen ? styles.fullscreenVideoWrapper : styles.videoWrapper}
              onLayout={(e) => setVideoLayout(e.nativeEvent.layout)}
            >
              <VideoView
                player={player}
                style={styles.videoPlayer}
                contentMode="contain"
                onLoad={(event) => {
                  if (event.source?.width) setNaturalSize({ width: event.source.width, height: event.source.height });
                }}
              />
              <SkeletonOverlay
                landmarks={currentFrameData}
                width={videoLayout.width}
                height={videoLayout.height}
                naturalSize={naturalSize || { width: videoLayout.width, height: videoLayout.height }}
              />
              <TouchableOpacity
                style={[styles.modernExpandButton, { bottom: isFullscreen ? 60 : 24 }]}
                onPress={() => setIsFullscreen(!isFullscreen)}
              >
                {isFullscreen ? <Minimize2 size={22} color="#FFF" /> : <Maximize2 size={22} color="#FFF" />}
              </TouchableOpacity>
            </View>
            {!isFullscreen && (
              <TouchableOpacity style={styles.resetButton} onPress={handleReset}>
                <Text style={styles.resetButtonText}>Analyze New Swing</Text>
              </TouchableOpacity>
            )}
          </View>
        )}

        {error && (
          <View style={styles.errorCard}>
            <AlertCircle size={24} color="#FF3B30" /><Text style={styles.errorText}>{error}</Text>
            <TouchableOpacity style={styles.retryButton} onPress={pickVideo}><Text style={styles.retryText}>Try Again</Text></TouchableOpacity>
          </View>
        )}
      </SafeAreaView>
    </SafeAreaProvider>
  );
}

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
  cancelButton: { flexDirection: 'row', alignItems: 'center', marginTop: 15, padding: 10, backgroundColor: '#FFF5F5', borderRadius: 8 },
  cancelButtonText: { color: '#FF3B30', fontWeight: '600', marginLeft: 8 },
  successCard: { backgroundColor: '#FFF', borderRadius: 20, padding: 20 },
  videoWrapper: { width: '100%', aspectRatio: 16 / 9, backgroundColor: '#000', borderRadius: 15, overflow: 'hidden', position: 'relative' },
  videoPlayer: { flex: 1 },
  resetButton: { marginTop: 20, backgroundColor: '#007AFF', padding: 15, borderRadius: 12, alignItems: 'center' },
  resetButtonText: { color: '#FFF', fontWeight: '700' },
  fullscreenContainer: { ...StyleSheet.absoluteFillObject, backgroundColor: '#000', zIndex: 1000 },
  fullscreenVideoWrapper: { flex: 1, width: '100%', height: '100%', justifyContent: 'center' },
  modernExpandButton: { position: 'absolute', right: 20, backgroundColor: 'rgba(28, 28, 30, 0.8)', width: 50, height: 50, borderRadius: 25, alignItems: 'center', justifyContent: 'center', zIndex: 1001 },
  errorCard: { backgroundColor: '#FFF', borderRadius: 20, padding: 20, alignItems: 'center' },
  errorText: { color: '#1C1C1E', fontWeight: '600', marginVertical: 10 },
  retryButton: { backgroundColor: '#F2F2F7', padding: 10, borderRadius: 8 },
  retryText: { color: '#007AFF', fontWeight: '700' },
});