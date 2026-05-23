import 'package:flutter/material.dart';
import 'package:vibyuk/core/theme/app_colors.dart';
import 'package:vibyuk/core/theme/app_spacing.dart';

enum SnackBarType { info, success, warning, error }

abstract final class AppSnackBar {
  static void show(
    BuildContext context, {
    required String message,
    SnackBarType type = SnackBarType.info,
    Duration duration = const Duration(seconds: 3),
    String? actionLabel,
    VoidCallback? onAction,
  }) {
    final config = _SnackBarConfig.fromType(type);

    ScaffoldMessenger.of(context)
      ..hideCurrentSnackBar()
      ..showSnackBar(
        SnackBar(
          content: Row(
            children: [
              Icon(config.icon, color: config.iconColor, size: 20),
              AppSpacing.hGapSm,
              Expanded(
                child: Text(
                  message,
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        color: config.textColor,
                      ),
                ),
              ),
            ],
          ),
          backgroundColor: config.backgroundColor,
          duration: duration,
          behavior: SnackBarBehavior.floating,
          shape: const RoundedRectangleBorder(borderRadius: AppSpacing.brMd),
          margin: const EdgeInsets.all(AppSpacing.lg),
          action: actionLabel != null
              ? SnackBarAction(
                  label: actionLabel,
                  textColor: config.iconColor,
                  onPressed: onAction ?? () {},
                )
              : null,
        ),
      );
  }

  static void success(BuildContext context, String message, {Duration? duration}) =>
      show(context, message: message, type: SnackBarType.success, duration: duration ?? const Duration(seconds: 3));

  static void error(BuildContext context, String message, {Duration? duration}) =>
      show(context, message: message, type: SnackBarType.error, duration: duration ?? const Duration(seconds: 4));

  static void warning(BuildContext context, String message, {Duration? duration}) =>
      show(context, message: message, type: SnackBarType.warning, duration: duration ?? const Duration(seconds: 3));

  static void info(BuildContext context, String message, {Duration? duration}) =>
      show(context, message: message, type: SnackBarType.info, duration: duration ?? const Duration(seconds: 3));
}

class _SnackBarConfig {
  const _SnackBarConfig({
    required this.backgroundColor,
    required this.icon,
    required this.iconColor,
    required this.textColor,
  });

  final Color backgroundColor;
  final IconData icon;
  final Color iconColor;
  final Color textColor;

  factory _SnackBarConfig.fromType(SnackBarType type) => switch (type) {
        SnackBarType.success => const _SnackBarConfig(
            backgroundColor: Color(0xFF1A3326),
            icon: Icons.check_circle_outline_rounded,
            iconColor: AppColors.tertiary,
            textColor: Color(0xFFB7F5DC),
          ),
        SnackBarType.error => const _SnackBarConfig(
            backgroundColor: Color(0xFF3B1A1A),
            icon: Icons.error_outline_rounded,
            iconColor: AppColors.error,
            textColor: Color(0xFFFFC9C9),
          ),
        SnackBarType.warning => const _SnackBarConfig(
            backgroundColor: Color(0xFF3B2F0A),
            icon: Icons.warning_amber_rounded,
            iconColor: AppColors.warning,
            textColor: Color(0xFFFFF0C2),
          ),
        SnackBarType.info => const _SnackBarConfig(
            backgroundColor: Color(0xFF0F2040),
            icon: Icons.info_outline_rounded,
            iconColor: AppColors.info,
            textColor: Color(0xFFBDD8FF),
          ),
      };
}
