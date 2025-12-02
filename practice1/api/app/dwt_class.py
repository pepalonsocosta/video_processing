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

