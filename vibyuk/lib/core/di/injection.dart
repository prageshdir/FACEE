import 'package:get_it/get_it.dart';
import 'package:hive_flutter/hive_flutter.dart';
import 'package:vibyuk/core/di/modules/api_module.dart';
import 'package:vibyuk/core/di/modules/cache_module.dart';
import 'package:vibyuk/core/di/modules/repository_module.dart';
import 'package:vibyuk/core/firebase/firebase_config.dart';
import 'package:vibyuk/core/firebase/push_notification_service.dart';
import 'package:vibyuk/core/logging/app_logger.dart';
import 'package:vibyuk/core/navigation/app_router.dart';
import 'package:vibyuk/core/navigation/route_guards.dart';
import 'package:vibyuk/core/storage/secure_storage.dart';
import 'package:vibyuk/core/auth/token_manager.dart';

final GetIt sl = GetIt.instance;

Future<void> configureDependencies() async {
  AppLogger.info('DI: configuring dependencies');

  // Infrastructure
  await Hive.initFlutter();

  // Firebase
  await FirebaseConfig.initialize();

  // Async modules must be awaited
  await registerCacheModule(sl);

  // Synchronous modules
  registerApiModule(sl);
  registerRepositoryModule(sl);

  // Push Notifications
  sl.registerLazySingleton<PushNotificationService>(
    () => PushNotificationService(secureStorage: sl<SecureStorage>()),
  );

  // Navigation
  sl.registerLazySingleton<AuthGuard>(
    () => AuthGuard(
      tokenManager: sl<TokenManager>(),
      secureStorage: sl<SecureStorage>(),
    ),
  );

  sl.registerLazySingleton<AppRouter>(
    () => AppRouter(authGuard: sl<AuthGuard>()),
  );

  await sl.allReady();
  AppLogger.info('DI: all dependencies ready');
}
