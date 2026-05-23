import 'package:firebase_core/firebase_core.dart';
import 'package:vibyuk/core/logging/app_logger.dart';

abstract final class FirebaseConfig {
  static bool _initialized = false;

  static Future<void> initialize() async {
    if (_initialized) return;
    try {
      await Firebase.initializeApp();
      _initialized = true;
      AppLogger.info('FirebaseConfig: initialized');
    } catch (e, st) {
      AppLogger.fatal('FirebaseConfig: initialization failed', error: e, stackTrace: st);
      rethrow;
    }
  }

  static bool get isInitialized => _initialized;
}
