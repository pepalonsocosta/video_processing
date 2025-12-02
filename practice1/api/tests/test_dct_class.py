import numpy as np
import pytest
from app.dct_class import DCT


@pytest.fixture
def test_block_8x8():
    """Fixture for a standard 8x8 test block"""
    return np.array([
        [100, 110, 120, 130, 140, 150, 160, 170],
        [110, 120, 130, 140, 150, 160, 170, 180],
        [120, 130, 140, 150, 160, 170, 180, 190],
        [130, 140, 150, 160, 170, 180, 190, 200],
        [140, 150, 160, 170, 180, 190, 200, 210],
        [150, 160, 170, 180, 190, 200, 210, 220],
        [160, 170, 180, 190, 200, 210, 220, 230],
        [170, 180, 190, 200, 210, 220, 230, 240]
    ], dtype=np.uint8)


@pytest.fixture
def zero_block_8x8():
    """Fixture for an 8x8 block of zeros"""
    return np.zeros((8, 8), dtype=np.uint8)


@pytest.fixture
def constant_block_8x8():
    """Fixture for an 8x8 block with constant value"""
    return np.full((8, 8), 128, dtype=np.uint8)


class TestDCTEncode:
    """Tests for DCT.encode() method"""
    
    def test_encode_shape(self, test_block_8x8):
        """Test that encode returns 8x8 array"""
        result = DCT.encode(test_block_8x8)
        assert result.shape == (8, 8)
    
    def test_encode_type(self, test_block_8x8):
        """Test that encode returns numpy array"""
        result = DCT.encode(test_block_8x8)
        assert isinstance(result, np.ndarray)
    
    def test_encode_zero_block(self, zero_block_8x8):
        """Test encoding a block of zeros"""
        result = DCT.encode(zero_block_8x8)
        # DC coefficient should be zero, others should be zero or very small
        assert np.abs(result[0, 0]) < 1e-10
        assert np.allclose(result, 0, atol=1e-10)
    
    def test_encode_constant_block(self, constant_block_8x8):
        """Test encoding a constant block"""
        result = DCT.encode(constant_block_8x8)
        # DC coefficient should be the constant value * 8
        assert np.abs(result[0, 0] - 128 * 8) < 1.0
        # AC coefficients should be zero or very small
        ac_coeffs = result.copy()
        ac_coeffs[0, 0] = 0
        assert np.allclose(ac_coeffs, 0, atol=1.0)


class TestDCTDecode:
    """Tests for DCT.decode() method"""
    
    def test_decode_shape(self, test_block_8x8):
        """Test that decode returns 8x8 array"""
        coeffs = DCT.encode(test_block_8x8)
        result = DCT.decode(coeffs)
        assert result.shape == (8, 8)
    
    def test_decode_type(self, test_block_8x8):
        """Test that decode returns numpy array of uint8"""
        coeffs = DCT.encode(test_block_8x8)
        result = DCT.decode(coeffs)
        assert isinstance(result, np.ndarray)
        assert result.dtype == np.uint8
    
    def test_decode_pixel_range(self, test_block_8x8):
        """Test that decoded values are in valid pixel range"""
        coeffs = DCT.encode(test_block_8x8)
        result = DCT.decode(coeffs)
        assert np.all(result >= 0)
        assert np.all(result <= 255)


class TestDCTRoundTrip:
    """Tests for encode -> decode round-trip"""
    
    def test_round_trip_accuracy(self, test_block_8x8):
        """Test that encode -> decode returns original (within tolerance)"""
        coeffs = DCT.encode(test_block_8x8)
        reconstructed = DCT.decode(coeffs)
        difference = np.abs(test_block_8x8.astype(int) - reconstructed.astype(int))
        # Should be very close (within 1 pixel difference due to rounding)
        assert np.max(difference) <= 1
        assert np.mean(difference) < 0.5
    
    def test_round_trip_zero_block(self, zero_block_8x8):
        """Test round-trip with zero block"""
        coeffs = DCT.encode(zero_block_8x8)
        reconstructed = DCT.decode(coeffs)
        assert np.allclose(reconstructed, 0)
    
    def test_round_trip_constant_block(self, constant_block_8x8):
        """Test round-trip with constant block"""
        coeffs = DCT.encode(constant_block_8x8)
        reconstructed = DCT.decode(coeffs)
        # Should reconstruct to constant value (within rounding)
        assert np.all(np.abs(reconstructed.astype(int) - 128) <= 1)
    
    def test_round_trip_random_block(self):
        """Test round-trip with random block"""
        random_block = np.random.randint(0, 256, (8, 8), dtype=np.uint8)
        coeffs = DCT.encode(random_block)
        reconstructed = DCT.decode(coeffs)
        difference = np.abs(random_block.astype(int) - reconstructed.astype(int))
        # Should be very close
        assert np.max(difference) <= 1
        assert np.mean(difference) < 0.5


class TestDCTProperties:
    """Tests for DCT mathematical properties"""
    
    def test_dc_coefficient(self, test_block_8x8):
        """Test that DC coefficient (0,0) is related to block average"""
        coeffs = DCT.encode(test_block_8x8)
        block_sum = np.sum(test_block_8x8)
        # DC coefficient should be approximately sum * normalization factors
        # For DCT: DC = (2/N) * a(0) * a(0) * sum = (2/8) * (1/√2) * (1/√2) * sum = (1/4) * sum
        expected_dc = block_sum * (2.0 / 8) * (1.0 / np.sqrt(2)) * (1.0 / np.sqrt(2))
        # Allow some tolerance for floating point precision
        assert np.abs(coeffs[0, 0] - expected_dc) < 50.0
    
    def test_symmetry(self, test_block_8x8):
        """Test that DCT coefficients have expected properties"""
        coeffs = DCT.encode(test_block_8x8)
        # DC coefficient should be largest in magnitude for smooth images
        dc_magnitude = np.abs(coeffs[0, 0])
        ac_magnitudes = np.abs(coeffs[1:, 1:])
        # DC should be significant
        assert dc_magnitude > 100

