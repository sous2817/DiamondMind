import React, { useState, useRef, useEffect } from 'react';
import { StyleSheet, Text, View, TouchableOpacity, ActivityIndicator, LogBox } from 'react-native';
import { SafeAreaProvider, SafeAreaView } from 'react-native-safe-area-context';
import * as ImagePicker from 'expo-image-picker';
import { UploadCloud, Maximize2, Minimize2, AlertCircle, XCircle, Download } from 'lucide-react-native';
import { useVideoPlayer, VideoView } from 'expo-video';
import UploadService from './src/services/UploadService.js';
import SkeletonOverlay from './src/components/SkeletonOverlay';
import { captureRef } from 'react-native-view-shot';
import * as Sharing from 'expo-sharing';
import * as FileSystem from 'expo-file-system';
import { Config } from './src/config.js';

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
  cancelButton: { flexDirection: 'row', alignItems: 'center', marginTop: 15, paddingVertical: 10, paddingHorizontal: 20, backgroundColor: '#FFF5F5', borderRadius: 10, borderWidth: 1, borderColor: '#FF3B30' },
  cancelButtonText: { color: '#FF3B30', fontWeight: '700', marginLeft: 8 },
  videoWrapper: { width: '100%', backgroundColor: '#000', borderRadius: 15, overflow: 'hidden', position: 'relative' },
  resetButton: { marginTop: 20, backgroundColor: '#007AFF', padding: 15, borderRadius: 12, alignItems: 'center' },
  resetButtonText: { color: '#FFF', fontWeight: '700' },
  fullscreenContainer: { position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: '#000', zIndex: 1000 },
  fullscreenVideoWrapper: { flex: 1, width: '100%', height: '100%', justifyContent: 'center', alignItems: 'center' },
  modernExpandButton: { position: 'absolute', backgroundColor: 'rgba(28, 28, 30, 0.8)', alignItems: 'center', justifyContent: 'center', zIndex: 1001 },
  errorCard: { backgroundColor: '#FFF', borderRadius: 20, padding: 20, alignItems: 'center' },
  errorText: { color: '#1C1C1E', fontWeight: '600', marginVertical: 10 },
  retryButton: { backgroundColor: '#F2F2F7', padding: 10, borderRadius: 8 },
  retryText: { color: '#007AFF', fontWeight: '700' },
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

  const player = useVideoPlayer(videoUri, (p) => {
    p.loop = true;
    p.timeUpdateEventInterval = 0.016;
    p.play();
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
      // The fix: result.frames logic now matches the data wrapper below
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

    // 🔧 FIX: Use the correct backend URL (changed from diamondmind-vg35)
    const ws = new WebSocket(`${Config.WS_BASE_URL}/ws/progress/${jobId}`);

    console.log(`📡 WebSocket connecting to job: ${jobId}`);

    ws.onmessage = (e) => {
      const data = JSON.parse(e.data);
      console.log(`📊 Progress update: ${data.progress}%`);
      if (data.progress) setProgress(data.progress);
    };

    ws.onerror = (err) => {
      console.error("❌ WebSocket Error:", err);
    };

    ws.onopen = () => {
      console.log("✅ WebSocket connected");
    };

    try {
      const data = await UploadService.uploadSwingVideo(uri, jobId, abortControllerRef.current.signal);
      console.log("✅ Analysis complete:", {
        totalFrames: data?.frames?.length,
        framesWithPerson: data?.frames_with_person,
        firstFrame: data?.frames?.[0]
      });
      if (data) setResult(data);
    } catch (err) {
      console.error("❌ UPLOAD FAILED:", err);
      if (err.response) {
        console.error("❌ SERVER DATA:", err.response.data);
        console.error("❌ STATUS CODE:", err.response.status);
      }

      if (err.message !== 'canceled') {
        const msg = err.response?.data?.detail || err.message || "Analysis failed.";
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
    setVideoDimensions({ width: asset.width, height: asset.height });
    setSelectedFile(asset.fileName || "swing.mp4");
    setVideoUri(asset.uri);
    player.replace(asset.uri);
    player.play();
    handleUpload(asset.uri);
  };

  const handleReset = () => {
    setResult(null); setVideoUri(null); setProgress(0);
    setCurrentFrameData(null); setIsFullscreen(false);
  };

  const videoRatio = player.src?.width ? player.src.width / player.src.height : 1.77;

  return (
    <SafeAreaProvider>
      {result && isFullscreen && (
        <View style={styles.fullscreenContainer}>
          <View style={styles.fullscreenVideoWrapper} onLayout={(e) => setFullscreenDimensions(e.nativeEvent.layout)}>
            <VideoView player={player} style={StyleSheet.absoluteFill} contentMode="contain" />
            <View style={StyleSheet.absoluteFill} pointerEvents="none">
              <SkeletonOverlay landmarks={currentFrameData} videoWidth={videoDimensions.width} videoHeight={videoDimensions.height} containerWidth={fullscreenDimensions.width} containerHeight={fullscreenDimensions.height} />
            </View>
            <TouchableOpacity style={[styles.modernExpandButton, { bottom: 60, right: 24, width: 50, height: 50, borderRadius: 25 }]} onPress={() => setIsFullscreen(false)}>
              <Minimize2 size={22} color="#FFF" />
            </TouchableOpacity>
          </View>
        </View>
      )}

      {error && (
        <View style={styles.errorCard}>
          <AlertCircle size={48} color="#FF3B30" />
          <Text style={styles.errorText}>{error}</Text>
          <TouchableOpacity style={styles.retryButton} onPress={() => setError(null)}>
            <Text style={styles.retryText}>Try Again</Text>
          </TouchableOpacity>
        </View>
      )}

      {!loading && !result && !error && (
        <View />
      )}

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
              <Text style={styles.loadingText}>Analyzing: {selectedFile}</Text>
              <View style={styles.progressContainer}><View style={[styles.progressBar, { width: `${progress}%` }]} /></View>
              <TouchableOpacity style={styles.cancelButton} onPress={() => { abortControllerRef.current?.abort(); setLoading(false); }}>
                <XCircle size={20} color="#FF3B30" /><Text style={styles.cancelButtonText}>Cancel Upload</Text>
              </TouchableOpacity>
            </View>
          )}

          {result && (
            <View style={styles.successCard}>
              <View ref={viewShotRef} style={[styles.videoWrapper, { aspectRatio: videoRatio }]} onLayout={(e) => setContainerDimensions(e.nativeEvent.layout)}>
                <VideoView player={player} style={StyleSheet.absoluteFill} contentMode="contain" />
                <View style={StyleSheet.absoluteFill} pointerEvents="none">
                  <SkeletonOverlay landmarks={currentFrameData} videoWidth={videoDimensions.width} videoHeight={videoDimensions.height} containerWidth={containerDimensions.width} containerHeight={containerDimensions.height} />
                </View>
                <TouchableOpacity style={[styles.modernExpandButton, { bottom: 10, right: 10, width: 40, height: 40, borderRadius: 20 }]} onPress={() => setIsFullscreen(true)}>
                  <Maximize2 size={18} color="#FFF" />
                </TouchableOpacity>
              </View>

              <View style={{ flexDirection: 'row', justifyContent: 'space-between', marginTop: 15 }}>
                <TouchableOpacity style={[styles.resetButton, { flex: 1, marginTop: 0, marginRight: 10, backgroundColor: '#E5E5EA' }]} onPress={handleReset}>
                  <Text style={[styles.resetButtonText, { color: '#1C1C1E' }]}>New Swing</Text>
                </TouchableOpacity>
                <TouchableOpacity style={[styles.resetButton, { flex: 1, marginTop: 0, backgroundColor: isExporting ? '#8E8E93' : '#007AFF' }]} onPress={handleExport} disabled={isExporting}>
                  {isExporting ? <ActivityIndicator color="#FFF" /> : <><Download size={20} color="#FFF" style={{ marginRight: 8 }} /><Text style={styles.resetButtonText}>Download</Text></>}
                </TouchableOpacity>
              </View>
            </View>
          )}
        </SafeAreaView>
      )}
    </SafeAreaProvider>
  );
}