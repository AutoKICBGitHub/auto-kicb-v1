# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: webTransferApi.proto
# Protobuf Python Version: 5.27.2
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    27,
    2,
    '',
    'webTransferApi.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x14webTransferApi.proto\x12\x10web_transfer_api\"1\n\x13IncomingWebTransfer\x12\x0c\n\x04\x63ode\x18\x01 \x01(\t\x12\x0c\n\x04\x64\x61ta\x18\x02 \x01(\t\"]\n\x13OutgoingWebTransfer\x12\x0f\n\x07success\x18\x01 \x01(\x08\x12\x0c\n\x04\x64\x61ta\x18\x02 \x01(\t\x12\'\n\x05\x65rror\x18\x03 \x01(\x0b\x32\x18.web_transfer_api.Error2\"$\n\x06\x45rror2\x12\x0c\n\x04\x63ode\x18\x01 \x01(\t\x12\x0c\n\x04\x64\x61ta\x18\x02 \x01(\t2s\n\x0eWebTransferApi\x12\x61\n\x0fmakeWebTransfer\x12%.web_transfer_api.IncomingWebTransfer\x1a%.web_transfer_api.OutgoingWebTransfer\"\x00\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'webTransferApi_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_INCOMINGWEBTRANSFER']._serialized_start=42
  _globals['_INCOMINGWEBTRANSFER']._serialized_end=91
  _globals['_OUTGOINGWEBTRANSFER']._serialized_start=93
  _globals['_OUTGOINGWEBTRANSFER']._serialized_end=186
  _globals['_ERROR2']._serialized_start=188
  _globals['_ERROR2']._serialized_end=224
  _globals['_WEBTRANSFERAPI']._serialized_start=226
  _globals['_WEBTRANSFERAPI']._serialized_end=341
# @@protoc_insertion_point(module_scope)