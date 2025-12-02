import numpy as np

class DCT:
    
    @staticmethod
    def encode(block):

        block = np.array(block, dtype=np.float64)
        N = 8
        result = np.zeros((N, N), dtype=np.float64)
        
        # Normalization factors: a(0) = 1/√2, a(n) = 1 for n > 0
        def alpha(n):
            return 1.0 / np.sqrt(2) if n == 0 else 1.0
        
        # Compute DCT for each coefficient (u, v)
        for u in range(N):
            for v in range(N):
                sum_val = 0.0
                
                # Double sum over all pixels (x, y)
                for x in range(N):
                    for y in range(N):
                        cos_x = np.cos((2 * x + 1) * u * np.pi / (2 * N))
                        cos_y = np.cos((2 * y + 1) * v * np.pi / (2 * N))
                        sum_val += block[x, y] * cos_x * cos_y
                
                # Apply normalization factors: (2/N) * a(u) * a(v)
                result[u, v] = (2.0 / N) * alpha(u) * alpha(v) * sum_val
        
        return result
    
    @staticmethod
    def decode(coefficients):

        coeffs = np.array(coefficients, dtype=np.float64)
        N = 8
        result = np.zeros((N, N), dtype=np.float64)
        
        # Normalization factors: a(0) = 1/√2, a(n) = 1 for n > 0
        def alpha(n):
            return 1.0 / np.sqrt(2) if n == 0 else 1.0
        
        # Compute IDCT for each pixel (x, y)
        for x in range(N):
            for y in range(N):
                sum_val = 0.0
                
                # Double sum over all coefficients (u, v)
                for u in range(N):
                    for v in range(N):
                        cos_x = np.cos((2 * x + 1) * u * np.pi / (2 * N))
                        cos_y = np.cos((2 * y + 1) * v * np.pi / (2 * N))
                        sum_val += alpha(u) * alpha(v) * coeffs[u, v] * cos_x * cos_y
                
                # Normalize by (2/N) factor
                result[x, y] = (2.0 / N) * sum_val
        
        # Clip to valid pixel range and round
        result = np.clip(result, 0, 255)
        result = np.round(result).astype(np.uint8)
        
        return result

