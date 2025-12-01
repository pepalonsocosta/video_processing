import numpy as np
import pytest
import sys
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))
from first_seminar import Seminar1


class TestRGBYUV:
    """Tests for RGB to YUV conversion methods"""
    
    def test_rgb_to_yuv(self):
        """Test RGB to YUV conversion"""
        r, g, b = 120, 200, 80
        y, u, v = Seminar1.rgb_to_yuv(r, g, b)
        
        assert isinstance(y, (int, float))
        assert isinstance(u, (int, float))
        assert isinstance(v, (int, float))
        assert 0 <= y <= 255
        assert 0 <= u <= 255
        assert 0 <= v <= 255
    
    def test_yuv_to_rgb(self):
        """Test YUV to RGB conversion"""
        y, u, v = 155.48, 87.16, 101.4
        r, g, b = Seminar1.yuv_to_rgb(y, u, v)
        
        assert isinstance(r, int)
        assert isinstance(g, int)
        assert isinstance(b, int)
        assert 0 <= r <= 255
        assert 0 <= g <= 255
        assert 0 <= b <= 255
    
    def test_round_trip_rgb_yuv(self):
        """Test that RGB -> YUV -> RGB returns original (approximately)"""
        original_r, original_g, original_b = 120, 200, 80
        y, u, v = Seminar1.rgb_to_yuv(original_r, original_g, original_b)
        r, g, b = Seminar1.yuv_to_rgb(y, u, v)
        
        # Should be close (within 1-2 pixels due to rounding)
        assert abs(r - original_r) <= 2
        assert abs(g - original_g) <= 2
        assert abs(b - original_b) <= 2
    
    def test_round_trip_yuv_rgb(self):
        """Test that YUV -> RGB -> YUV returns original (approximately)"""
        original_y, original_u, original_v = 155.48, 87.16, 101.4
        r, g, b = Seminar1.yuv_to_rgb(original_y, original_u, original_v)
        y, u, v = Seminar1.rgb_to_yuv(r, g, b)
        
        # Should be close (within tolerance)
        assert abs(y - original_y) < 5.0
        assert abs(u - original_u) < 5.0
        assert abs(v - original_v) < 5.0
    
    def test_edge_cases(self):
        """Test edge cases: black, white, primary colors"""
        # Black
        y, u, v = Seminar1.rgb_to_yuv(0, 0, 0)
        assert y >= 0
        r, g, b = Seminar1.yuv_to_rgb(y, u, v)
        assert r >= 0 and g >= 0 and b >= 0
        
        # White
        y, u, v = Seminar1.rgb_to_yuv(255, 255, 255)
        assert y <= 255
        r, g, b = Seminar1.yuv_to_rgb(y, u, v)
        assert r <= 255 and g <= 255 and b <= 255


class TestSerpentine:
    """Tests for serpentine (zigzag) method"""
    
    def test_serpentine_returns_list(self):
        """Test that serpentine returns a list"""
        # Create a temporary test file
        test_data = bytearray([i for i in range(64)])  # 64 bytes = one 8x8 block
        
        with patch('builtins.open', mock_open(read_data=bytes(test_data))):
            result = Seminar1.serpentine('dummy_path.jpg')
            assert isinstance(result, list)
    
    def test_serpentine_processes_bytes(self):
        """Test that serpentine processes file bytes"""
        test_data = bytearray([i for i in range(64)])
        
        with patch('builtins.open', mock_open(read_data=bytes(test_data))):
            result = Seminar1.serpentine('dummy_path.jpg')
            assert len(result) == 64  # One 8x8 block = 64 bytes
    
    def test_serpentine_zigzag_pattern(self):
        """Test that serpentine applies zigzag pattern correctly"""
        # Create test data that will show zigzag pattern
        test_data = bytearray([i for i in range(64)])
        
        with patch('builtins.open', mock_open(read_data=bytes(test_data))):
            result = Seminar1.serpentine('dummy_path.jpg')
            # First value should be from position (0,0)
            # Second should be from (0,1) or (1,0) depending on zigzag
            assert len(result) == 64
            # The pattern should reorder the bytes
            assert result[0] == 0  # First byte (0,0)
    
    def test_serpentine_multiple_blocks(self):
        """Test that serpentine handles multiple 8x8 blocks"""
        test_data = bytearray([i % 256 for i in range(128)])  # 2 blocks
        
        with patch('builtins.open', mock_open(read_data=bytes(test_data))):
            result = Seminar1.serpentine('dummy_path.jpg')
            assert len(result) == 128  # 2 blocks = 128 bytes
    
    def test_serpentine_file_not_found(self):
        """Test that serpentine handles file not found gracefully"""
        with patch('builtins.open', side_effect=FileNotFoundError):
            # Should raise FileNotFoundError
            with pytest.raises(FileNotFoundError):
                Seminar1.serpentine('nonexistent.jpg')


