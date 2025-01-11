# grpc_setup.py
import grpc
import uuid
import json
from protofile_pb2_grpc import WebIntegrationApiStub, WebTransferApiStub

# Путь к JSON файлу
json_file_path = 'C:\\project_kicb\\Backend_grpc_requests\\data.json'

# Чтение данных из JSON файла
with open(json_file_path, 'r', encoding='utf-8') as json_file:
    json_data = json.load(json_file)

# Создание SSL credentials
credentials = grpc.ssl_channel_credentials()

# Создание защищенного канала с SSL
channel = grpc.secure_channel(
    'newibanktest.kicb.net:443',
    credentials,
    options=(('grpc.ssl_target_name_override', 'newibanktest.kicb.net'),)
)

# Создание клиентов
integration_client = WebIntegrationApiStub(channel)
transfer_client = WebTransferApiStub(channel)

def get_metadata():
    return [
        ('sessionkey', json_data['grpc_session_key']),
        ('device-type', json_data['grpc_device_type']),
        ('ref-id', str(uuid.uuid4())),
        ('x-real-ip', json_data['grpc_x_real_ip']),
        ('user-agent-c', json_data['grpc_user_agent_c']),
        ('app-type', json_data['grpc_app_type']),
        ('imei', json_data['grpc_imei']),
        ('user-id', json_data['grpc_user_id']),
        ('customer-no', json_data['grpc_customer_no']),
    ]
