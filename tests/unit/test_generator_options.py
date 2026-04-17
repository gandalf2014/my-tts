"""
TTSGenerator参数转换单元测试

测试_convert_options_to_edge_tts()函数的转换逻辑
"""

import pytest
from src.tts.generator import TTSGenerator, TTSOptions


class TestOptionsConversion:
    """参数转换测试类"""

    def test_speed_minimum(self):
        """测试语速最小值边界"""
        options = TTSOptions(speed=0.5, pitch=1.0, volume=100.0)
        result = TTSGenerator._convert_options_to_edge_tts(options)
        assert result['rate'] == '-50%'

    def test_speed_maximum(self):
        """测试语速最大值边界"""
        options = TTSOptions(speed=2.0, pitch=1.0, volume=100.0)
        result = TTSGenerator._convert_options_to_edge_tts(options)
        assert result['rate'] == '+100%'

    def test_speed_default(self):
        """测试语速默认值"""
        options = TTSOptions(speed=1.0, pitch=1.0, volume=100.0)
        result = TTSGenerator._convert_options_to_edge_tts(options)
        assert result['rate'] == '+0%'

    def test_speed_middle_value(self):
        """测试语速中间值"""
        options = TTSOptions(speed=1.5, pitch=1.0, volume=100.0)
        result = TTSGenerator._convert_options_to_edge_tts(options)
        assert result['rate'] == '+50%'

    def test_speed_below_minimum_raises_error(self):
        """测试语速低于最小值抛出异常"""
        options = TTSOptions(speed=0.4, pitch=1.0, volume=100.0)
        with pytest.raises(ValueError, match="语速.*超出有效范围"):
            TTSGenerator._convert_options_to_edge_tts(options)

    def test_speed_above_maximum_raises_error(self):
        """测试语速高于最大值抛出异常"""
        options = TTSOptions(speed=2.1, pitch=1.0, volume=100.0)
        with pytest.raises(ValueError, match="语速.*超出有效范围"):
            TTSGenerator._convert_options_to_edge_tts(options)

    def test_pitch_minimum(self):
        """测试音调最小值边界"""
        options = TTSOptions(speed=1.0, pitch=0.5, volume=100.0)
        result = TTSGenerator._convert_options_to_edge_tts(options)
        assert result['pitch'] == '-50Hz'

    def test_pitch_maximum(self):
        """测试音调最大值边界"""
        options = TTSOptions(speed=1.0, pitch=2.0, volume=100.0)
        result = TTSGenerator._convert_options_to_edge_tts(options)
        assert result['pitch'] == '+100Hz'

    def test_pitch_default(self):
        """测试音调默认值 - 不传递pitch参数"""
        options = TTSOptions(speed=1.0, pitch=1.0, volume=100.0)
        result = TTSGenerator._convert_options_to_edge_tts(options)
        # edge-tts 不接受 '0Hz'，所以默认值不传递
        assert 'pitch' not in result

    def test_pitch_middle_value(self):
        """测试音调中间值"""
        options = TTSOptions(speed=1.0, pitch=1.75, volume=100.0)
        result = TTSGenerator._convert_options_to_edge_tts(options)
        assert result['pitch'] == '+75Hz'

    def test_pitch_below_minimum_raises_error(self):
        """测试音调低于最小值抛出异常"""
        options = TTSOptions(speed=1.0, pitch=0.4, volume=100.0)
        with pytest.raises(ValueError, match="音调.*超出有效范围"):
            TTSGenerator._convert_options_to_edge_tts(options)

    def test_pitch_above_maximum_raises_error(self):
        """测试音调高于最大值抛出异常"""
        options = TTSOptions(speed=1.0, pitch=2.1, volume=100.0)
        with pytest.raises(ValueError, match="音调.*超出有效范围"):
            TTSGenerator._convert_options_to_edge_tts(options)

    def test_volume_minimum(self):
        """测试音量最小值边界"""
        options = TTSOptions(speed=1.0, pitch=1.0, volume=0)
        result = TTSGenerator._convert_options_to_edge_tts(options)
        assert result['volume'] == '-100%'

    def test_volume_maximum(self):
        """测试音量最大值 - 不传递volume参数"""
        options = TTSOptions(speed=1.0, pitch=1.0, volume=100.0)
        result = TTSGenerator._convert_options_to_edge_tts(options)
        # edge-tts 不接受 '0%'，所以默认值不传递
        assert 'volume' not in result

    def test_volume_middle_value(self):
        """测试音量中间值"""
        options = TTSOptions(speed=1.0, pitch=1.0, volume=50.0)
        result = TTSGenerator._convert_options_to_edge_tts(options)
        assert result['volume'] == '-50%'

    def test_volume_quarter_value(self):
        """测试音量25%"""
        options = TTSOptions(speed=1.0, pitch=1.0, volume=25.0)
        result = TTSGenerator._convert_options_to_edge_tts(options)
        assert result['volume'] == '-75%'

    def test_volume_below_minimum_raises_error(self):
        """测试音量低于最小值抛出异常"""
        options = TTSOptions(speed=1.0, pitch=1.0, volume=-1.0)
        with pytest.raises(ValueError, match="音量.*超出有效范围"):
            TTSGenerator._convert_options_to_edge_tts(options)

    def test_volume_above_maximum_raises_error(self):
        """测试音量高于最大值抛出异常"""
        options = TTSOptions(speed=1.0, pitch=1.0, volume=101.0)
        with pytest.raises(ValueError, match="音量.*超出有效范围"):
            TTSGenerator._convert_options_to_edge_tts(options)

    def test_all_parameters_combined(self):
        """测试所有参数组合转换"""
        options = TTSOptions(speed=1.25, pitch=0.75, volume=75.0)
        result = TTSGenerator._convert_options_to_edge_tts(options)
        assert result['rate'] == '+25%'
        assert result['pitch'] == '-25Hz'
        assert result['volume'] == '-25%'

    def test_all_default_values(self):
        """测试所有默认值 - 只有rate传递"""
        options = TTSOptions()
        result = TTSGenerator._convert_options_to_edge_tts(options)
        assert result['rate'] == '+0%'
        # pitch=1.0 和 volume=100 是默认值，不传递
        assert 'pitch' not in result
        assert 'volume' not in result

    def test_return_type_is_dict(self):
        """测试返回类型是字典"""
        options = TTSOptions()
        result = TTSGenerator._convert_options_to_edge_tts(options)
        assert isinstance(result, dict)
        assert 'rate' in result
        # pitch 和 volume 在默认值时不传递
