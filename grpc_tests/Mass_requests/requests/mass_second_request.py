import grpc
import json
from google.protobuf.json_format import MessageToDict
from grpc_tests.protofile_pb2_grpc import WebTransferApiStub
from grpc_tests.webTransferApi_pb2 import IncomingWebTransfer

async def make_request(uuid, result):
    async with grpc.aio.secure_channel('newibanktest.kicb.net:443', grpc.ssl_channel_credentials()) as channel:
        client = WebTransferApiStub(channel)

        # Metadata: Используем refid и sessionkey из operation_data
        metadata = (
            ('refid', "test"),
            ('sessionkey', result['sessionkey']),
            ('device-type', 'ios'),
            ('user-agent-c', '12; iPhone12MaxProDan'),
        )

        # Используем данные из operation_data
        data = {
            "otp": "111111",
            "operationId": uuid
        }

        request = IncomingWebTransfer(
            code="CONFIRM_TRANSFER",
            data=json.dumps(data)
        )

        try:
            # Выполняем gRPC запрос
            response = await client.makeWebTransfer(request, metadata=metadata)  # Ожидаем ответ
            response_dict = MessageToDict(response)  # Преобразуем ответ в словарь
            print('Получен ответ от Query service:', response_dict)
            return response_dict, request  # Возвращаем ответ для дальнейшего использования

        except grpc.RpcError as e:
            # Обрабатываем ошибки RPC
            print(f'Ошибка от Query service: {e.code()}, {e.details()}')
            return {'error': {'code': e.code(), 'details': e.details(), 'requestBody': request}}  # Исправлено
