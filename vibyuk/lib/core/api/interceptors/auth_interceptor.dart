import 'package:dio/dio.dart';
import 'package:vibyuk/core/auth/token_manager.dart';
import 'package:vibyuk/core/auth/token_refresh_service.dart';
import 'package:vibyuk/core/error/exceptions.dart';
import 'package:vibyuk/core/logging/app_logger.dart';

class AuthInterceptor extends Interceptor {
  AuthInterceptor({
    required TokenManager tokenManager,
    required TokenRefreshService tokenRefreshService,
    required List<String> publicEndpoints,
  })  : _tokenManager = tokenManager,
        _tokenRefreshService = tokenRefreshService,
        _publicEndpoints = publicEndpoints;

  final TokenManager _tokenManager;
  final TokenRefreshService _tokenRefreshService;
  final List<String> _publicEndpoints;

  @override
  Future<void> onRequest(
    RequestOptions options,
    RequestInterceptorHandler handler,
  ) async {
    if (_isPublicEndpoint(options.path)) {
      return handler.next(options);
    }

    try {
      if (await _tokenManager.isTokenExpiringSoon()) {
        AppLogger.debug('AuthInterceptor: proactively refreshing expiring token');
        await _tokenRefreshService.refreshIfNeeded();
      }

      final token = await _tokenManager.getAccessToken();
      if (token != null && token.isNotEmpty) {
        options.headers['Authorization'] = 'Bearer $token';
      }
      return handler.next(options);
    } catch (e) {
      AppLogger.warning('AuthInterceptor: failed to attach token', error: e);
      return handler.next(options);
    }
  }

  @override
  Future<void> onError(
    DioException err,
    ErrorInterceptorHandler handler,
  ) async {
    if (err.response?.statusCode != 401) {
      return handler.next(err);
    }

    if (_isPublicEndpoint(err.requestOptions.path)) {
      return handler.next(err);
    }

    // Prevent refresh loop
    if (err.requestOptions.extra['_retried'] == true) {
      await _tokenManager.clearTokens();
      AppLogger.warning('AuthInterceptor: refresh retry failed — clearing session');
      return handler.reject(
        DioException(
          requestOptions: err.requestOptions,
          error: const UnauthorizedException(),
          type: DioExceptionType.badResponse,
          response: err.response,
        ),
      );
    }

    try {
      AppLogger.info('AuthInterceptor: 401 received — attempting token refresh');
      final newToken = await _tokenRefreshService.refreshIfNeeded();

      if (newToken == null) {
        await _tokenManager.clearTokens();
        return handler.reject(err);
      }

      final retryOptions = err.requestOptions.copyWith(
        headers: {
          ...err.requestOptions.headers,
          'Authorization': 'Bearer $newToken',
        },
        extra: {...err.requestOptions.extra, '_retried': true},
      );

      final dio = Dio(BaseOptions(
        baseUrl: err.requestOptions.baseUrl,
        headers: retryOptions.headers,
      ));

      final response = await dio.fetch(retryOptions);
      return handler.resolve(response);
    } catch (e) {
      await _tokenManager.clearTokens();
      AppLogger.error('AuthInterceptor: token refresh failed', error: e);
      return handler.reject(err);
    }
  }

  bool _isPublicEndpoint(String path) =>
      _publicEndpoints.any((endpoint) => path.endsWith(endpoint));
}
