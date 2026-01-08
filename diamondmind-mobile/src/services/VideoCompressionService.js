import { Video } from 'react-native-compressor';
import * as FileSystem from 'expo-file-system';

export class VideoCompressionService {
    /**
     * Compress video to 720p with 2.5 Mbps bitrate
     * @param {string} sourceUri - Original video URI
     * @param {function} onProgress - Progress callback (0-100)
     * @returns {Promise<string>} - Compressed video URI
     */
    static async compressVideo(sourceUri, onProgress = () => { }) {
        try {
            console.log('🎬 Starting video compression:', sourceUri);

            // Get file info
            const fileInfo = await FileSystem.getInfoAsync(sourceUri);
            const fileSizeMB = fileInfo.size / (1024 * 1024);

            console.log(`📊 Original file size: ${fileSizeMB.toFixed(2)} MB`);

            // Skip compression if already small
            if (fileSizeMB < 10) {
                console.log('✅ File already small, skipping compression');
                return sourceUri;
            }

            // Check available storage
            const freeSpace = await FileSystem.getFreeDiskStorageAsync();
            const requiredSpace = fileInfo.size * 0.5; // Assume 50% of original

            if (freeSpace < requiredSpace) {
                console.warn('⚠️ Low storage space, skipping compression');
                return sourceUri;
            }

            // Compress to 720p
            const compressedUri = await Video.compress(
                sourceUri,
                {
                    compressionMethod: 'manual',
                    maxSize: 1280, // 720p width (maintains aspect ratio)
                    bitrate: 2500000, // 2.5 Mbps
                },
                (progress) => {
                    onProgress(Math.round(progress * 100));
                }
            );

            // Get compressed file info
            const compressedInfo = await FileSystem.getInfoAsync(compressedUri);
            const compressedSizeMB = compressedInfo.size / (1024 * 1024);

            console.log(`✅ Compressed to: ${compressedSizeMB.toFixed(2)} MB`);
            console.log(`📉 Reduction: ${((1 - compressedSizeMB / fileSizeMB) * 100).toFixed(1)}%`);

            return compressedUri;

        } catch (error) {
            console.error('❌ Compression failed:', error);

            // Fallback: return original if compression fails
            console.log('⚠️ Using original file as fallback');
            return sourceUri;
        }
    }

    /**
     * Clean up temporary compressed files
     */
    static async cleanupTempFiles() {
        try {
            const cacheDir = FileSystem.cacheDirectory;
            const files = await FileSystem.readDirectoryAsync(cacheDir);

            // Delete old compressed videos (older than 1 hour)
            const oneHourAgo = Date.now() - (60 * 60 * 1000);

            for (const file of files) {
                if (file.startsWith('compressed_')) {
                    const filePath = `${cacheDir}${file}`;
                    const info = await FileSystem.getInfoAsync(filePath);

                    if (info.modificationTime * 1000 < oneHourAgo) {
                        await FileSystem.deleteAsync(filePath, { idempotent: true });
                        console.log('🗑️ Cleaned up old compressed file:', file);
                    }
                }
            }
        } catch (error) {
            console.error('⚠️ Cleanup failed:', error);
            // Non-critical, don't throw
        }
    }
}
