import grpc
import json
from google.protobuf.json_format import MessageToDict
from protofile_pb2_grpc import WebTransferApiStub
from webTransferApi_pb2 import IncomingWebTransfer

def make_request(uuid, operation_data):
    channel = grpc.secure_channel('newibanktest.kicb.net:443', grpc.ssl_channel_credentials())
    client = WebTransferApiStub(channel)

    # Metadata: Используем refid и sessionkey из operation_data
    metadata = (
        ('refid', operation_data['refid']),
        ('sessionkey', operation_data['sessionkey']),
        ('device-type', 'ios'),
        ('user-agent-c', '12; iPhone12MaxProDan'),
    )

    # Используем данные из operation_data
    data = {
        "operationId": uuid,
        "accountIdDebit": operation_data['accountIdDebit'],
        "accountCreditPropValue": operation_data['accountCreditPropValue'],
        "accountCreditPropType": operation_data['accountCreditPropType'],
        "paymentPurpose": operation_data['paymentPurpose'],
        "amountDebit": operation_data['amountDebit'],
        "valueDate": None,
        "knp": None,
        "theirRefNo": None,
        "valueTime": None,
        "txnId": None,
        "qrPayment": operation_data['qrPayment'],
        "qrAccountChangeable": operation_data['qrAccountChangeable'],
        "qrComment": operation_data['qrComment'],
        "qrServiceName": operation_data['qrServiceName'],
        "qrServiceId": operation_data['qrServiceId'],
        "clientType": operation_data['clientType'],
        "qrVersion": operation_data['qrVersion'],
        "qrType": operation_data['qrType'],
        "qrMerchantProviderId": operation_data['qrMerchantProviderId'],
        "qrMerchantId": operation_data['qrMerchantId'],
        "qrAccount": operation_data['qrAccount'],
        "qrMcc": operation_data['qrMcc'],
        "qrCcy": operation_data['qrCcy'],
        "qrTransactionId": operation_data['qrTransactionId'],
        "qrControlSum": operation_data['qrControlSum']
    }

    request = IncomingWebTransfer(
        code="MAKE_BANK_CLIENT_TRANSFER",
        data=json.dumps(data)
    )

    try:
        response = client.makeWebTransfer(request, metadata=metadata)
        response_dict = MessageToDict(response)
        print('Получен ответ от Query service:', response_dict)
    except grpc.RpcError as e:
        print(f'Ошибка от Query service: {e.code()}, {e.details()}')
