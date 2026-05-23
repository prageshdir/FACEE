abstract final class StorageKeys {
  // Auth
  static const String accessToken = 'auth_access_token';
  static const String refreshToken = 'auth_refresh_token';
  static const String tokenExpiry = 'auth_token_expiry';
  static const String userId = 'auth_user_id';

  // User preferences
  static const String themeMode = 'pref_theme_mode';
  static const String locale = 'pref_locale';
  static const String onboardingComplete = 'pref_onboarding_complete';
  static const String pushNotificationsEnabled = 'pref_push_notifications';
  static const String fcmToken = 'fcm_device_token';

  // Cache metadata
  static const String cacheVersion = 'cache_version';
  static const String lastSyncTimestamp = 'cache_last_sync';
}
