import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:vibyuk/app/app.dart';
import 'package:vibyuk/app/app_bloc_observer.dart';
import 'package:vibyuk/core/config/flavor_config.dart';
import 'package:vibyuk/core/di/injection.dart';
import 'package:vibyuk/core/firebase/push_notification_service.dart';
import 'package:vibyuk/core/logging/app_logger.dart';

void main() {
  FlavorConfig.initialize(FlavorConfig.dev);
  _bootstrap();
}

void _bootstrap() {
  runZonedGuarded(
    () async {
      WidgetsFlutterBinding.ensureInitialized();

      AppLogger.initialize();
      AppLogger.info('App starting — flavor=dev');

      Bloc.observer = AppBlocObserver();

      await configureDependencies();

      await sl<PushNotificationService>().initialize();

      runApp(const VibyukApp());
    },
    (error, stack) {
      AppLogger.fatal('Unhandled zone error', error: error, stackTrace: stack);
    },
  );
}
