import numpy as np
import pywt

class DWT:
    
    @staticmethod
    def encode(data, wavelet='haar', mode='symmetric'):

        data = np.array(data, dtype=np.float64)
        
        coeffs = pywt.dwt2(data, wavelet, mode)
        
        return coeffs
    
    @staticmethod
    def decode(coeffs, wavelet='haar', mode='symmetric'):

        reconstructed = pywt.idwt2(coeffs, wavelet, mode)
        
        reconstructed = np.clip(reconstructed, 0, 255)
        reconstructed = np.round(reconstructed).astype(np.uint8)
        
        return reconstructed


if __name__ == "__main__":

    test_block = np.array([
        [100, 110, 120, 130, 140, 150, 160, 170],
        [110, 120, 130, 140, 150, 160, 170, 180],
        [120, 130, 140, 150, 160, 170, 180, 190],
        [130, 140, 150, 160, 170, 180, 190, 200],
        [140, 150, 160, 170, 180, 190, 200, 210],
        [150, 160, 170, 180, 190, 200, 210, 220],
        [160, 170, 180, 190, 200, 210, 220, 230],
        [170, 180, 190, 200, 210, 220, 230, 240]
    ], dtype=np.uint8)
    
    print("Original 8x8 block:")
    print(test_block)
    print()
    
    dwt_coeffs = DWT.encode(test_block)
    cA, (cH, cV, cD) = dwt_coeffs
    
    print("DWT coefficients:")
    print(cA.astype(int))
    print(cH.astype(int))
    print(cV.astype(int))
    print(cD.astype(int))
    print()
    
    reconstructed = DWT.decode(dwt_coeffs)
    print("Reconstructed block (after IDWT):")
    print(reconstructed)
    print()
    
    difference = np.abs(test_block.astype(int) - reconstructed.astype(int))
    print("Difference between original and reconstructed:")
    print(difference)

