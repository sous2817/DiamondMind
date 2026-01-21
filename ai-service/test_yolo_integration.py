"""
Test YOLO v3 bat detection integration (DM-66)

This script tests the pose_engine with YOLO bat detection on videos from docs/test-videos.
"""
import os
import sys
from pose_engine import PoseExtractor

# Test videos directory
TEST_VIDEOS_DIR = r"C:\dm\docs\test-videos"

def test_yolo_loading():
    """Test that YOLO model loads successfully"""
    print("=" * 60)
    print("TEST 1: YOLO Model Loading")
    print("=" * 60)
    
    try:
        extractor = PoseExtractor()
        
        if extractor.bat_detector is not None:
            print("✅ YOLO model loaded successfully")
            print(f"   Confidence threshold: {extractor.bat_conf_threshold}")
            return True
        else:
            print("❌ YOLO model failed to load (bat_detector is None)")
            return False
    except Exception as e:
        print(f"❌ Error during model loading: {e}")
        return False

def test_video_processing(video_name="bat3.mp4"):
    """Test video processing with YOLO detection"""
    print("\n" + "=" * 60)
    print(f"TEST 2: Video Processing ({video_name})")
    print("=" * 60)
    
    video_path = os.path.join(TEST_VIDEOS_DIR, video_name)
    
    if not os.path.exists(video_path):
        print(f"❌ Test video not found: {video_path}")
        return False
    
    try:
        extractor = PoseExtractor()
        output_dir = os.path.join(TEST_VIDEOS_DIR, "v3_test_results")
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"📹 Processing: {video_name}")
        result = extractor.process_video(
            video_path=video_path,
            job_id="yolo_test",
            output_dir=output_dir
        )
        
        print("\n📊 Results:")
        print(f"   Total frames: {result['total_frames']}")
        print(f"   Frames processed: {result['frames_processed']}")
        print(f"   Frames with person: {result['frames_with_person']}")
        print(f"   FPS: {result['fps']:.2f}")
        print(f"   Frame skip: {result['frame_skip']}")
        
        # Count bat detections with confidence
        bat_detections = [f for f in result['frames'] if f['bat_position'] is not None]
        yolo_detections = [f for f in bat_detections if 'confidence' in f['bat_position']]
        geometric_detections = len(bat_detections) - len(yolo_detections)
        
        print(f"\n🏏 Bat Detections:")
        print(f"   Total: {len(bat_detections)} frames")
        print(f"   YOLO: {len(yolo_detections)} frames")
        print(f"   Geometric fallback: {geometric_detections} frames")
        
        if yolo_detections:
            avg_conf = sum(f['bat_position']['confidence'] for f in [f for f in result['frames'] 
                           if f['bat_position'] and 'confidence' in f['bat_position']]) / len(yolo_detections)
            print(f"   Average YOLO confidence: {avg_conf:.3f}")
            
            # Show sample detections
            print(f"\n   Sample YOLO Detections (first 5):")
            count = 0
            for f in result['frames']:
                if f['bat_position'] and 'confidence' in f['bat_position']:
                    pos = f['bat_position']
                    print(f"      Frame {result['frames'].index(f)}: "
                          f"({pos['x']:.3f}, {pos['y']:.3f}) conf={pos['confidence']:.3f}")
                    count += 1
                    if count >= 5:
                        break
        
        print(f"\n✅ Video processing complete!")
        print(f"   Output: {output_dir}/analyzed_yolo_test.mp4")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during video processing: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("\n🧪 YOLO v3 Integration Test (DM-66)\n")
    
    # Test 1: Model loading
    test1_passed = test_yolo_loading()
    
    # Test 2: Video processing
    test2_passed = test_video_processing("bat3.mp4")
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Model Loading:      {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"Video Processing:   {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 All tests passed! YOLO v3 integration successful.")
        return 0
    else:
        print("\n⚠️ Some tests failed. Check errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
