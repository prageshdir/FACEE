import 'package:dio/dio.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:get_it/get_it.dart';
import 'package:vibyuk/core/api/api_client.dart';
import 'package:vibyuk/core/api/api_endpoints.dart';
import 'package:vibyuk/core/api/interceptors/auth_interceptor.dart';
import 'package:vibyuk/core/api/interceptors/error_interceptor.dart';
import 'package:vibyuk/core/auth/token_manager.dart';
import 'package:vibyuk/core/auth/token_refresh_service.dart';
import 'package:vibyuk/core/config/app_config.dart';
import 'package:vibyuk/core/storage/secure_storage.dart';

void registerApiModule(GetIt sl) {
  sl.registerLazySingleton<FlutterSecureStorage>(
    () => const FlutterSecureStorage(),
  );

  sl.registerLazySingleton<SecureStorage>(
    () => SecureStorage(sl<FlutterSecureStorage>()),
  );

  sl.registerLazySingleton<TokenManager>(
    () => TokenManager(sl<SecureStorage>()),
  );

  // Bare Dio for token refresh (no auth interceptor to avoid loops)
  sl.registerLazySingleton<Dio>(
    () => Dio(
      BaseOptions(
        baseUrl: AppConfig.baseUrl,
        connectTimeout: const Duration(milliseconds: AppConfig.connectTimeoutMs),
        receiveTimeout: const Duration(milliseconds: AppConfig.receiveTimeoutMs),
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
      ),
    ),
    instanceName: 'refreshDio',
  );

  sl.registerLazySingleton<TokenRefreshService>(
    () => TokenRefreshService(
      tokenManager: sl<TokenManager>(),
      httpClient: sl<Dio>(instanceName: 'refreshDio'),
      refreshEndpoint: ApiEndpoints.refreshToken,
    ),
  );

  sl.registerLazySingleton<AuthInterceptor>(
    () => AuthInterceptor(
      tokenManager: sl<TokenManager>(),
      tokenRefreshService: sl<TokenRefreshService>(),
      publicEndpoints: [
        ApiEndpoints.login,
        ApiEndpoints.register,
        ApiEndpoints.refreshToken,
        ApiEndpoints.forgotPassword,
        ApiEndpoints.resetPassword,
      ],
    ),
  );

  sl.registerLazySingleton<ErrorInterceptor>(() => ErrorInterceptor());

  sl.registerLazySingleton<ApiClient>(
    () => ApiClient.create(
      authInterceptor: sl<AuthInterceptor>(),
      errorInterceptor: sl<ErrorInterceptor>(),
      enableLogging: AppConfig.enableLogging,
    ),
  );
}
