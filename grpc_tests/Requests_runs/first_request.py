import grpc
import json
from google.protobuf.json_format import MessageToDict
from grpc_tests.protofile_pb2_grpc import WebTransferApiStub
from grpc_tests.webTransferApi_pb2 import IncomingWebTransfer

async def make_request(uuid, operation_data):
    async with grpc.aio.secure_channel('newibanktest.kicb.net:443', grpc.ssl_channel_credentials()) as channel:
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
            "operationId": uuid,
            "accountIdDebit": operation_data['accountIdDebit'],
            "accountCreditPropValue": '1285090000630562',
            "accountCreditPropType": 'ACCOUNT_NO',
            "paymentPurpose": 'Payment for services',
            "amountDebit": '3000.30',
            "valueDate": None,
            "knp": None,
            "theirRefNo": None,
            "valueTime": None,
            "txnId": None,
            "qrPayment": True,
            "qrAccountChangeable": False,
            "qrComment": 'Payment for services',
            "qrServiceName": 'KICB',
            "qrServiceId": '01',
            "clientType": '1',
            "qrVersion": '01',
            "qrType": 'STATIC',
            "qrMerchantProviderId": 'p2p.kicb.net',
            "qrMerchantId": None,
            "qrAccount": '1285090000630562',
            "qrMcc": '9999',
            "qrCcy": '417',
            "qrTransactionId": 'Test 1',
            "qrControlSum": 'c560'
        }

        request = IncomingWebTransfer(
            code="MAKE_BANK_CLIENT_TRANSFER",
            data=json.dumps(data)
        )

        try:
            # Выполняем запрос и преобразуем ответ в словарь
            response = await client.makeWebTransfer(request, metadata=metadata)  # Ожидаем ответ
            response_dict = MessageToDict(response)
            print('Получен ответ от Query service:', response_dict)
            return response_dict, request  # Возвращаем словарь ответа

        except grpc.RpcError as e:
            print(f'Ошибка от Query service: {e.code()}, {e.details()}')
            return {'error': {'code': e.code(), 'details': e.details(), 'requestBody': request}}, request  # Возвращаем ошибку и запрос
