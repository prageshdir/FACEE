import 'package:dio/dio.dart';
import 'package:vibyuk/core/api/interceptors/auth_interceptor.dart';
import 'package:vibyuk/core/api/interceptors/error_interceptor.dart';
import 'package:vibyuk/core/api/interceptors/logging_interceptor.dart';
import 'package:vibyuk/core/config/app_config.dart';
import 'package:vibyuk/core/error/exceptions.dart';
import 'package:vibyuk/core/logging/app_logger.dart';

class ApiClient {
  ApiClient._({required Dio dio}) : _dio = dio;

  final Dio _dio;

  static ApiClient create({
    required AuthInterceptor authInterceptor,
    required ErrorInterceptor errorInterceptor,
    bool enableLogging = false,
  }) {
    final dio = Dio(
      BaseOptions(
        baseUrl: AppConfig.baseUrl,
        connectTimeout: const Duration(milliseconds: AppConfig.connectTimeoutMs),
        receiveTimeout: const Duration(milliseconds: AppConfig.receiveTimeoutMs),
        sendTimeout: const Duration(milliseconds: AppConfig.sendTimeoutMs),
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
          'X-App-Version': AppConfig.appVersion,
          'X-Platform': 'mobile',
        },
      ),
    );

    if (enableLogging) {
      dio.interceptors.add(LoggingInterceptor());
    }
    dio.interceptors
      ..add(authInterceptor)
      ..add(errorInterceptor);

    return ApiClient._(dio: dio);
  }

  Future<Response<T>> get<T>(
    String path, {
    Map<String, dynamic>? queryParameters,
    Options? options,
    CancelToken? cancelToken,
  }) =>
      _execute(
        () => _dio.get<T>(
          path,
          queryParameters: queryParameters,
          options: options,
          cancelToken: cancelToken,
        ),
      );

  Future<Response<T>> post<T>(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
    CancelToken? cancelToken,
  }) =>
      _execute(
        () => _dio.post<T>(
          path,
          data: data,
          queryParameters: queryParameters,
          options: options,
          cancelToken: cancelToken,
        ),
      );

  Future<Response<T>> put<T>(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
    CancelToken? cancelToken,
  }) =>
      _execute(
        () => _dio.put<T>(
          path,
          data: data,
          queryParameters: queryParameters,
          options: options,
          cancelToken: cancelToken,
        ),
      );

  Future<Response<T>> patch<T>(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
    CancelToken? cancelToken,
  }) =>
      _execute(
        () => _dio.patch<T>(
          path,
          data: data,
          queryParameters: queryParameters,
          options: options,
          cancelToken: cancelToken,
        ),
      );

  Future<Response<T>> delete<T>(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
    CancelToken? cancelToken,
  }) =>
      _execute(
        () => _dio.delete<T>(
          path,
          data: data,
          queryParameters: queryParameters,
          options: options,
          cancelToken: cancelToken,
        ),
      );

  Future<Response<T>> uploadFile<T>(
    String path, {
    required FormData formData,
    void Function(int sent, int total)? onSendProgress,
    CancelToken? cancelToken,
  }) =>
      _execute(
        () => _dio.post<T>(
          path,
          data: formData,
          options: Options(contentType: 'multipart/form-data'),
          onSendProgress: onSendProgress,
          cancelToken: cancelToken,
        ),
      );

  Future<Response<T>> _execute<T>(Future<Response<T>> Function() call) async {
    try {
      return await call();
    } on DioException catch (e) {
      if (e.error is AppException) rethrow;
      throw NetworkException.fromDioException(e);
    } catch (e, st) {
      AppLogger.error('ApiClient: unexpected error', error: e, stackTrace: st);
      rethrow;
    }
  }

  void close({bool force = false}) => _dio.close(force: force);
}
