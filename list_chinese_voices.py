#!/usr/bin/env python3
"""
列出所有中文语音选项
"""
import asyncio
import edge_tts

async def list_all_chinese_voices():
    """列出所有中文语音"""
    print("正在获取所有中文语音...")
    voices = await edge_tts.list_voices()
    
    # 筛选中文语音
    chinese_voices = [v for v in voices if v['Locale'].startswith('zh-')]
    
    print(f"\n找到 {len(chinese_voices)} 个中文语音:")
    print("=" * 80)
    
    # 按地区分组
    regions = {}
    for voice in chinese_voices:
        locale = voice['Locale']
        if locale not in regions:
            regions[locale] = []
        regions[locale].append(voice)
    
    for locale, voices_in_region in sorted(regions.items()):
        region_name = {
            'zh-CN': '中国大陆',
            'zh-HK': '香港',
            'zh-TW': '台湾',
            'zh-CN-liaoning': '中国大陆(辽宁)',
            'zh-CN-shaanxi': '中国大陆(陕西)'
        }.get(locale, locale)
        
        print(f"\n📍 {region_name} ({locale}) - {len(voices_in_region)} 个语音:")
        print("-" * 60)
        
        for voice in voices_in_region:
            # 提取英文名称
            short_name = voice['ShortName']
            if '-' in short_name:
                english_name = short_name.split('-')[-1].replace('Neural', '')
            else:
                english_name = voice['FriendlyName'].split(' ')[1] if ' ' in voice['FriendlyName'] else voice['FriendlyName']
            
            # 获取中文名称
            chinese_name = get_chinese_name(english_name)
            
            print(f"  {chinese_name} / {english_name}")
            print(f"    完整名称: {voice['FriendlyName']}")
            print(f"    短名称: {voice['ShortName']}")
            print(f"    性别: {voice['Gender']}")
            print()

def get_chinese_name(english_name):
    """获取语音的中文名称"""
    name_mapping = {
        # 中国大陆语音
        'Xiaoxiao': '晓晓',
        'Xiaoyi': '晓伊', 
        'Yunjian': '云健',
        'Yunxi': '云希',
        'Yunxia': '云夏',
        'Yunyang': '云扬',
        'Xiaobei': '晓北',
        'Xiaoni': '晓妮',
        'Xiaoxuan': '晓萱',
        'Xiaochen': '晓辰',
        'Xiaohan': '晓涵',
        'Xiaoyan': '晓燕',
        'Yunhao': '云浩',
        'Xiaoshuang': '晓双',
        'Xiaomeng': '晓梦',
        'Yunfeng': '云峰',
        'Yunze': '云泽',
        'Xiaoqiu': '晓秋',
        'Yunye': '云野',
        'Xiaorui': '晓睿',
        'Yunxi': '云曦',
        'Xiaoyou': '晓悠',
        'Xiaomo': '晓墨',
        
        # 香港语音
        'HiuGaai': '晓佳',
        'HiuMaan': '晓曼',
        'WanLung': '云龙',
        
        # 台湾语音
        'HsiaoChen': '晓臻',
        'YunJhe': '云哲',
        'HsiaoYu': '晓雨'
    }
    return name_mapping.get(english_name, english_name)

async def test_voice_generation():
    """测试语音生成"""
    print("\n=== 测试语音生成 ===")
    
    voices = await edge_tts.list_voices()
    chinese_voices = [v for v in voices if v['Locale'].startswith('zh-CN')]
    
    if chinese_voices:
        # 测试前3个语音
        test_text = "你好，我是语音合成测试。"
        
        for i, voice in enumerate(chinese_voices[:3]):
            print(f"\n测试语音 {i+1}: {voice['FriendlyName']}")
            
            try:
                output_file = f"voice_test_{i+1}.mp3"
                communicate = edge_tts.Communicate(test_text, voice['ShortName'])
                await communicate.save(output_file)
                
                import os
                if os.path.exists(output_file):
                    file_size = os.path.getsize(output_file)
                    print(f"✅ 生成成功: {output_file} ({file_size} 字节)")
                else:
                    print("❌ 生成失败")
                    
            except Exception as e:
                print(f"❌ 错误: {str(e)}")

async def main():
    """主函数"""
    print("🎤 中文语音列表查看器")
    print("=" * 50)
    
    await list_all_chinese_voices()
    await test_voice_generation()
    
    print("\n✅ 完成！")

if __name__ == "__main__":
    asyncio.run(main())
