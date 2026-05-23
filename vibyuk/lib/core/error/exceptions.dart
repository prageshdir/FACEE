import 'package:dio/dio.dart';

sealed class AppException implements Exception {
  final String message;
  final String? code;

  const AppException({required this.message, this.code});

  @override
  String toString() => 'AppException(message: $message, code: $code)';
}

final class NetworkException extends AppException {
  final int? statusCode;
  final dynamic data;

  const NetworkException({
    required super.message,
    super.code,
    this.statusCode,
    this.data,
  });

  factory NetworkException.fromDioException(DioException e) {
    switch (e.type) {
      case DioExceptionType.connectionTimeout:
      case DioExceptionType.sendTimeout:
      case DioExceptionType.receiveTimeout:
        return NetworkException(
          message: 'Connection timed out. Please check your internet connection.',
          code: 'TIMEOUT',
          statusCode: e.response?.statusCode,
        );
      case DioExceptionType.badResponse:
        return NetworkException.fromResponse(e.response);
      case DioExceptionType.cancel:
        return const NetworkException(
          message: 'Request was cancelled.',
          code: 'REQUEST_CANCELLED',
        );
      case DioExceptionType.connectionError:
        return const NetworkException(
          message: 'Unable to connect. Please check your internet connection.',
          code: 'CONNECTION_ERROR',
        );
      default:
        return NetworkException(
          message: e.message ?? 'An unexpected network error occurred.',
          code: 'UNKNOWN_NETWORK_ERROR',
          statusCode: e.response?.statusCode,
        );
    }
  }

  factory NetworkException.fromResponse(Response? response) {
    if (response == null) {
      return const NetworkException(
        message: 'No response from server.',
        code: 'NO_RESPONSE',
      );
    }
    final data = response.data;
    final message = _extractMessage(data);
    final code = _extractCode(data);

    return NetworkException(
      message: message,
      code: code,
      statusCode: response.statusCode,
      data: data,
    );
  }

  static String _extractMessage(dynamic data) {
    if (data is Map<String, dynamic>) {
      return (data['message'] ?? data['error'] ?? data['detail'] ?? 'Request failed.')
          .toString();
    }
    return 'Request failed.';
  }

  static String? _extractCode(dynamic data) {
    if (data is Map<String, dynamic>) {
      return data['code']?.toString();
    }
    return null;
  }
}

final class UnauthorizedException extends AppException {
  const UnauthorizedException({
    super.message = 'Session expired. Please log in again.',
    super.code = 'UNAUTHORIZED',
  });
}

final class ForbiddenException extends AppException {
  const ForbiddenException({
    super.message = 'You do not have permission to perform this action.',
    super.code = 'FORBIDDEN',
  });
}

final class NotFoundException extends AppException {
  const NotFoundException({
    super.message = 'The requested resource was not found.',
    super.code = 'NOT_FOUND',
  });
}

final class ValidationException extends AppException {
  final Map<String, List<String>>? fieldErrors;

  const ValidationException({
    super.message = 'Validation failed.',
    super.code = 'VALIDATION_ERROR',
    this.fieldErrors,
  });
}

final class CacheException extends AppException {
  const CacheException({
    required super.message,
    super.code = 'CACHE_ERROR',
  });
}

final class StorageException extends AppException {
  const StorageException({
    required super.message,
    super.code = 'STORAGE_ERROR',
  });
}

final class ParseException extends AppException {
  const ParseException({
    required super.message,
    super.code = 'PARSE_ERROR',
  });
}

final class TokenException extends AppException {
  const TokenException({
    required super.message,
    super.code = 'TOKEN_ERROR',
  });
}

final class NoInternetException extends AppException {
  const NoInternetException({
    super.message = 'No internet connection. Please check your network settings.',
    super.code = 'NO_INTERNET',
  });
}

final class ServerException extends AppException {
  const ServerException({
    super.message = 'An internal server error occurred. Please try again later.',
    super.code = 'SERVER_ERROR',
    int? statusCode,
  });
}
