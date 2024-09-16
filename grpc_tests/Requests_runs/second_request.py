import grpc
import json
from google.protobuf.json_format import MessageToDict
from grpc_tests.protofile_pb2_grpc import WebTransferApiStub
from grpc_tests.webTransferApi_pb2 import IncomingWebTransfer

def make_request(uuid, operation_data):
    channel = grpc.secure_channel('newibanktest.kicb.net:443', grpc.ssl_channel_credentials())
    client = WebTransferApiStub(channel)

    # Metadata: Используем refid и sessionkey из operation_data
    metadata = (
        ('refid', "test"),
        ('sessionkey', operation_data['sessionkey']),
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
        # Make the gRPC request
        response = client.makeWebTransfer(request, metadata=metadata)
        response_dict = MessageToDict(response)  # Convert response to a dictionary
        print('Получен ответ от Query service:', response_dict)
        return response_dict  # Return the response for further use

    except grpc.RpcError as e:
        # Handle RPC errors
        print(f'Ошибка от Query service: {e.code()}, {e.details()}')
        return {'error': {'code': e.code(), 'details': e.details()}}