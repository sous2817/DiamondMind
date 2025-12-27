import React, { useState, useRef, useEffect } from 'react';
import { StyleSheet, Text, View, TouchableOpacity, ActivityIndicator } from 'react-native';
import { SafeAreaProvider, SafeAreaView } from 'react-native-safe-area-context';
import * as ImagePicker from 'expo-image-picker';
import { CheckCircle2, AlertCircle, UploadCloud, XCircle } from 'lucide-react-native';
import UploadService from './src/services/UploadService.js';
import SkeletonOverlay from './src/components/SkeletonOverlay';
import { useVideoPlayer, VideoView } from 'expo-video';

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

  const player = useVideoPlayer(videoUri, (player) => {
    player.loop = true;
    player.play();
  });

  useEffect(() => {
    // If we don't have a URI or results yet, don't attach listener
    if (!videoUri || !result) return;

    console.log("Attaching listener to player for URI:", videoUri);

    const subscription = player.addListener('timeUpdate', (payload) => {
      // Force capture naturalSize if it's missing
      if (!naturalSize && player.src?.width) {
        setNaturalSize({ width: player.src.width, height: player.src.height });
      }

      if (result?.frames) {
        const currentTimeMs = payload.currentTime * 1000;
        // DEBUG LOG: This will show in your terminal if the listener is alive
        console.log(`Clock: ${currentTimeMs.toFixed(0)}ms`);

        const frame = result.frames.find(f => f.timestamp >= currentTimeMs);
        if (frame) {
          setCurrentFrameData(frame.landmarks);
        }
      }
    });

    return () => subscription.remove();
  }, [player, videoUri, result]);

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
      } catch (err) {
        console.error("WS Message Error:", err);
      }
    };

    try {
      const data = await UploadService.uploadSwingVideo(
        uri,
        jobId,
        abortControllerRef.current.signal
      );
      if (data) setResult(data);
    } catch (err) {
      if (err.message !== 'canceled') {
        setError("Analysis failed or timed out.");
      }
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
    setLoading(false);
  };

  const cancelAnalysis = () => {
    if (abortControllerRef.current) abortControllerRef.current.abort();
    handleReset();
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
            <Text style={styles.uploadSubtext}>Max 50MB • MP4 or MOV</Text>
          </TouchableOpacity>
        )}

        {loading && (
          <View style={styles.statusCard}>
            <ActivityIndicator size="large" color="#007AFF" />
            <Text style={styles.loadingText}>Analyzing: {selectedFile}</Text>
            <View style={styles.progressContainer}>
              <View style={[styles.progressBar, { width: `${progress}%` }]} />
            </View>
            <Text style={styles.progressText}>{progress}% Complete</Text>
            <Text style={styles.waitingText}>Our AI is mapping 33 body points...</Text>
            <TouchableOpacity style={styles.cancelButton} onPress={cancelAnalysis}>
              <XCircle size={20} color="#FF3B30" />
              <Text style={styles.cancelButtonText}>Cancel Analysis</Text>
            </TouchableOpacity>
          </View>
        )}

        {result && (
          <View style={styles.successCard}>
            <View style={styles.row}>
              <CheckCircle2 size={24} color="#34C759" />
              <Text style={styles.successTitle}>Swing Analysis Ready</Text>
            </View>

            <View
              style={styles.videoWrapper}
              onLayout={(e) => setVideoLayout(e.nativeEvent.layout)}
            >
              <VideoView
                player={player}
                style={styles.videoPlayer}
                contentMode="contain"
                fullscreenOptions={{ canEnterFullscreen: true }}
                onLoad={(event) => {
                  if (event.source?.width) {
                    setNaturalSize({ width: event.source.width, height: event.source.height });
                  }
                }}
              />
              <SkeletonOverlay
                landmarks={currentFrameData}
                width={videoLayout.width}
                height={videoLayout.height}
                // Fallback: If naturalSize is null, use the layout size so it at least draws SOMETHING
                naturalSize={naturalSize || { width: videoLayout.width, height: videoLayout.height }}
              />
            </View>

            <TouchableOpacity style={styles.resetButton} onPress={handleReset}>
              <Text style={styles.resetButtonText}>Analyze New Swing</Text>
            </TouchableOpacity>
          </View>
        )}

        {error && (
          <View style={styles.errorCard}>
            <AlertCircle size={24} color="#FF3B30" />
            <Text style={styles.errorText}>{error}</Text>
            <TouchableOpacity style={styles.retryButton} onPress={pickVideo}>
              <Text style={styles.retryText}>Try Again</Text>
            </TouchableOpacity>
          </View>
        )}
      </SafeAreaView>
    </SafeAreaProvider>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F2F2F7', padding: 20 },
  header: { alignItems: 'center', marginTop: 20, marginBottom: 40 },
  title: { fontSize: 32, fontWeight: '900', color: '#1C1C1E', letterSpacing: -1 },
  subtitle: { fontSize: 16, color: '#8E8E93', fontWeight: '500' },
  uploadCard: { backgroundColor: '#FFF', borderRadius: 20, padding: 40, alignItems: 'center', borderStyle: 'dashed', borderWidth: 2, borderColor: '#007AFF' },
  uploadText: { marginTop: 15, fontSize: 18, fontWeight: '600', color: '#1C1C1E' },
  uploadSubtext: { marginTop: 5, fontSize: 14, color: '#8E8E93' },
  statusCard: { backgroundColor: '#FFF', borderRadius: 20, padding: 30, alignItems: 'center', elevation: 5, shadowColor: '#000', shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.1, shadowRadius: 10 },
  loadingText: { marginTop: 20, fontSize: 16, fontWeight: '700', textAlign: 'center', marginBottom: 15 },
  progressContainer: { width: '100%', height: 10, backgroundColor: '#E5E5EA', borderRadius: 5, overflow: 'hidden', marginBottom: 10 },
  progressBar: { height: '100%', backgroundColor: '#007AFF' },
  progressText: { fontSize: 14, fontWeight: '600', color: '#007AFF', marginBottom: 10 },
  waitingText: { marginTop: 8, fontSize: 14, color: '#8E8E93', marginBottom: 10 },
  cancelButton: { flexDirection: 'row', alignItems: 'center', marginTop: 15, padding: 10, backgroundColor: '#FFF5F5', borderRadius: 8, borderWidth: 1, borderColor: '#FFE5E5' },
  cancelButtonText: { color: '#FF3B30', fontWeight: '600', marginLeft: 8 },
  successCard: { backgroundColor: '#FFF', borderRadius: 20, padding: 20, width: '100%' },
  row: { flexDirection: 'row', alignItems: 'center', marginBottom: 10 },
  successTitle: { fontSize: 18, fontWeight: '700', color: '#34C759', marginLeft: 8 },
  resetButton: { marginTop: 20, backgroundColor: '#007AFF', padding: 15, borderRadius: 12, alignItems: 'center' },
  resetButtonText: { color: '#FFF', fontWeight: '700' },
  errorCard: { backgroundColor: '#FFF', borderRadius: 20, padding: 20, alignItems: 'center', borderLeftWidth: 5, borderLeftColor: '#FF3B30' },
  errorText: { color: '#1C1C1E', fontWeight: '600', marginVertical: 10 },
  retryButton: { backgroundColor: '#F2F2F7', padding: 10, borderRadius: 8 },
  retryText: { color: '#007AFF', fontWeight: '700' },
  videoWrapper: {
    width: '100%',
    aspectRatio: 16 / 9,
    backgroundColor: '#000',
    borderRadius: 15,
    overflow: 'hidden',
    position: 'relative',
    marginTop: 10,
  },
  videoPlayer: { flex: 1 },
});