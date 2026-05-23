import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:vibyuk/core/config/app_config.dart';
import 'package:vibyuk/core/di/injection.dart';
import 'package:vibyuk/core/navigation/app_router.dart';
import 'package:vibyuk/core/theme/app_theme.dart';

class VibyukApp extends StatelessWidget {
  const VibyukApp({super.key});

  @override
  Widget build(BuildContext context) {
    final router = sl<AppRouter>().router;

    return MaterialApp.router(
      title: AppConfig.appName,
      debugShowCheckedModeBanner: false,
      theme: AppTheme.light,
      darkTheme: AppTheme.dark,
      themeMode: ThemeMode.system,
      routerConfig: router,
      localizationsDelegates: const [
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
      ],
      supportedLocales: const [
        Locale('en'),
      ],
    );
  }
}
