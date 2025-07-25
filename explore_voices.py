#!/usr/bin/env python3
"""
Script to explore available voices in edge-tts
"""
import asyncio
import edge_tts

async def list_voices():
    """List all available voices"""
    voices = await edge_tts.list_voices()
    
    print(f"Total voices available: {len(voices)}")
    print("\nVoice details:")
    print("-" * 80)
    
    # Group voices by language
    voices_by_lang = {}
    for voice in voices:
        lang = voice['Locale']
        if lang not in voices_by_lang:
            voices_by_lang[lang] = []
        voices_by_lang[lang].append(voice)
    
    # Display voices grouped by language
    for lang, lang_voices in sorted(voices_by_lang.items()):
        print(f"\n{lang} ({len(lang_voices)} voices):")
        for voice in lang_voices:
            print(f"  - {voice['FriendlyName']} ({voice['Gender']})")
            print(f"    Short Name: {voice['ShortName']}")
            print(f"    Locale: {voice['Locale']}")
            print()

if __name__ == "__main__":
    asyncio.run(list_voices())
