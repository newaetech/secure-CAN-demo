from Crypto.Cipher import AES

class secure_can():
    def __init__(self):
        self.auth_key = str(bytearray( range(0, 16) ))
        self.enc_key = str(bytearray( [ 0x21, 0x7E, 0x15, 0x16, 0x28, 0xAE, 0xD2, 0xA6, 0xAB, 0xF7, 0x15, 0x88, 0x09, 0xCF, 0x4F, 0x3C ]))
        self.auth_iv = str(bytearray( [0x01, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88, 0x99, 0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF]))
        
    #returns payload based on data, id, and cnt
    def encrypt(self, msg_data, msg_id, msg_cnt):
        enc_ecb = AES.new(self.enc_key, AES.MODE_ECB)
        enc_mac = AES.new(self.auth_key, AES.MODE_CBC, self.auth_iv)

        nonce = [(msg_cnt >> 16) &0xff, (msg_cnt >> 8) & 0xff, msg_cnt & 0xff]
        nonce.extend( [ (msg_id >> 8) & 0xff, msg_id & 0xff ] )
        nonce_auth = nonce[:]
        nonce_ctr = nonce[:]

        nonce_auth.extend([0] * 7)
        nonce_auth.extend(msg_data)
        
        #Nonce ctr tag - no data
        nonce_ctr.extend( [0] * 11 )
        
        mac = enc_mac.encrypt(str(bytearray(nonce_auth)))
        mac = list(bytearray(mac))
        
        ctr_out = enc_ecb.encrypt(str(bytearray(nonce_ctr)))
        ctr_out = list(bytearray(ctr_out))
        payload = [0] * 8

        for i in range(0, 4):
            payload[i] = ctr_out[i+8] ^ msg_data[i]
            payload[i + 4] = ctr_out[i+12] ^ mac[i]
        
        return payload
            
    #returns (data, auth_passed) based on payload, id, and cnt
    def decrypt(self, payload, msg_id, msg_cnt):
        enc_ecb = AES.new(self.enc_key, AES.MODE_ECB)
        enc_mac = AES.new(self.auth_key, AES.MODE_CBC, self.auth_iv)
        
        nonce = [(msg_cnt >> 16) &0xff, (msg_cnt >> 8) & 0xff, msg_cnt & 0xff]
        nonce.extend( [ (msg_id >> 8) & 0xff, msg_id & 0xff ] )
        nonce_ctr = nonce[:]
        nonce_auth = nonce[:]
        
        nonce_ctr.extend( [0] * 11 )
        ctr_out = enc_ecb.encrypt(str(bytearray(nonce_ctr)))
        ctr_out = list(bytearray(ctr_out))
        
        data = [0] * 4
        for i in range(0, 4):
            data[i] = payload[i] ^ ctr_out[i + 8]
            
        nonce_auth.extend([0] * 7)
        nonce_auth.extend(data)
        
        mac = enc_mac.encrypt(str(bytearray(nonce_auth)))
        mac = list(bytearray(mac))
        
        tag_enc = [ctr_out[i+12] ^ mac[i] for i in range(0, 4)]
        
        return (data, cmp(payload[4:], tag_enc) == 0)
        
    #returns ext_id from a msg_id and msg_cnt
    def ext_id(self, msg_id, msg_cnt):
        ret = msg_id & 0x7FF
        ret |= (msg_cnt << 11) & 0x1FFFF800
        return ret
    
    #returns [msg_id, msg_cnt] from an ext_id
    def get_id_cnt(self, ext_id):
        return [ext_id & 0x7FF, (ext_id >> 11) & 0x3FFFF]
        pass