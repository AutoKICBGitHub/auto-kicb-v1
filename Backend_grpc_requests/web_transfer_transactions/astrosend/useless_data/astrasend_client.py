import grpc
from typing import Dict, Any, Optional
import collections

# Заменяем относительные импорты на абсолютные
import astrasend_internal_api_pb2 as pb2
import astrasend_internal_api_pb2_grpc as pb2_grpc

# Создаем класс для хранения деталей вызова
_ClientCallDetails = collections.namedtuple(
    '_ClientCallDetails',
    ['method', 'timeout', 'metadata', 'credentials', 'wait_for_ready']
)

class RefidInterceptor(grpc.UnaryUnaryClientInterceptor):
    def __init__(self, refid):
        self.refid = refid
        
    def intercept_unary_unary(self, continuation, client_call_details, request):
        metadata = []
        if client_call_details.metadata is not None:
            metadata = list(client_call_details.metadata)
        metadata.append(('refid', self.refid))
        
        new_details = _ClientCallDetails(
            method=client_call_details.method,
            timeout=client_call_details.timeout,
            metadata=metadata,
            credentials=client_call_details.credentials,
            wait_for_ready=client_call_details.wait_for_ready
        )
        
        return continuation(new_details, request)

class AstrasendClient:
    """Клиент для работы с AstrasendInternalApi через gRPC."""
    
    def __init__(self, server_address: str, refid: str = None):
        """
        Инициализирует клиент AstrasendInternalApi.
        
        Args:
            server_address: Адрес gRPC сервера в формате 'host:port'
            refid: Уникальный идентификатор запроса
        """
        self.channel = grpc.insecure_channel(server_address)
        self.stub = pb2_grpc.AstrasendInternalApiStub(self.channel)
        self.refid = refid
    
    def close(self):
        """Закрывает gRPC канал."""
        self.channel.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def _create_iso_code(self, country_code: str, currency_code: str) -> pb2.IsoCode:
        """Создает объект IsoCode."""
        return pb2.IsoCode(countryCode=country_code, currencyCode=currency_code)
    
    def _create_name(self, first_name: str, middle_name: str = "", last_name: str = "") -> pb2.Name:
        """Создает объект Name."""
        return pb2.Name(firstName=first_name, middleName=middle_name, lastName=last_name)
    
    def _create_address(self, addr_line1: str, city: str, postal_code: str = "", 
                        country: str = "", addr_line2: str = "") -> pb2.Address:
        """Создает объект Address."""
        return pb2.Address(
            addrLine1=addr_line1,
            city=city,
            postalCode=postal_code,
            country=country,
            addrLine2=addr_line2
        )
    
    def _create_passport(self, passport_type: str, number: str, issue_date: str,
                         country_of_issue: str, expired_date: str, is_expired: bool = False) -> pb2.Passport:
        """Создает объект Passport."""
        return pb2.Passport(
            type=passport_type,
            number=number,
            issueDate=issue_date,
            countryOfIssue=country_of_issue,
            expiredDate=expired_date,
            isExpired=is_expired
        )
    
    def _create_financials(self, originators_principal_amount: float, destination_principal_amount: float,
                          pay_amount: float, agent_fee: float) -> pb2.Financials:
        """Создает объект Financials."""
        return pb2.Financials(
            originatorsPrincipalAmount=originators_principal_amount,
            destinationPrincipalAmount=destination_principal_amount,
            payAmount=pay_amount,
            agentFee=agent_fee
        )
    
    def search_receive_money(self, mtcn: str = "", kicb_ref_no: str = "") -> Dict[str, Any]:
        """
        Поиск транзакции по MTCN или KICB Reference Number.
        
        Args:
            mtcn: Money Transfer Control Number
            kicb_ref_no: KICB Reference Number
            
        Returns:
            Словарь с результатами поиска
        """
        request = pb2.SearchReceiveMoneyRequest(mtcn=mtcn, kicbRefNo=kicb_ref_no)
        response = self.stub.searchReceiveMoney(request)
        
        # Преобразуем ответ в словарь для удобства использования
        result = {
            "success": response.success
        }
        
        if response.success:
            data = response.data
            result["data"] = {
                "sender": {
                    "name": {
                        "firstName": data.sender.name.firstName,
                        "middleName": data.sender.name.middleName,
                        "lastName": data.sender.name.lastName
                    },
                    "contactPhone": data.sender.contactPhone
                },
                "receiver": {
                    "name": {
                        "firstName": data.receiver.name.firstName,
                        "middleName": data.receiver.name.middleName,
                        "lastName": data.receiver.name.lastName
                    }
                },
                "financials": {
                    "originatorsPrincipalAmount": data.financials.originatorsPrincipalAmount,
                    "destinationPrincipalAmount": data.financials.destinationPrincipalAmount,
                    "payAmount": data.financials.payAmount,
                    "agentFee": data.financials.agentFee
                },
                "paymentDetails": {
                    "originatingCountryCurrency": {
                        "countryCode": data.paymentDetails.originatingCountryCurrency.isoCode.countryCode,
                        "currencyCode": data.paymentDetails.originatingCountryCurrency.isoCode.currencyCode
                    },
                    "destinationCountryCurrency": {
                        "countryCode": data.paymentDetails.destinationCountryCurrency.isoCode.countryCode,
                        "currencyCode": data.paymentDetails.destinationCountryCurrency.isoCode.currencyCode
                    },
                    "originatingCity": data.paymentDetails.originatingCity,
                    "exchangeRate": data.paymentDetails.exchangeRate,
                    "fixOnSend": data.paymentDetails.fixOnSend
                },
                "filingDate": data.filingDate,
                "filingTime": data.filingTime,
                "payStatusDescription": data.payStatusDescription,
                "mtcn": data.mtcn,
                "newMtcn": data.newMtcn,
                "paidDate": data.paidDate,
                "paidTime": data.paidTime
            }
        else:
            result["error"] = {
                "code": response.error.code,
                "data": response.error.data
            }
        
        return result
    
    def receive_money_pay(self, receiver_data: Dict[str, Any], transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Выполняет выплату денежного перевода.
        
        Args:
            receiver_data: Данные получателя
            transaction_data: Данные транзакции
            
        Returns:
            Словарь с результатами операции
        """
        # Создаем объекты для запроса
        receiver_name = self._create_name(
            first_name=receiver_data.get("firstName", ""),
            middle_name=receiver_data.get("middleName", ""),
            last_name=receiver_data.get("lastName", "")
        )
        
        receiver_passport = self._create_passport(
            passport_type=receiver_data.get("passportType", ""),
            number=receiver_data.get("passportNumber", ""),
            issue_date=receiver_data.get("passportIssueDate", ""),
            country_of_issue=receiver_data.get("passportCountryOfIssue", ""),
            expired_date=receiver_data.get("passportExpiredDate", ""),
            is_expired=receiver_data.get("isPassportExpired", False)
        )
        
        receiver_address = self._create_address(
            addr_line1=receiver_data.get("addrLine1", ""),
            city=receiver_data.get("city", ""),
            country=receiver_data.get("country", "")
        )
        
        # Создаем объекты CountryCurrency напрямую, без использования IsoCode
        origin_country_currency = pb2.CountryCurrency(
            countryCode=transaction_data.get("originCountryCode", ""),
            currencyCode=transaction_data.get("originCurrencyCode", "")
        )
        
        dest_country_currency = pb2.CountryCurrency(
            countryCode=transaction_data.get("destCountryCode", ""),
            currencyCode=transaction_data.get("destCurrencyCode", "")
        )
        
        original_dest_country_currency = pb2.CountryCurrency(
            countryCode=transaction_data.get("originalDestCountryCode", ""),
            currencyCode=transaction_data.get("originalDestCurrencyCode", "")
        )
        
        financials = pb2.Financials(
            originatorsPrincipalAmount=transaction_data.get("originatorsPrincipalAmount", 0.0),
            destinationPrincipalAmount=transaction_data.get("destinationPrincipalAmount", 0.0),
            payAmount=transaction_data.get("payAmount", 0.0),
            agentFee=transaction_data.get("agentFee", 0.0)
        )
        
        # Создаем запрос
        request = pb2.ReceiveMoneyPayRequest(
            receiverName=receiver_name,
            receiverPassport=receiver_passport,
            receiverAddress=receiver_address,
            receiverBirthDate=receiver_data.get("birthDate", ""),
            receiverBirthPlace=receiver_data.get("birthPlace", ""),
            marketingFlag=receiver_data.get("marketingFlag", ""),
            receiverEmail=receiver_data.get("email", ""),
            receiverPhoneNumber=receiver_data.get("phoneNumber", ""),
            receiverAccountNo=receiver_data.get("accountNo", ""),
            originatingCountryCurrency=origin_country_currency,
            originatingCity=transaction_data.get("originatingCity", ""),
            fixOnSend=transaction_data.get("fixOnSend", ""),
            exchangeRate=transaction_data.get("exchangeRate", 0.0),
            destinationCountryCurrency=dest_country_currency,
            originalDestinationCountryCurrency=original_dest_country_currency,
            financials=financials,
            mtcn=transaction_data.get("mtcn", ""),
            newMtcn=transaction_data.get("newMtcn", ""),
            kicbRefNo=transaction_data.get("kicbRefNo", ""),
            isPersonalDataConfirmed=transaction_data.get("isPersonalDataConfirmed", False)
        )
        
        # Создаем метаданные с refid
        metadata = []
        if self.refid:
            metadata.append(("refid", self.refid))
        
        # Вызываем метод с метаданными
        response = self.stub.receiveMoneyPay(request, metadata=metadata)
        
        # Преобразуем ответ в словарь
        result = {
            "success": response.success
        }
        
        if response.success:
            data = response.data
            result["data"] = {
                "financials": {
                    "originatorsPrincipalAmount": data.financials.originatorsPrincipalAmount,
                    "destinationPrincipalAmount": data.financials.destinationPrincipalAmount,
                    "payAmount": data.financials.payAmount,
                    "agentFee": data.financials.agentFee
                },
                "mtcn": data.mtcn,
                "newMtcn": data.newMtcn,
                "paidDate": data.paidDate,
                "paidTime": data.paidTime,
                "settlementDate": data.settlementDate
            }
        else:
            result["error"] = {
                "code": response.error.code,
                "data": response.error.data
            }
        
        return result
    
    def pay_status(self, mtcn: str = "", new_mtcn: str = "", kicb_ref_no: str = "", refid: str = "") -> Dict[str, Any]:
        """
        Проверяет статус платежа.
        
        Args:
            mtcn: Money Transfer Control Number
            new_mtcn: Новый Money Transfer Control Number
            kicb_ref_no: KICB Reference Number
            refid: Уникальный идентификатор запроса
            
        Returns:
            Словарь со статусом платежа
        """
        request = pb2.PayStatusRequest(mtcn=mtcn, newMtcn=new_mtcn, kicbRefNo=kicb_ref_no)
        
        # Создаем метаданные с refid
        metadata = []
        if refid:
            metadata.append(("refid", refid))
        elif self.refid:
            metadata.append(("refid", self.refid))
        
        # Вызываем метод с метаданными
        response = self.stub.payStatus(request, metadata=metadata)
        
        # Преобразуем ответ в словарь
        result = {
            "success": response.success
        }
        
        if response.success:
            data = response.data
            result["data"] = {
                "sender": {
                    "name": {
                        "firstName": data.sender.name.firstName,
                        "middleName": data.sender.name.middleName,
                        "lastName": data.sender.name.lastName
                    },
                    "contactPhone": data.sender.contactPhone
                },
                "receiver": {
                    "name": {
                        "firstName": data.receiver.name.firstName,
                        "middleName": data.receiver.name.middleName,
                        "lastName": data.receiver.name.lastName
                    }
                },
                "financials": {
                    "originatorsPrincipalAmount": data.financials.originatorsPrincipalAmount,
                    "destinationPrincipalAmount": data.financials.destinationPrincipalAmount,
                    "payAmount": data.financials.payAmount,
                    "agentFee": data.financials.agentFee
                },
                "paymentDetails": {
                    "originatingCountryCurrency": {
                        "countryCode": data.paymentDetails.originatingCountryCurrency.isoCode.countryCode,
                        "currencyCode": data.paymentDetails.originatingCountryCurrency.isoCode.currencyCode
                    },
                    "destinationCountryCurrency": {
                        "countryCode": data.paymentDetails.destinationCountryCurrency.isoCode.countryCode,
                        "currencyCode": data.paymentDetails.destinationCountryCurrency.isoCode.currencyCode
                    },
                    "originatingCity": data.paymentDetails.originatingCity,
                    "exchangeRate": data.paymentDetails.exchangeRate,
                    "fixOnSend": data.paymentDetails.fixOnSend
                },
                "filingDate": data.filingDate,
                "filingTime": data.filingTime,
                "payStatusDescription": data.payStatusDescription,
                "mtcn": data.mtcn,
                "newMtcn": data.newMtcn,
                "paidDate": data.paidDate,
                "paidTime": data.paidTime
            }
        else:
            result["error"] = {
                "code": response.error.code,
                "data": response.error.data
            }
        
        return result 