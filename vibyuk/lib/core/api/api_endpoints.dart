abstract final class ApiEndpoints {
  // Auth
  static const String login = '/auth/login';
  static const String register = '/auth/register';
  static const String logout = '/auth/logout';
  static const String refreshToken = '/auth/token/refresh';
  static const String forgotPassword = '/auth/password/forgot';
  static const String resetPassword = '/auth/password/reset';
  static const String verifyEmail = '/auth/email/verify';
  static const String resendVerification = '/auth/email/resend';

  // User
  static const String me = '/users/me';
  static const String updateProfile = '/users/me';
  static const String uploadAvatar = '/users/me/avatar';
  static const String users = '/users';
  static String userById(String id) => '/users/$id';

  // Notifications
  static const String notifications = '/notifications';
  static const String markNotificationRead = '/notifications/read';
  static const String registerFcmToken = '/notifications/fcm-token';

  // Pagination helper
  static String paginate(String endpoint, {int page = 1, int limit = 20}) =>
      '$endpoint?page=$page&limit=$limit';
}
