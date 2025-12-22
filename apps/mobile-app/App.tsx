import React, { useEffect, useState, useRef } from 'react';
import { StyleSheet, View, Text, ActivityIndicator, TouchableOpacity, Alert } from 'react-native';
import { Camera, useCameraDevice, useCameraPermission } from 'react-native-vision-camera';

// NOTE: Ensure this matches your specific emulator setup from the snapshot!
const DEV_URL = 'http://10.0.2.2:8000';

export default function App() {
  const { hasPermission, requestPermission } = useCameraPermission();
  const device = useCameraDevice('back');
  const camera = useRef<Camera>(null); // Reference to the camera component
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    if (!hasPermission) requestPermission();
  }, [hasPermission]);

  // Function to take photo and upload
  const handleCapture = async () => {
    if (!camera.current) return;

    try {
      setUploading(true);

      // 1. Snap the photo
      const photo = await camera.current.takePhoto({
        flash: 'off',
        enableShutterSound: true
      });

      // 2. Prepare the file for upload
      const formData = new FormData();
      formData.append('file', {
        uri: 'file://' + photo.path,
        type: 'image/jpeg',
        name: 'vision_capture.jpg',
      } as any);

      // 3. Send to Python Backend
      const response = await fetch(`${DEV_URL}/analyze`, {
        method: 'POST',
        body: formData,
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      const result = await response.json();
      Alert.alert("Brain Response", `✅ ${result.message}`);

    } catch (error) {
      Alert.alert("Error", "Failed to send image to brain.");
      console.error(error);
    } finally {
      setUploading(false);
    }
  };

  if (!hasPermission || device == null) return <ActivityIndicator size="large" />;

  return (
    <View style={styles.container}>
      <Camera
        ref={camera}
        style={StyleSheet.absoluteFill}
        device={device}
        isActive={true}
        photo={true} // <--- Enable Photo Capture
      />

      {/* Capture Button */}
      <View style={styles.bottomBar}>
        <TouchableOpacity
          style={styles.captureBtn}
          onPress={handleCapture}
          disabled={uploading}
        >
          {uploading ? (
            <ActivityIndicator color="black" />
          ) : (
            <View style={styles.captureInner} />
          )}
        </TouchableOpacity>
        <Text style={styles.hint}>Tap to Analyze</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: 'black' },
  bottomBar: {
    position: 'absolute',
    bottom: 50,
    width: '100%',
    alignItems: 'center',
  },
  captureBtn: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: 'white',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 10,
  },
  captureInner: {
    width: 70,
    height: 70,
    borderRadius: 35,
    backgroundColor: 'white',
    borderWidth: 2,
    borderColor: 'black',
  },
  hint: { color: 'white', fontWeight: '600' }
});