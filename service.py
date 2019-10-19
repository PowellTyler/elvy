from Crypto.Cipher import AES
from os.path import isfile
from db import Session
import string
import random
from __init__ import config

__all__ = (
    'add_password',
    'get_passwords',
    'set_passphrase',
    'validate_passphrase',
    'is_passphrase_set'
)


def add_password(passphrase='', password='', association=None):
    if not validate_passphrase(passphrase):
        return {'error': 'Invalid passphrase'}

    with Session() as session:
        if association == 'MAIN':
            return {'error': 'MAIN is an invalid association'}
        iv_list = session.get_iv_list()
        # In some situations a generated iv will create an encrypted password that is difficult to store in the database,
        # so instead this continues to try different iv's until one works
        while True:
            while True:
                iv = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for _ in range(16))
                if iv not in iv_list:
                    break
            aes = AES.new(passphrase, AES.MODE_CBC, iv)
            padding_count = 16 - len(password) % 16
            p = str(('#' * padding_count) + password)
            encrypted_password = aes.encrypt(p)
            encrypted_password = str(encrypted_password)[2:-1].replace('\\', '\\\\')
            try:
                session.create_row(encrypted_password, iv, padding_count, association)
                break
            except Exception:
                pass


def get_passwords(passphrase, associations=None):
    """
    Gets every saved password with given associations
    """
    if not validate_passphrase(passphrase):
        return {'error': 'Invalid passphrase'}
    passwords = []
    with Session() as session:
        rows = session.filter(associations)
        for id, association, password, padding, iv in rows:
            aes = AES.new(passphrase, AES.MODE_CBC, iv)
            padding = int(padding)
            password_bytes = password.replace('\\\\', '\\').encode().decode('unicode-escape').encode('ISO-8859-1')
            passwords.append({
                'association': association,
                'password': aes.decrypt(password_bytes)[padding:].decode(),
                'id': str(id)
            })
    return passwords


def delete_password(passphrase, id=0):
    """
    Deletes password by its id
    """
    if not validate_passphrase(passphrase):
        return {'error': 'Invalid passphrase'}
    with Session() as session:
        session.delete_row(id)


def set_passphrase(passphrase):
    """
    Sets the passphrase
    """
    if not len(passphrase) == 16:
        return {'error': 'passphrase must be 16 characters long'}
    
    with Session() as session:
        iv_list = session.get_iv_list()
        while True:
            iv = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for _ in range(16))
            if iv not in iv_list:
                break
        if session.get_main():
            return {'error': 'passphrase has already been set'}
        aes = AES.new(passphrase, AES.MODE_CBC, iv)
        encrypted_password = aes.encrypt(passphrase)
        encrypted_password = str(encrypted_password)[2:-1].replace('\\', '\\\\')
        session.create_row(encrypted_password, iv, association='MAIN')

    return {'message': 'Passphrase set'}


def validate_passphrase(passphrase):
    """
    Returns true if passphrase is valid
    """
    if not len(passphrase) == 16:
        return False

    with Session() as session:
        main = session.get_main()
        if not main:
            return False
        
    aes = AES.new(passphrase, AES.MODE_CBC, main[4])
    encrypted_password = aes.encrypt(passphrase)
    encrypted_password = str(encrypted_password)[2:-1].replace('\\', '\\\\')

    return main[2] == encrypted_password


def is_passphrase_set():
    """
    Return true 
    """
    with Session() as session:
        main = session.get_main()
        return False if not main else True
