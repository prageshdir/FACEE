import 'package:dio/dio.dart';
import 'package:vibyuk/core/error/exceptions.dart';
import 'package:vibyuk/core/logging/app_logger.dart';

class ErrorInterceptor extends Interceptor {
  @override
  void onError(DioException err, ErrorInterceptorHandler handler) {
    AppLogger.error('ErrorInterceptor: ${err.type}', error: err);

    final exception = switch (err.response?.statusCode) {
      400 => _handle400(err),
      401 => const UnauthorizedException(),
      403 => const ForbiddenException(),
      404 => const NotFoundException(),
      422 => _handle422(err),
      >= 500 => const ServerException(),
      _ => NetworkException.fromDioException(err),
    };

    handler.reject(
      DioException(
        requestOptions: err.requestOptions,
        response: err.response,
        type: err.type,
        error: exception,
        message: exception.message,
      ),
    );
  }

  AppException _handle400(DioException err) {
    final data = err.response?.data;
    if (data is Map<String, dynamic>) {
      final message = data['message']?.toString() ?? 'Bad request.';
      return NetworkException(
        message: message,
        statusCode: 400,
        data: data,
      );
    }
    return const NetworkException(message: 'Bad request.', statusCode: 400);
  }

  AppException _handle422(DioException err) {
    final data = err.response?.data;
    if (data is Map<String, dynamic>) {
      final errors = data['errors'];
      if (errors is Map<String, dynamic>) {
        final fieldErrors = errors.map(
          (key, value) => MapEntry(
            key,
            (value as List).map((e) => e.toString()).toList(),
          ),
        );
        return ValidationException(
          message: data['message']?.toString() ?? 'Validation failed.',
          fieldErrors: fieldErrors,
        );
      }
    }
    return const ValidationException();
  }
}
