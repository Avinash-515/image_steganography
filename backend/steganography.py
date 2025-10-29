from PIL import Image
import numpy as np
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes
import base64
import os

class ImageSteganography:
    def __init__(self):
        self.delimiter = '1111111111111110'  # Binary delimiter to mark end of data
    
    def hide_data(self, image_path, secret_data, password='', output_path=None):
        """Hide secret data in an image using LSB steganography"""
        try:
            # Load image
            img = Image.open(image_path)
            
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Encrypt data if password is provided
            data_to_hide = secret_data
            if password:
                data_to_hide = self._encrypt_data(secret_data, password)
            
            # Convert data to binary
            binary_data = ''.join(format(ord(char), '08b') for char in data_to_hide)
            binary_data += self.delimiter  # Add delimiter
            
            # Check if image can hold the data
            img_array = np.array(img)
            max_capacity = img_array.size
            
            if len(binary_data) > max_capacity:
                raise ValueError(f"Image too small. Need {len(binary_data)} bits, have {max_capacity}")
            
            # Flatten image array for easier manipulation
            flat_img = img_array.flatten()
            
            # Hide data in LSBs
            for i, bit in enumerate(binary_data):
                if i < len(flat_img):
                    # Modify LSB
                    flat_img[i] = (flat_img[i] & 0xFE) | int(bit)
            
            # Reshape back to original shape
            modified_img_array = flat_img.reshape(img_array.shape)
            
            # Create output image
            output_img = Image.fromarray(modified_img_array.astype('uint8'))
            
            # Use the specified output path or generate one
            if output_path is None:
                output_path = os.path.join(
                    os.path.dirname(image_path),
                    f"stego_{os.path.basename(image_path)}"
                )
            
            # Save steganographic image
            output_img.save(output_path, 'PNG')
            
            print(f"✅ Data hidden successfully in {output_path}")
            return output_path
            
        except Exception as e:
            print(f"❌ Steganography error: {str(e)}")
            return None
    
    def extract_data(self, image_path, password=None):
        """Extract hidden data from steganographic image"""
        try:
            # Load image
            img = Image.open(image_path)
            
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Convert to numpy array and flatten
            img_array = np.array(img).flatten()
            
            # Extract LSBs
            binary_data = ''
            for pixel_value in img_array:
                binary_data += str(pixel_value & 1)
            
            # Find delimiter
            delimiter_index = binary_data.find(self.delimiter)
            if delimiter_index == -1:
                raise ValueError("No hidden data found or data corrupted")
            
            # Extract actual data (before delimiter)
            actual_binary_data = binary_data[:delimiter_index]
            
            # Convert binary to text
            if len(actual_binary_data) % 8 != 0:
                raise ValueError("Invalid data length - not divisible by 8")
            
            extracted_text = ''
            for i in range(0, len(actual_binary_data), 8):
                byte = actual_binary_data[i:i+8]
                if len(byte) == 8:
                    char_code = int(byte, 2)
                    if 0 <= char_code <= 127:  # Valid ASCII range
                        extracted_text += chr(char_code)
                    else:
                        break  # Invalid character, might be end of data
            
            # Decrypt if password was used
            if password:
                try:
                    extracted_text = self._decrypt_data(extracted_text, password)
                except:
                    raise ValueError("Incorrect password or corrupted encrypted data")
            
            if not extracted_text:
                raise ValueError("No valid data could be extracted")
            
            print(f"✅ Data extracted successfully: {len(extracted_text)} characters")
            return extracted_text
            
        except Exception as e:
            raise Exception(f"Data extraction failed: {str(e)}")
    
    def _encrypt_data(self, data, password):
        """Encrypt data using AES encryption"""
        try:
            # Generate salt
            salt = get_random_bytes(16)
            
            # Derive key from password
            key = PBKDF2(password, salt, 32, count=100000)
            
            # Create cipher
            cipher = AES.new(key, AES.MODE_GCM)
            
            # Encrypt data
            ciphertext, tag = cipher.encrypt_and_digest(data.encode('utf-8'))
            
            # Combine salt, nonce, tag, and ciphertext
            encrypted_data = base64.b64encode(
                salt + cipher.nonce + tag + ciphertext
            ).decode('utf-8')
            
            return encrypted_data
            
        except Exception as e:
            raise Exception(f"Encryption failed: {str(e)}")
    
    def _decrypt_data(self, encrypted_data, password):
        """Decrypt AES encrypted data"""
        try:
            # Decode base64
            encrypted_bytes = base64.b64decode(encrypted_data.encode('utf-8'))
            
            # Extract components
            salt = encrypted_bytes[:16]
            nonce = encrypted_bytes[16:32]
            tag = encrypted_bytes[32:48]
            ciphertext = encrypted_bytes[48:]
            
            # Derive key from password
            key = PBKDF2(password, salt, 32, count=100000)
            
            # Create cipher and decrypt
            cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
            decrypted_data = cipher.decrypt_and_verify(ciphertext, tag)
            
            return decrypted_data.decode('utf-8')
            
        except Exception as e:
            raise Exception(f"Decryption failed: {str(e)}")
    
    def analyze_image_capacity(self, image_path):
        """Analyze how much data an image can hold"""
        try:
            img = Image.open(image_path)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            img_array = np.array(img)
            total_pixels = img_array.size
            
            # Each pixel can hide 1 bit, need 8 bits per character
            max_chars = (total_pixels - len(self.delimiter)) // 8
            
            return {
                'total_pixels': total_pixels,
                'max_characters': max_chars,
                'max_bytes': max_chars,
                'image_dimensions': img.size
            }
            
        except Exception as e:
            raise Exception(f"Image analysis failed: {str(e)}")