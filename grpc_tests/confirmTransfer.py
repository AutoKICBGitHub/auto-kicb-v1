import grpc
import json
from google.protobuf.json_format import MessageToDict
from grpc_tests.Protofiles.protofile_pb2_grpc import WebTransferApiStub
from grpc_tests.Protofiles.webTransferApi_pb2 import IncomingWebTransfer

# gRPC client setup (без сертификата для тестирования)
cert_file = 'path/to/ca_certificate.pem'  # Замените на путь к вашему сертификату

# Создайте SSL-сертификат

# Создайте защищенный канал
channel = grpc.secure_channel('newibanktest.kicb.net:443', grpc.ssl_channel_credentials())
client = WebTransferApiStub(channel)

# Metadata (формат строк для передачи)
metadata = (
    ('refid', 'daniyarRefIdSariev1234'),  # Убедитесь, что ключи метаданных правильные
    ('sessionkey', '6I1lbpdC0wocBgTjksQpOM'),
    ('device-type', 'ios'),
    ('user-agent-c', '12; iPhone12MaxProDan'),
)

# Data for the request
data = {
    "otp": "111111",
    "operationId": "bgWoZHeXa6FLVtv83lSSOB"
}

# Конструирование запроса
request = IncomingWebTransfer(
    code="CONFIRM_TRANSFER",
    data=json.dumps(data)  # Убедитесь, что это правильный формат данных
)

# Выполнение вызова gRPC
try:
    response = client.makeWebTransfer(request, metadata=metadata)
    response_dict = MessageToDict(response)
    print('Получен ответ от Query service:', response_dict)
except grpc.RpcError as e:
    print(f'Ошибка от Query service: {e.code()}, {e.details()}')
