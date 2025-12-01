import numpy as np
import pytest
import sys
from pathlib import Path

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))
from dwt_class import DWT


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


class TestDWTEncode:
    """Tests for DWT.encode() method"""
    
    def test_encode_returns_tuple(self, test_block_8x8):
        """Test that encode returns a tuple of coefficients"""
        result = DWT.encode(test_block_8x8)
        assert isinstance(result, tuple)
        assert len(result) == 2
    
    def test_encode_structure(self, test_block_8x8):
        """Test that encode returns (cA, (cH, cV, cD)) structure"""
        coeffs = DWT.encode(test_block_8x8)
        cA, details = coeffs
        cH, cV, cD = details
        
        assert isinstance(cA, np.ndarray)
        assert isinstance(cH, np.ndarray)
        assert isinstance(cV, np.ndarray)
        assert isinstance(cD, np.ndarray)
    
    def test_encode_subband_shapes(self, test_block_8x8):
        """Test that sub-bands have correct downsampled shapes"""
        coeffs = DWT.encode(test_block_8x8)
        cA, (cH, cV, cD) = coeffs
        
        # For 8x8 input with Haar, output should be 4x4
        assert cA.shape == (4, 4)
        assert cH.shape == (4, 4)
        assert cV.shape == (4, 4)
        assert cD.shape == (4, 4)
    
    def test_encode_zero_block(self, zero_block_8x8):
        """Test encoding a block of zeros"""
        coeffs = DWT.encode(zero_block_8x8)
        cA, (cH, cV, cD) = coeffs
        assert np.allclose(cA, 0)
        assert np.allclose(cH, 0)
        assert np.allclose(cV, 0)
        assert np.allclose(cD, 0)
    
    def test_encode_constant_block(self, constant_block_8x8):
        """Test encoding a constant block"""
        coeffs = DWT.encode(constant_block_8x8)
        cA, (cH, cV, cD) = coeffs
        # Approximation should be constant (Haar averages pairs, so 128+128 = 256)
        # For constant block, LL should be the constant value * 2 (due to averaging)
        assert np.allclose(cA, 256, atol=1.0)
        # Details should be zero or very small (no differences in constant block)
        assert np.allclose(cH, 0, atol=1.0)
        assert np.allclose(cV, 0, atol=1.0)
        assert np.allclose(cD, 0, atol=1.0)


class TestDWTDecode:
    """Tests for DWT.decode() method"""
    
    def test_decode_shape(self, test_block_8x8):
        """Test that decode returns original shape"""
        coeffs = DWT.encode(test_block_8x8)
        result = DWT.decode(coeffs)
        assert result.shape == test_block_8x8.shape
    
    def test_decode_type(self, test_block_8x8):
        """Test that decode returns numpy array of uint8"""
        coeffs = DWT.encode(test_block_8x8)
        result = DWT.decode(coeffs)
        assert isinstance(result, np.ndarray)
        assert result.dtype == np.uint8
    
    def test_decode_pixel_range(self, test_block_8x8):
        """Test that decoded values are in valid pixel range"""
        coeffs = DWT.encode(test_block_8x8)
        result = DWT.decode(coeffs)
        assert np.all(result >= 0)
        assert np.all(result <= 255)


class TestDWTRoundTrip:
    """Tests for encode -> decode round-trip"""
    
    def test_round_trip_accuracy(self, test_block_8x8):
        """Test that encode -> decode returns original (lossless)"""
        coeffs = DWT.encode(test_block_8x8)
        reconstructed = DWT.decode(coeffs)
        difference = np.abs(test_block_8x8.astype(int) - reconstructed.astype(int))
        # DWT with Haar should be lossless (or very close)
        assert np.max(difference) <= 1
        assert np.mean(difference) < 0.5
    
    def test_round_trip_zero_block(self, zero_block_8x8):
        """Test round-trip with zero block"""
        coeffs = DWT.encode(zero_block_8x8)
        reconstructed = DWT.decode(coeffs)
        assert np.allclose(reconstructed, 0)
    
    def test_round_trip_constant_block(self, constant_block_8x8):
        """Test round-trip with constant block"""
        coeffs = DWT.encode(constant_block_8x8)
        reconstructed = DWT.decode(coeffs)
        # Should reconstruct to constant value
        assert np.all(np.abs(reconstructed.astype(int) - 128) <= 1)
    
    def test_round_trip_random_block(self):
        """Test round-trip with random block"""
        random_block = np.random.randint(0, 256, (8, 8), dtype=np.uint8)
        coeffs = DWT.encode(random_block)
        reconstructed = DWT.decode(coeffs)
        difference = np.abs(random_block.astype(int) - reconstructed.astype(int))
        # Should be very close (lossless or near-lossless)
        assert np.max(difference) <= 1
        assert np.mean(difference) < 0.5


class TestDWTProperties:
    """Tests for DWT mathematical properties"""
    
    def test_ll_approximation(self, test_block_8x8):
        """Test that LL sub-band contains approximation"""
        coeffs = DWT.encode(test_block_8x8)
        cA, (cH, cV, cD) = coeffs
        # LL should have significant values (approximation)
        assert np.abs(cA).sum() > 0
    
    def test_detail_subbands(self, test_block_8x8):
        """Test that detail sub-bands capture differences"""
        coeffs = DWT.encode(test_block_8x8)
        cA, (cH, cV, cD) = coeffs
        # For a gradient image, we should have some detail
        # At least one detail sub-band should have non-zero values
        detail_sum = np.abs(cH).sum() + np.abs(cV).sum() + np.abs(cD).sum()
        assert detail_sum > 0

