# utils.py
# This will hold utility functions for your application
from google.cloud import secretmanager
from cryptography.fernet import Fernet

def get_secret(secret_id, version_id="latest"):
    client = secretmanager.SecretManagerServiceClient()
    secret_name = f"projects/arcs-391022/secrets/{secret_id}/versions/{version_id}"
    response = client.access_secret_version(request={"name": secret_name})
    return response.payload.data.decode('UTF-8')

cipher_suite = Fernet(get_secret("FERNET_KEY"))

def encrypt(data: str) -> str:
    encoded_data = data.encode()
    encrypted_data = cipher_suite.encrypt(encoded_data)
    return encrypted_data.decode()

def decrypt(data: str) -> str:
    encrypted_data = data.encode()
    decrypted_data = cipher_suite.decrypt(encrypted_data)
    return decrypted_data.decode()