class TestRunLengthEncoding:
    """Tests for run-length encoding method"""
    
    def test_rle_returns_list(self):
        """Test that RLE returns a list"""
        input_bytes = bytearray([1, 2, 3, 4, 5])
        result = Seminar1.run_lenght_encoding(input_bytes)
        assert isinstance(result, list)
    
    def test_rle_single_values(self):
        """Test RLE with no repeated values"""
        input_bytes = bytearray([1, 2, 3, 4, 5])
        result = Seminar1.run_lenght_encoding(input_bytes)
        # All should be single values (not tuples)
        assert all(not isinstance(x, tuple) for x in result)
        assert len(result) == 5
    
    def test_rle_repeated_values(self):
        """Test RLE with repeated values"""
        input_bytes = bytearray([1, 1, 1, 2, 3, 3, 4])
        result = Seminar1.run_lenght_encoding(input_bytes)
        
        # Should have tuples for runs
        assert isinstance(result[0], tuple)  # (3, 1)
        assert result[0] == (3, 1)
        assert result[1] == 2  # Single value
        assert isinstance(result[2], tuple)  # (2, 3)
        assert result[2] == (2, 3)
        assert result[3] == 4  # Single value
    
    def test_rle_all_same(self):
        """Test RLE with all same values"""
        input_bytes = bytearray([5, 5, 5, 5, 5])
        result = Seminar1.run_lenght_encoding(input_bytes)
        assert len(result) == 1
        assert result[0] == (5, 5)
    
    def test_rle_empty(self):
        """Test RLE with empty input"""
        input_bytes = bytearray()
        result = Seminar1.run_lenght_encoding(input_bytes)
        # Empty input should return empty list
        assert isinstance(result, list)
        assert len(result) == 0
    
    def test_rle_format(self):
        """Test RLE output format: tuples for runs, numbers for singles"""
        input_bytes = bytearray([10, 10, 20, 30, 30, 30, 40])
        result = Seminar1.run_lenght_encoding(input_bytes)
        
        # Check format: (count, value) for runs, value for singles
        assert isinstance(result[0], tuple)  # (2, 10)
        assert result[1] == 20  # Single
        assert isinstance(result[2], tuple)  # (3, 30)
        assert result[3] == 40  # Single


class TestReduceQuality:
    """Tests for reduce_quality method"""
    
    @patch('subprocess.run')
    def test_reduce_quality_calls_ffmpeg(self, mock_run):
        """Test that reduce_quality calls ffmpeg with correct arguments"""
        mock_run.return_value = MagicMock()
        
        result = Seminar1.reduce_quality('input.jpg', 'output.jpg', 31)
        
        # Check that subprocess.run was called
        assert mock_run.called
        # Check arguments
        call_args = mock_run.call_args[0][0]
        assert 'ffmpeg' in call_args
        assert '-i' in call_args
        assert 'input.jpg' in call_args
        assert '-q:v' in call_args
        assert '31' in call_args
        assert 'output.jpg' in call_args
        assert result == 'output.jpg'
    
    @patch('subprocess.run')
    def test_reduce_quality_returns_output_path(self, mock_run):
        """Test that reduce_quality returns output path"""
        mock_run.return_value = MagicMock()
        
        result = Seminar1.reduce_quality('input.jpg', 'output.jpg', 32)
        assert result == 'output.jpg'


class TestConvertToBWMaxCompression:
    """Tests for convert_to_bw_max_compression method"""
    
    @patch('subprocess.run')
    def test_convert_to_bw_calls_ffmpeg(self, mock_run):
        """Test that convert_to_bw calls ffmpeg with correct arguments"""
        mock_run.return_value = MagicMock()
        
        result = Seminar1.convert_to_bw_max_compression('input.jpg', 'output.jpg')
        
        # Check that subprocess.run was called
        assert mock_run.called
        # Check arguments
        call_args = mock_run.call_args[0][0]
        assert 'ffmpeg' in call_args
        assert '-i' in call_args
        assert 'input.jpg' in call_args
        assert '-vf' in call_args
        assert 'format=gray' in call_args
        assert '-q:v' in call_args
        assert '31' in call_args
        assert 'output.jpg' in call_args
        assert result == 'output.jpg'
    
    @patch('subprocess.run')
    def test_convert_to_bw_returns_output_path(self, mock_run):
        """Test that convert_to_bw returns output path"""
        mock_run.return_value = MagicMock()
        
        result = Seminar1.convert_to_bw_max_compression('input.jpg', 'bw_output.jpg')
        assert result == 'bw_output.jpg'


class TestZigzagIndices:
    """Tests for _generate_zigzag_indices helper method (tested via serpentine)"""
    
    def test_zigzag_indices_via_serpentine(self):
        """Test zigzag pattern indirectly through serpentine"""
        # Create known test data
        test_data = bytearray([i for i in range(64)])
        
        with patch('builtins.open', mock_open(read_data=bytes(test_data))):
            result = Seminar1.serpentine('dummy_path.jpg')
            # Verify zigzag reordering happened
            # First should be 0 (position 0,0)
            assert result[0] == 0
            # Should have 64 elements
            assert len(result) == 64
            # All original values should be present
            assert set(result) == set(range(64))

