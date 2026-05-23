import 'package:dio/dio.dart';
import 'package:vibyuk/core/logging/app_logger.dart';

class LoggingInterceptor extends Interceptor {
  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) {
    AppLogger.debug(
      '→ ${options.method} ${options.uri}\n'
      '  Headers: ${_sanitizeHeaders(options.headers)}\n'
      '  Body: ${options.data}',
    );
    handler.next(options);
  }

  @override
  void onResponse(Response response, ResponseInterceptorHandler handler) {
    AppLogger.debug(
      '← ${response.statusCode} ${response.requestOptions.uri}\n'
      '  Body: ${_truncate(response.data.toString())}',
    );
    handler.next(response);
  }

  @override
  void onError(DioException err, ErrorInterceptorHandler handler) {
    AppLogger.error(
      '✗ ${err.requestOptions.method} ${err.requestOptions.uri}\n'
      '  Status: ${err.response?.statusCode}\n'
      '  Error: ${err.message}\n'
      '  Body: ${_truncate(err.response?.data?.toString() ?? '')}',
      error: err,
    );
    handler.next(err);
  }

  Map<String, dynamic> _sanitizeHeaders(Map<String, dynamic> headers) {
    final copy = Map<String, dynamic>.from(headers);
    if (copy.containsKey('Authorization')) {
      copy['Authorization'] = 'Bearer [REDACTED]';
    }
    return copy;
  }

  String _truncate(String text, {int maxLength = 500}) =>
      text.length > maxLength ? '${text.substring(0, maxLength)}...[truncated]' : text;
}
