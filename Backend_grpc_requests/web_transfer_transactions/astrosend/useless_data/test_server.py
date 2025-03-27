import grpc
from concurrent import futures
import time
import astrasend_internal_api_pb2 as pb2
import astrasend_internal_api_pb2_grpc as pb2_grpc

class AstrasendInternalApiServicer(pb2_grpc.AstrasendInternalApiServicer):
    def searchReceiveMoney(self, request, context):
        # Тестовый ответ
        response = pb2.SearchReceiveMoneyResponse(success=True)
        
        # Создаем тестовые данные
        sender_name = pb2.Name(firstName="YAROSLAV", middleName="", lastName="BORISOV")
        sender_address = pb2.Address(addrLine1="GARDENIA AVE 29", city="NURAFSHON", postalCode=106058, country="UZB")
        sender_compliance = pb2.ComplianceDetails(currentAddress=sender_address)
        sender = pb2.Sender(name=sender_name, complianceDetails=sender_compliance, contactPhone="79334444420")
        
        receiver_name = pb2.Name(firstName="NURLAN", middleName="BAKYNBEKOVIC", lastName="AITBAEV")
        receiver = pb2.Receiver(name=receiver_name)
        
        financials = pb2.Financials(
            originatorsPrincipalAmount=1765,
            destinationPrincipalAmount=171700,
            payAmount=171700,
            agentFee=0
        )
        
        origin_iso = pb2.IsoCode(countryCode="UZB", currencyCode="USD")
        dest_iso = pb2.IsoCode(countryCode="KGZ", currencyCode="RUB")
        origin_country_currency = pb2.CountryCurrency(isoCode=origin_iso)
        dest_country_currency = pb2.CountryCurrency(isoCode=dest_iso)
        original_dest_country_currency = pb2.CountryCurrency(isoCode=dest_iso)
        
        payment_details = pb2.PaymentDetails(
            originatingCountryCurrency=origin_country_currency,
            destinationCountryCurrency=dest_country_currency,
            originatingCity="Andizhan",
            exchangeRate=0.01027956,
            fixOnSend="Y",
            originalDestinationCountryCurrency=original_dest_country_currency
        )
        
        data = pb2.PaymentTransactionData(
            sender=sender,
            receiver=receiver,
            financials=financials,
            paymentDetails=payment_details,
            filingDate="9012025",
            filingTime="09:08:02",
            payStatusDescription="WILL CALL",
            mtcn="3142256907",
            newMtcn="090120253142256907"
        )
        
        response.data.CopyFrom(data)
        return response
    
    def receiveMoneyPay(self, request, context):
        # Тестовый ответ
        response = pb2.ReceiveMoneyPayResponse(success=True)
        
        financials = pb2.Financials(
            originatorsPrincipalAmount=request.financials.originatorsPrincipalAmount,
            destinationPrincipalAmount=request.financials.destinationPrincipalAmount,
            payAmount=request.financials.payAmount,
            agentFee=request.financials.agentFee
        )
        
        data = pb2.ReceiveMoneyPayData(
            financials=financials,
            mtcn=request.mtcn,
            newMtcn=request.newMtcn,
            paidDate="24032025",
            paidTime="12:00:00",
            settlementDate="24032025"
        )
        
        response.data.CopyFrom(data)
        return response
    
    def payStatus(self, request, context):
        # Тестовый ответ (аналогичный searchReceiveMoney, но с обновленным статусом)
        response = pb2.PayStatusResponse(success=True)
        
        # Создаем тестовые данные (аналогично searchReceiveMoney)
        sender_name = pb2.Name(firstName="YAROSLAV", middleName="", lastName="BORISOV")
        sender_address = pb2.Address(addrLine1="GARDENIA AVE 29", city="NURAFSHON", postalCode=106058, country="UZB")
        sender_compliance = pb2.ComplianceDetails(currentAddress=sender_address)
        sender = pb2.Sender(name=sender_name, complianceDetails=sender_compliance, contactPhone="79334444420")
        
        receiver_name = pb2.Name(firstName="NURLAN", middleName="BAKYNBEKOVIC", lastName="AITBAEV")
        receiver = pb2.Receiver(name=receiver_name)
        
        financials = pb2.Financials(
            originatorsPrincipalAmount=1765,
            destinationPrincipalAmount=171700,
            payAmount=171700,
            agentFee=0
        )
        
        origin_iso = pb2.IsoCode(countryCode="UZB", currencyCode="USD")
        dest_iso = pb2.IsoCode(countryCode="KGZ", currencyCode="RUB")
        origin_country_currency = pb2.CountryCurrency(isoCode=origin_iso)
        dest_country_currency = pb2.CountryCurrency(isoCode=dest_iso)
        original_dest_country_currency = pb2.CountryCurrency(isoCode=dest_iso)
        
        payment_details = pb2.PaymentDetails(
            originatingCountryCurrency=origin_country_currency,
            destinationCountryCurrency=dest_country_currency,
            originatingCity="Andizhan",
            exchangeRate=0.01027956,
            fixOnSend="Y",
            originalDestinationCountryCurrency=original_dest_country_currency
        )
        
        data = pb2.PaymentTransactionData(
            sender=sender,
            receiver=receiver,
            financials=financials,
            paymentDetails=payment_details,
            filingDate="9012025",
            filingTime="09:08:02",
            payStatusDescription="PAID",  # Обновленный статус
            mtcn=request.mtcn,
            newMtcn=request.newMtcn,
            paidDate="24032025",
            paidTime="12:00:00"
        )
        
        response.data.CopyFrom(data)
        return response

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb2_grpc.add_AstrasendInternalApiServicer_to_server(AstrasendInternalApiServicer(), server)
    server.add_insecure_port('localhost:50113')
    server.start()
    print("Тестовый сервер запущен на порту 50113")
    try:
        while True:
            time.sleep(86400)  # Один день в секундах
    except KeyboardInterrupt:
        server.stop(0)
        print("Сервер остановлен")

if __name__ == '__main__':
    serve() 