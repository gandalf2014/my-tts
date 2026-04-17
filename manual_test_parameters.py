#!/usr/bin/env python3
"""
Manual parameter verification script for SSML controls.
Tests extreme parameter values and verifies parameter conversion.
"""

import asyncio
import sys
import os
import tempfile
import logging
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.tts.generator import TTSGenerator, TTSOptions, create_tts_options

# Configure logging to show parameter conversions
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def verify_parameter_conversion():
    """Verify parameter conversion logic with boundary values."""
    print("\n" + "="*60)
    print("PARAMETER CONVERSION VERIFICATION")
    print("="*60)
    
    test_cases = [
        # (name, options, expected)
        ("Default values", create_tts_options(1.0, 1.0, 100.0), 
         {'rate': '+0%', 'pitch': '+0Hz', 'volume': '+0%'}),
        ("Extreme speed max", create_tts_options(2.0, 1.0, 100.0), 
         {'rate': '+100%', 'pitch': '+0Hz', 'volume': '+0%'}),
        ("Extreme speed min", create_tts_options(0.5, 1.0, 100.0), 
         {'rate': '-50%', 'pitch': '+0Hz', 'volume': '+0%'}),
        ("Extreme pitch max", create_tts_options(1.0, 2.0, 100.0), 
         {'rate': '+0%', 'pitch': '+100Hz', 'volume': '+0%'}),
        ("Extreme pitch min", create_tts_options(1.0, 0.5, 100.0), 
         {'rate': '+0%', 'pitch': '-50Hz', 'volume': '+0%'}),
        ("Extreme volume min", create_tts_options(1.0, 1.0, 0.0), 
         {'rate': '+0%', 'pitch': '+0Hz', 'volume': '-100%'}),
        ("All extremes max", create_tts_options(2.0, 2.0, 100.0), 
         {'rate': '+100%', 'pitch': '+100Hz', 'volume': '+0%'}),
        ("All extremes min", create_tts_options(0.5, 0.5, 0.0), 
         {'rate': '-50%', 'pitch': '-50Hz', 'volume': '-100%'}),
    ]
    
    all_passed = True
    for name, options, expected in test_cases:
        result = TTSGenerator._convert_options_to_edge_tts(options)
        passed = result == expected
        status = "[PASS]" if passed else "[FAIL]"
        
        print(f"\n{name}:")
        print(f"  Input:    speed={options.speed}, pitch={options.pitch}, volume={options.volume}")
        print(f"  Expected: {expected}")
        print(f"  Got:      {result}")
        print(f"  {status}")
        
        if not passed:
            all_passed = False
    
    return all_passed


async def generate_test_audio():
    """Generate audio files with extreme parameter values for manual review."""
    print("\n" + "="*60)
    print("AUDIO GENERATION TEST")
    print("="*60)
    
    generator = TTSGenerator()
    test_text = "这是一个参数测试。语速、音调、音量都已设置为极值。"
    voice_name = "zh-CN-XiaoxiaoNeural"  # Common Chinese voice
    
    test_configs = [
        ("normal", create_tts_options(1.0, 1.0, 100.0)),
        ("fast_high_pitch", create_tts_options(2.0, 2.0, 100.0)),
        ("slow_low_pitch", create_tts_options(0.5, 0.5, 100.0)),
        ("quiet", create_tts_options(1.0, 1.0, 0.0)),
    ]
    
    results = []
    
    for config_name, options in test_configs:
        print(f"\nGenerating audio with config: {config_name}")
        print(f"  Options: speed={options.speed}, pitch={options.pitch}, volume={options.volume}")
        
        try:
            # Create output file in temp directory
            output_dir = Path(tempfile.gettempdir()) / "tts_param_test"
            output_dir.mkdir(exist_ok=True)
            output_path = output_dir / f"{config_name}.mp3"
            
            # Generate audio
            converted = TTSGenerator._convert_options_to_edge_tts(options)
            print(f"  Converted: rate={converted['rate']}, pitch={converted['pitch']}, volume={converted['volume']}")
            
            result_path = await generator.generate_async(
                text=test_text,
                voice_name=voice_name,
                options=options,
                output_path=str(output_path)
            )
            
            file_size = os.path.getsize(result_path)
            print(f"  Generated: {result_path} ({file_size} bytes)")
            results.append((config_name, result_path, file_size, True))
            
        except Exception as e:
            print(f"  [ERROR] Error: {e}")
            results.append((config_name, None, 0, False))
    
    return results


def main():
    """Run verification tests."""
    print("SSML Parameter Verification Test")
    print("="*60)
    
    # Step 1: Verify parameter conversion logic
    conversion_passed = verify_parameter_conversion()
    
    # Step 2: Generate test audio files
    print("\n")
    try:
        results = asyncio.run(generate_test_audio())
    except Exception as e:
        logger.error(f"Audio generation failed: {e}")
        results = []
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    print(f"\nParameter Conversion: {'[PASSED]' if conversion_passed else '[FAILED]'}")
    
    if results:
        print("\nAudio Generation Results:")
        for config_name, path, size, success in results:
            status = "[OK]" if success else "[FAIL]"
            if path:
                print(f"  {status} {config_name}: {path} ({size} bytes)")
            else:
                print(f"  {status} {config_name}: FAILED")
    
    # Overall verdict
    audio_success = all(r[3] for r in results) if results else False
    
    if conversion_passed:
        print("\n[OK] VERIFICATION PASSED")
        print("Parameter conversion is correctly implemented.")
        print("UI sliders (speed 0.5x-2x, pitch 0.5-2.0, volume 0-100%)")
        print("are correctly converted to edge-tts format.")
        return 0
    else:
        print("\n[FAIL] VERIFICATION FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
