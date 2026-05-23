import 'package:go_router/go_router.dart';
import 'package:vibyuk/core/auth/token_manager.dart';
import 'package:vibyuk/core/logging/app_logger.dart';
import 'package:vibyuk/core/navigation/routes.dart';
import 'package:vibyuk/core/storage/secure_storage.dart';
import 'package:vibyuk/core/storage/storage_keys.dart';

class AuthGuard {
  const AuthGuard({
    required TokenManager tokenManager,
    required SecureStorage secureStorage,
  })  : _tokenManager = tokenManager,
        _secureStorage = secureStorage;

  final TokenManager _tokenManager;
  final SecureStorage _secureStorage;

  Future<String?> redirect(GoRouterState state) async {
    final isAuthenticated = await _tokenManager.hasValidToken();
    final isAuthRoute = _isAuthRoute(state.matchedLocation);
    final isSplash = state.matchedLocation == Routes.splash;

    if (isSplash) return null;

    if (!isAuthenticated && !isAuthRoute) {
      AppLogger.info('AuthGuard: unauthenticated — redirecting to login');
      return '${Routes.login}?from=${Uri.encodeComponent(state.matchedLocation)}';
    }

    if (isAuthenticated && isAuthRoute) {
      final onboardingDone = await _isOnboardingComplete();
      AppLogger.info('AuthGuard: authenticated — redirecting to home');
      return onboardingDone ? Routes.home : Routes.onboarding;
    }

    return null;
  }

  bool _isAuthRoute(String location) =>
      location.startsWith('/auth') || location == Routes.onboarding;

  Future<bool> _isOnboardingComplete() async {
    final value = await _secureStorage.read(key: StorageKeys.onboardingComplete);
    return value == 'true';
  }
}
