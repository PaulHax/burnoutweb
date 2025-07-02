#!/usr/bin/env python3
"""
Quick Test for Phase 1b Service Architecture
Tests service with limited frames to validate functionality quickly.
"""

import sys
import asyncio
import time
sys.path.append('/home/paulhax/src/tele-stuff/burnoutweb/app')

async def test_quick_detection():
    """Test detection with limited frames for quick validation."""
    print("=== Quick Detection Test (5 frames) ===")
    
    try:
        from burn_out.app.features.track_features_service import FeatureTrackingService
        from burn_out.app.features.config import ORBDetectorConfig
        
        video_path = "/home/paulhax/src/tele-stuff/videos/09172008flight1tape3_2.mpg"
        
        progress_updates = []
        result_data = None
        
        def progress_handler(data):
            progress_updates.append(data)
            status = data.get('status', 'unknown')
            message = data.get('message', '')
            print(f"  {status}: {message}")
        
        def completion_handler(data):
            nonlocal result_data
            result_data = data
        
        service = FeatureTrackingService(
            progress_callback=progress_handler,
            completion_callback=completion_handler
        )
        
        # Use fast preset with limited frames
        config_params = ORBDetectorConfig.get_fast_preset()
        
        # Monkey-patch to limit frames for quick test
        import burn_out.app.features.track_features_service as service_module
        original_sample = service_module._sample_frames
        
        def limited_sample_frames(video_reader, max_frames=500):
            return list(range(1, 6))  # Only 5 frames
        
        service_module._sample_frames = limited_sample_frames
        
        try:
            service.detect_features(video_path, config_params)
            print("✓ Detection started")
            
            # Wait for completion with shorter timeout
            timeout = 30
            start_time = time.time()
            
            while result_data is None and (time.time() - start_time) < timeout:
                await asyncio.sleep(0.5)
            
            if result_data and result_data.get('success'):
                summary = result_data.get('summary', {})
                frames = summary.get('total_frames_processed', 0)
                features = summary.get('total_features_detected', 0)
                avg = summary.get('average_features_per_frame', 0)
                
                print(f"✅ SUCCESS: {frames} frames, {features} features, {avg:.1f} avg")
                print(f"✓ Progress updates: {len(progress_updates)}")
                return True
            else:
                error = result_data.get('error') if result_data else 'Timeout'
                print(f"✗ Failed: {error}")
                return False
                
        finally:
            service_module._sample_frames = original_sample
            service.close()
        
    except Exception as e:
        print(f"✗ Quick detection test failed: {e}")
        return False

async def main():
    """Run quick service validation."""
    print("🚀 PHASE 1B: QUICK SERVICE VALIDATION")
    print("=" * 40)
    
    success = await test_quick_detection()
    
    if success:
        print("\n✅ PHASE 1B SERVICE ARCHITECTURE: VALIDATED")
        print("Ready to proceed with Phase 2a implementation")
    else:
        print("\n❌ PHASE 1B SERVICE ARCHITECTURE: NEEDS FIXES")
    
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)