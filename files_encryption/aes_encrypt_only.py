"""
Implementación de AES 128 desde cero - Solo cifrado
"""

class AES128Encrypt:
    """
    Implementación de AES 128 enfocada únicamente en cifrado
    """
    
    def __init__(self):
        # S-Box para SubBytes
        self.s_box = [
            0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5, 0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76,
            0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59, 0x47, 0xf0, 0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4, 0x72, 0xc0,
            0xb7, 0xfd, 0x93, 0x26, 0x36, 0x3f, 0xf7, 0xcc, 0x34, 0xa5, 0xe5, 0xf1, 0x71, 0xd8, 0x31, 0x15,
            0x04, 0xc7, 0x23, 0xc3, 0x18, 0x96, 0x05, 0x9a, 0x07, 0x12, 0x80, 0xe2, 0xeb, 0x27, 0xb2, 0x75,
            0x09, 0x83, 0x2c, 0x1a, 0x1b, 0x6e, 0x5a, 0xa0, 0x52, 0x3b, 0xd6, 0xb3, 0x29, 0xe3, 0x2f, 0x84,
            0x53, 0xd1, 0x00, 0xed, 0x20, 0xfc, 0xb1, 0x5b, 0x6a, 0xcb, 0xbe, 0x39, 0x4a, 0x4c, 0x58, 0xcf,
            0xd0, 0xef, 0xaa, 0xfb, 0x43, 0x4d, 0x33, 0x85, 0x45, 0xf9, 0x02, 0x7f, 0x50, 0x3c, 0x9f, 0xa8,
            0x51, 0xa3, 0x40, 0x8f, 0x92, 0x9d, 0x38, 0xf5, 0xbc, 0xb6, 0xda, 0x21, 0x10, 0xff, 0xf3, 0xd2,
            0xcd, 0x0c, 0x13, 0xec, 0x5f, 0x97, 0x44, 0x17, 0xc4, 0xa7, 0x7e, 0x3d, 0x64, 0x5d, 0x19, 0x73,
            0x60, 0x81, 0x4f, 0xdc, 0x22, 0x2a, 0x90, 0x88, 0x46, 0xee, 0xb8, 0x14, 0xde, 0x5e, 0x0b, 0xdb,
            0xe0, 0x32, 0x3a, 0x0a, 0x49, 0x06, 0x24, 0x5c, 0xc2, 0xd3, 0xac, 0x62, 0x91, 0x95, 0xe4, 0x79,
            0xe7, 0xc8, 0x37, 0x6d, 0x8d, 0xd5, 0x4e, 0xa9, 0x6c, 0x56, 0xf4, 0xea, 0x65, 0x7a, 0xae, 0x08,
            0xba, 0x78, 0x25, 0x2e, 0x1c, 0xa6, 0xb4, 0xc6, 0xe8, 0xdd, 0x74, 0x1f, 0x4b, 0xbd, 0x8b, 0x8a,
            0x70, 0x3e, 0xb5, 0x66, 0x48, 0x03, 0xf6, 0x0e, 0x61, 0x35, 0x57, 0xb9, 0x86, 0xc1, 0x1d, 0x9e,
            0xe1, 0xf8, 0x98, 0x11, 0x69, 0xd9, 0x8e, 0x94, 0x9b, 0x1e, 0x87, 0xe9, 0xce, 0x55, 0x28, 0xdf,
            0x8c, 0xa1, 0x89, 0x0d, 0xbf, 0xe6, 0x42, 0x68, 0x41, 0x99, 0x2d, 0x0f, 0xb0, 0x54, 0xbb, 0x16
        ]
        
        # Round constants para key expansion
        self.rcon = [
            0x8d, 0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1b, 0x36, 0x6c, 0xd8, 0xab, 0x4d, 0x9a
        ]
    
    def xor_bytes(self, a, b):
        """XOR entre dos arrays de bytes"""
        return [x ^ y for x, y in zip(a, b)]
    
    def sub_bytes(self, state):
        """Aplicar S-Box a cada byte del estado"""
        return [self.s_box[byte] for byte in state]
    
    def shift_rows(self, state):
        """Realizar ShiftRows en el estado"""
        # Convertir a matriz 4x4
        matrix = [state[i:i+4] for i in range(0, 16, 4)]
        
        # Shift rows correctamente: fila 0 sin cambio, fila 1 shift 1, fila 2 shift 2, fila 3 shift 3
        result = [0] * 16
        for row in range(4):
            for col in range(4):
                # Desplazar fila hacia la izquierda
                new_col = (col - row) % 4
                result[row * 4 + new_col] = matrix[row][col]
        
        return result
    
    def gf_mult(self, a, b):
        """Multiplicación en GF(2^8)"""
        if a == 0 or b == 0:
            return 0
        
        result = 0
        for i in range(8):
            if b & 1:
                result ^= a
            hi_bit_set = a & 0x80
            a <<= 1
            if hi_bit_set:
                a ^= 0x1b  # Polinomio irreducible
            b >>= 1
        
        return result & 0xff
    
    def mix_columns(self, state):
        """Realizar MixColumns en el estado"""
        # Matriz de MixColumns
        mix_matrix = [
            [0x02, 0x03, 0x01, 0x01],
            [0x01, 0x02, 0x03, 0x01],
            [0x01, 0x01, 0x02, 0x03],
            [0x03, 0x01, 0x01, 0x02]
        ]
        
        result = [0] * 16
        
        for col in range(4):
            for row in range(4):
                val = 0
                for k in range(4):
                    val ^= self.gf_mult(mix_matrix[row][k], state[k * 4 + col])
                result[row * 4 + col] = val
        
        return result
    
    def add_round_key(self, state, round_key):
        """Realizar AddRoundKey"""
        return self.xor_bytes(state, round_key)
    
    def rot_word(self, word):
        """Rotación de palabra para key expansion"""
        return word[1:] + word[:1]
    
    def sub_word(self, word):
        """Aplicar S-Box a una palabra"""
        return [self.s_box[byte] for byte in word]
    
    def key_expansion(self, key):
        """Expandir la clave de 128 bits a 11 round keys"""
        if len(key) != 16:
            raise ValueError("La clave debe ser de 128 bits (16 bytes)")
        
        w = []
        
        # Primeras 4 palabras son la clave original
        for i in range(4):
            w.append(key[i*4:(i+1)*4])
        
        # Generar las siguientes 40 palabras (10 rounds más)
        for i in range(4, 44):
            temp = w[i-1][:]
            
            if i % 4 == 0:
                temp = self.sub_word(self.rot_word(temp))
                temp[0] ^= self.rcon[i//4]
            
            w.append(self.xor_bytes(w[i-4], temp))
        
        # Convertir a round keys
        round_keys = []
        for i in range(11):
            round_key = []
            for j in range(4):
                round_key.extend(w[i*4 + j])
            round_keys.append(round_key)
        
        return round_keys
    
    def encrypt_block(self, plaintext, key):
        """Cifrar un bloque de 128 bits"""
        if len(plaintext) != 16:
            raise ValueError("El bloque debe ser de 128 bits (16 bytes)")
        
        round_keys = self.key_expansion(key)
        state = plaintext[:]
        
        # Round inicial
        state = self.add_round_key(state, round_keys[0])
        
        # 9 rounds principales
        for round_num in range(1, 10):
            state = self.sub_bytes(state)
            state = self.shift_rows(state)
            state = self.mix_columns(state)
            state = self.add_round_key(state, round_keys[round_num])
        
        # Round final
        state = self.sub_bytes(state)
        state = self.shift_rows(state)
        state = self.add_round_key(state, round_keys[10])
        
        return state
    
    def pad_data(self, data):
        """Aplicar PKCS#7 padding"""
        pad_length = 16 - (len(data) % 16)
        padding = bytes([pad_length] * pad_length)
        return data + padding
    
    def _process_key(self, key):
        """
        Procesar la clave para que sea de 16 bytes
        Acepta: 16 caracteres texto o 32 caracteres hexadecimal
        """
        if isinstance(key, bytes):
            if len(key) != 16:
                raise ValueError("La clave debe ser de 128 bits (16 bytes)")
            return key
        
        if isinstance(key, str):
            # Detectar si es hexadecimal (32 caracteres)
            if len(key) == 32 and all(c in '0123456789abcdefABCDEF' for c in key):
                try:
                    key_bytes = bytes.fromhex(key)
                    if len(key_bytes) != 16:
                        raise ValueError("La clave hexadecimal debe producir exactamente 16 bytes")
                    return key_bytes
                except ValueError as e:
                    if "invalid literal" in str(e):
                        raise ValueError("Formato hexadecimal inválido en la clave")
                    raise
            
            elif len(key) == 16:
                # Es clave de texto de 16 caracteres
                return key.encode('utf-8')
            
            else:
                raise ValueError("La clave debe tener 16 caracteres (texto) o 32 caracteres (hexadecimal)")
        
        raise ValueError("La clave debe ser string o bytes")

    def encrypt(self, data, key):
        """Cifrar datos usando AES 128 en modo ECB"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        # Procesar la clave
        key_bytes = self._process_key(key)
        
        # Aplicar padding
        padded_data = self.pad_data(data)
        
        # Cifrar por bloques
        encrypted_blocks = []
        for i in range(0, len(padded_data), 16):
            block = list(padded_data[i:i+16])
            encrypted_block = self.encrypt_block(block, list(key_bytes))
            encrypted_blocks.extend(encrypted_block)
        
        return bytes(encrypted_blocks) 