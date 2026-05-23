import 'package:vibyuk/core/config/flavor_config.dart';

abstract final class AppConfig {
  static const String appName = 'VIBYUK';
  static const String appVersion = '1.0.0';
  static const int buildNumber = 1;
  static const String appPackageId = 'com.vibyuk.app';

  // Network timeouts (milliseconds)
  static const int connectTimeoutMs = 30000;
  static const int receiveTimeoutMs = 30000;
  static const int sendTimeoutMs = 30000;

  // Token management
  static const int tokenRefreshThresholdSeconds = 60;
  static const int maxRetryAttempts = 3;
  static const int retryBaseDelayMs = 500;

  // Pagination
  static const int defaultPageSize = 20;
  static const int maxPageSize = 100;

  // Cache
  static const int defaultCacheMaxAgeSeconds = 300;
  static const int imageCacheMaxAgeSeconds = 86400;
  static const int maxCacheSizeMb = 50;

  // Pagination scroll threshold (0.0 - 1.0)
  static const double paginationScrollThreshold = 0.8;

  // Derived from flavor
  static String get baseUrl => FlavorConfig.instance.baseUrl;
  static String get wsUrl => FlavorConfig.instance.wsUrl;
  static bool get isDebug => !FlavorConfig.instance.isProduction;
  static bool get enableLogging => FlavorConfig.instance.enableLogging;
  static bool get enableCrashlytics => FlavorConfig.instance.enableCrashlytics;
  static bool get enableAnalytics => FlavorConfig.instance.enableAnalytics;
}
