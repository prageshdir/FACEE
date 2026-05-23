abstract final class AppConstants {
  static const String appName = 'VIBYUK';
  static const String appTagline = 'Create. Collaborate. Vibe.';

  // Asset paths
  static const String logoPath = 'assets/images/logo.png';
  static const String logomarkPath = 'assets/images/logomark.png';
  static const String splashPath = 'assets/images/splash.png';
  static const String onboardingPath = 'assets/images/onboarding';
  static const String placeholderAvatarPath = 'assets/images/avatar_placeholder.png';

  // Animation durations
  static const Duration animFast = Duration(milliseconds: 150);
  static const Duration animMedium = Duration(milliseconds: 300);
  static const Duration animSlow = Duration(milliseconds: 500);
  static const Duration animVerySlow = Duration(milliseconds: 800);

  // Snack bar durations
  static const Duration snackBarShort = Duration(seconds: 2);
  static const Duration snackBarMedium = Duration(seconds: 4);
  static const Duration snackBarLong = Duration(seconds: 6);

  // Keyboard debounce
  static const Duration searchDebounce = Duration(milliseconds: 400);

  // Network
  static const int maxImageSizeMb = 10;
  static const int maxVideoSizeMb = 100;
  static const List<String> allowedImageExtensions = ['jpg', 'jpeg', 'png', 'webp'];

  // Regex
  static final RegExp emailRegex = RegExp(r'^[\w.+-]+@[\w-]+\.[\w.]+$');
  static final RegExp passwordRegex = RegExp(
    r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$',
  );
  static final RegExp phoneRegex = RegExp(r'^\+?[1-9]\d{6,14}$');
  static final RegExp urlRegex = RegExp(
    r'^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}([-a-zA-Z0-9()@:%_+.~#?&/=]*)$',
  );
}
