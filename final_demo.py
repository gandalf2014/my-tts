#!/usr/bin/env python3
"""
最终演示 - 展示更多语音选择功能
"""
import asyncio
import edge_tts

def show_new_features():
    """展示新功能特点"""
    print("🎤 文本转语音GUI应用程序 - 更多语音版本")
    print("=" * 60)
    
    print("\n✨ 新增功能:")
    print("📢 更多中文语音选择 - 从6种增加到14种")
    print("🌏 支持多地区中文语音 - 大陆、香港、台湾、方言")
    print("🏷️ 友好的语音显示格式 - 晓萱 / Xiaoxuan")
    print("🔍 智能语音筛选 - 中文(所有地区)选项")
    print("🎛️ 完整的参数控制 - 语速、音调、音量")
    
    print("\n🎯 按钮功能:")
    print("🎧 试听按钮 - 根据左侧文本框内容生成并播放音频")
    print("💾 保存按钮 - 根据左侧文本框内容生成并保存MP3文件")
    
    print("\n📱 界面布局:")
    print("📝 左侧 - 大型文本输入区域")
    print("🎛️ 右侧 - 语音选择和参数控制面板")

def show_voice_list():
    """显示语音列表"""
    print("\n🎤 可用的中文语音 (14种):")
    print("-" * 40)
    
    voices = [
        ("🇨🇳 中国大陆", [
            "晓晓 / Xiaoxiao (女声)",
            "晓伊 / Xiaoyi (女声)", 
            "云健 / Yunjian (男声)",
            "云希 / Yunxi (男声)",
            "云夏 / Yunxia (男声)",
            "云扬 / Yunyang (男声)"
        ]),
        ("🇭🇰 香港", [
            "晓佳 / HiuGaai (女声)",
            "晓曼 / HiuMaan (女声)",
            "云龙 / WanLung (男声)"
        ]),
        ("🇹🇼 台湾", [
            "晓臻 / HsiaoChen (女声)",
            "云哲 / YunJhe (男声)",
            "晓雨 / HsiaoYu (女声)"
        ]),
        ("🗣️ 方言", [
            "晓北 / Xiaobei (女声) - 东北话",
            "晓妮 / Xiaoni (女声) - 陕西话"
        ])
    ]
    
    for region, voice_list in voices:
        print(f"\n{region}:")
        for voice in voice_list:
            print(f"  • {voice}")

async def demo_voice_comparison():
    """演示不同语音的对比"""
    print("\n🎵 语音对比演示:")
    print("-" * 30)
    
    # 获取几个代表性的中文语音
    voices = await edge_tts.list_voices()
    chinese_voices = [v for v in voices if v['Locale'].startswith('zh-')]
    
    # 选择几个代表性语音进行演示
    demo_voices = []
    voice_names = ['Xiaoxiao', 'Yunjian', 'HiuGaai', 'HsiaoChen']
    
    for name in voice_names:
        for voice in chinese_voices:
            if name in voice['ShortName']:
                demo_voices.append(voice)
                break
    
    test_text = "欢迎使用文本转语音转换器，现在支持更多中文语音选择！"
    
    print(f"测试文本: {test_text}")
    print()
    
    for i, voice in enumerate(demo_voices):
        # 提取显示名称
        short_name = voice['ShortName']
        english_name = short_name.split('-')[-1].replace('Neural', '')
        chinese_name = get_chinese_name(english_name)
        
        print(f"🎤 {chinese_name} / {english_name}")
        print(f"   地区: {voice['Locale']}")
        print(f"   性别: {voice['Gender']}")
        
        # 生成音频文件
        output_file = f"demo_{english_name.lower()}.mp3"
        
        try:
            ssml_text = f"""<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="zh-CN">
                <voice name="{voice['ShortName']}">
                    <prosody rate="1.0" pitch="1.0" volume="100%">
                        {test_text}
                    </prosody>
                </voice>
            </speak>"""
            
            communicate = edge_tts.Communicate(ssml_text, voice['ShortName'])
            await communicate.save(output_file)
            
            import os
            if os.path.exists(output_file):
                file_size = os.path.getsize(output_file)
                print(f"   ✅ 生成成功: {output_file} ({file_size} 字节)")
            else:
                print(f"   ❌ 生成失败")
                
        except Exception as e:
            print(f"   ❌ 错误: {str(e)}")
        
        print()

def get_chinese_name(english_name):
    """获取中文名称"""
    name_mapping = {
        'Xiaoxiao': '晓晓',
        'Xiaoyi': '晓伊', 
        'Yunjian': '云健',
        'Yunxi': '云希',
        'Yunxia': '云夏',
        'Yunyang': '云扬',
        'Xiaobei': '晓北',
        'Xiaoni': '晓妮',
        'HiuGaai': '晓佳',
        'HiuMaan': '晓曼',
        'WanLung': '云龙',
        'HsiaoChen': '晓臻',
        'YunJhe': '云哲',
        'HsiaoYu': '晓雨'
    }
    return name_mapping.get(english_name, english_name)

def show_usage_instructions():
    """显示使用说明"""
    print("\n📖 使用说明:")
    print("-" * 20)
    print("1. 启动程序: python tts_gui.py")
    print("2. 在左侧文本框输入要转换的文本")
    print("3. 选择语言: 中文(所有地区)")
    print("4. 选择喜欢的语音: 如 晓萱 / Xiaoxuan")
    print("5. 调节参数: 语速、音调、音量")
    print("6. 点击试听: 生成并播放音频")
    print("7. 点击保存: 保存为MP3文件")
    
    print("\n💡 小贴士:")
    print("• 试听按钮会根据当前文本和设置实时生成音频")
    print("• 保存按钮会先让您选择保存位置，然后生成音频")
    print("• 支持长文本输入，适合朗读文章、小说等")
    print("• 所有参数调节都会实时应用到生成的音频中")

async def main():
    """主函数"""
    show_new_features()
    show_voice_list()
    await demo_voice_comparison()
    show_usage_instructions()
    
    print("\n🚀 现在就开始使用吧!")
    print("运行: python tts_gui.py")
    print("\n✨ 享受更丰富的中文语音体验！")

if __name__ == "__main__":
    asyncio.run(main())
