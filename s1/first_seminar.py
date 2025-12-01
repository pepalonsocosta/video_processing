import subprocess

class Seminar1:

    @staticmethod
    def rgb_to_yuv(r, g, b):
        
        y = 0.257 * r + 0.504 * g + 0.098 * b + 16
        u = -0.148 * r - 0.291 * g + 0.439 * b + 128
        v = 0.439 * r - 0.368 * g - 0.071 * b + 128
        return y, u, v

    @staticmethod
    def yuv_to_rgb(y, u, v):

        y_prime = y - 16
        u_prime = u - 128
        v_prime = v - 128
        
        r = 1.164 * y_prime + 1.596 * v_prime
        g = 1.164 * y_prime - 0.813 * v_prime - 0.391 * u_prime
        b = 1.164 * y_prime + 2.018 * u_prime

        r = int(round(r))
        g = int(round(g))
        b = int(round(b))

        return r, g, b

    @staticmethod
    def reduce_quality(image_path, output_path,compression_factor):
        
        cmd = ['ffmpeg', '-y', '-i', str(image_path), '-q:v', str(compression_factor), str(output_path)]
        subprocess.run(cmd)
        
        return output_path

    @staticmethod
    def _generate_zigzag_indices(size=8):

        indices = []
        row, col = 0, 0
        direction = 1  # 1 for up-right, -1 for down-left
        
        for i in range(size * size):
            indices.append((row, col))
            
            if direction == 1:  # Moving up-right
                if col == size - 1:
                    row += 1
                    direction = -1
                elif row == 0:
                    col += 1
                    direction = -1
                else:
                    row -= 1
                    col += 1
            else:  # Moving down-left
                if row == size - 1:
                    col += 1
                    direction = 1
                elif col == 0:
                    row += 1
                    direction = 1
                else:
                    row += 1
                    col -= 1
        
        return indices

    @staticmethod
    def serpentine(jpeg_path):
        with open(jpeg_path, 'rb') as f:
            file_bytes = bytearray(f.read())
        
        # Generate zigzag indices for 8x8 block
        zigzag_indices = Seminar1._generate_zigzag_indices(8)
        
        # Process bytes in 8x8 blocks
        block_size = 8 * 8  # 64 bytes per block
        result = []
        
        # Process the file in 8x8 blocks
        for block_start in range(0, len(file_bytes), block_size):
            block = file_bytes[block_start:block_start + block_size]
            
            # If block is smaller than 64 bytes, pad with zeros
            if len(block) < block_size:
                block.extend([0] * (block_size - len(block)))
            
            # Create 8x8 matrix from block
            matrix = [[0] * 8 for _ in range(8)]
            for i in range(8):
                for j in range(8):
                    matrix[i][j] = block[i * 8 + j]
            
            # Apply zigzag scanning to get linear sequence
            zigzag_sequence = []
            for row, col in zigzag_indices:
                zigzag_sequence.append(matrix[row][col])
            
            result.extend(zigzag_sequence)
        
        return result

    @staticmethod
    def convert_to_bw_max_compression(image_path, output_path):
        
        cmd = ['ffmpeg', '-y', '-i', str(image_path), '-vf', 'format=gray', '-q:v', '31', str(output_path)]
        subprocess.run(cmd)
        
        return output_path

    @staticmethod
    def run_lenght_encoding(input_bytes):
        
        encoded = []
        count = 1
        
        for i in range(1, len(input_bytes)):
            if input_bytes[i] == input_bytes[i-1]:
                count += 1
            else:
                # If count > 1, it's a run - encode as tuple
                # If count == 1, it's a single value - add as number
                if count > 1:
                    encoded.append((count, input_bytes[i-1]))
                else:
                    encoded.append(input_bytes[i-1])
                count = 1
        
        # Handle the last byte
        if count > 1:
            encoded.append((count, input_bytes[-1]))
        else:
            encoded.append(input_bytes[-1])
        
        return encoded



# ex-2
r, g, b = 120, 200, 80
y, u, v = Seminar1.rgb_to_yuv(r, g, b)
print("YUV:", y, u, v)

r2, g2, b2 = Seminar1.yuv_to_rgb(y, u, v)
print("RGB:", r2, g2, b2)

# ex-3
output_image = Seminar1.reduce_quality('./image_to_resize.jpg', 'compressed_image.jpg', 32)
print("Compressed image saved to:", output_image)

# ex-4: Test serpentine method with a JPEG file
jpeg_file = './image_to_resize.jpg'
zigzag_bytes = Seminar1.serpentine(jpeg_file)
print(f"\nSerpentine scanning applied to {jpeg_file}")
print("Compressed file size:", len(zigzag_bytes))

# ex-5
bw_image = Seminar1.convert_to_bw_max_compression('./image_to_resize.jpg', 'bw_max_compressed.jpg')
print("B/W compressed image saved to:", bw_image)

# ex-5.2
with open(jpeg_file, 'rb') as f:
    input_bytes = bytearray(f.read())
encoded_bytes = Seminar1.run_lenght_encoding(input_bytes)
print(f"First 30 encoded bytes: {encoded_bytes[:30]}")