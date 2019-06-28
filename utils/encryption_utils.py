import base64
from Crypto.Cipher import AES


class AESEncryption(object):

    @staticmethod
    def encrypt(key, encryption_string):
        cipher = AES.new(key, AES.MODE_ECB)

        padded_string = AESEncryption._pad(encryption_string)
        encrypted_string = cipher.encrypt(padded_string)
        return base64.urlsafe_b64encode(encrypted_string)

    @staticmethod
    def decrypt(key, decryption_string):
        cipher = AES.new(key, AES.MODE_ECB)
        decrypted = cipher.decrypt(base64.b64decode(decryption_string))
        return AESEncryption._unpad(decrypted)

    @staticmethod
    def _pad(otp):
        '''
        pad the otp with a block size of 16
        '''
        bs = 16
        return otp + (bs - len(otp) % bs) * chr(bs - len(otp) % bs)

    @staticmethod
    def _unpad(decrypted_msg):
        return decrypted_msg[:-ord(decrypted_msg[len(decrypted_msg)-1:])]
