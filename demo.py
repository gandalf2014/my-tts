#!/usr/bin/env python3
"""
演示脚本 - 展示新界面的主要功能
"""
import asyncio
import edge_tts
import os

async def demo_chinese_voices():
    """演示中文语音功能"""
    print("=== 中文语音演示 ===")
    
    # 获取中文语音列表
    voices = await edge_tts.list_voices()
    chinese_voices = [v for v in voices if v['Locale'].startswith('zh-CN')]
    
    print(f"找到 {len(chinese_voices)} 个中文语音:")
    for i, voice in enumerate(chinese_voices[:5]):  # 只显示前5个
        print(f"{i+1}. {voice['FriendlyName']} ({voice['Gender']})")
    
    # 使用第一个中文语音生成演示音频
    if chinese_voices:
        demo_voice = chinese_voices[0]
        text = "欢迎使用文本转语音转换器！这个程序支持多种语音参数调节。"
        
        print(f"\n使用 {demo_voice['FriendlyName']} 生成演示音频...")
        
        # 创建带参数控制的SSML
        ssml_text = f"""<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="zh-CN">
            <voice name="{demo_voice['ShortName']}">
                <prosody rate="1.0" pitch="1.0" volume="100%">
                    {text}
                </prosody>
            </voice>
        </speak>"""
        
        output_file = "demo_chinese.mp3"
        
        try:
            communicate = edge_tts.Communicate(ssml_text, demo_voice['ShortName'])
            await communicate.save(output_file)
            
            file_size = os.path.getsize(output_file)
            print(f"✓ 演示音频生成成功: {output_file} ({file_size} 字节)")
            
        except Exception as e:
            print(f"✗ 生成失败: {str(e)}")

def show_interface_features():
    """显示界面功能说明"""
    print("\n=== 新界面功能特点 ===")
    print("📝 左侧文本输入区域:")
    print("   - 大型文本输入框，支持长文本")
    print("   - 默认显示示例文本")
    
    print("\n🎛️ 右侧控制面板:")
    print("   - 语言选择（默认中文）")
    print("   - 语音选择（按语言筛选）")
    print("   - 语音风格选择")
    print("   - 语速调节滑块 (0.5-2.0倍)")
    print("   - 音调调节滑块 (0.5-2.0倍)")
    print("   - 音量调节滑块 (0-100%)")
    print("   - 进度显示")
    print("   - 试听按钮（生成并播放）")
    print("   - 保存按钮（保存为MP3）")
    
    print("\n✨ 主要改进:")
    print("   - 界面布局更加合理（左右分栏）")
    print("   - 支持实时参数调节")
    print("   - 中文界面和默认中文语音")
    print("   - 一键试听功能")
    print("   - 更好的用户体验")

async def main():
    """主演示函数"""
    print("🎤 文本转语音GUI应用程序演示")
    print("=" * 50)
    
    # 显示界面功能
    show_interface_features()
    
    # 演示中文语音
    await demo_chinese_voices()
    
    print("\n🚀 启动应用程序:")
    print("   python tts_gui.py")
    print("   或双击 run_tts_gui.bat (Windows)")
    
    print("\n📖 更多信息请查看 README.md")

if __name__ == "__main__":
    asyncio.run(main())
