import 'package:flutter/material.dart';

abstract final class AppColors {
  // Brand
  static const Color primary = Color(0xFF6C3CE3);       // Vibe Purple
  static const Color primaryLight = Color(0xFF9B6FF0);
  static const Color primaryDark = Color(0xFF4A1DB5);
  static const Color primaryContainer = Color(0xFFEDE7FF);

  static const Color secondary = Color(0xFFFF6B6B);     // Energy Coral
  static const Color secondaryLight = Color(0xFFFF9999);
  static const Color secondaryDark = Color(0xFFD93F3F);
  static const Color secondaryContainer = Color(0xFFFFEBEB);

  static const Color tertiary = Color(0xFF00C896);      // Creator Teal
  static const Color tertiaryLight = Color(0xFF4DDDB8);
  static const Color tertiaryDark = Color(0xFF009970);
  static const Color tertiaryContainer = Color(0xFFDFF9F1);

  // Neutrals – Light theme
  static const Color surface = Color(0xFFFFFFFF);
  static const Color surfaceVariant = Color(0xFFF5F3FF);
  static const Color background = Color(0xFFF8F7FE);
  static const Color outline = Color(0xFFD0C9E8);
  static const Color outlineVariant = Color(0xFFE8E4F5);

  // Neutrals – Dark theme
  static const Color surfaceDark = Color(0xFF1A1625);
  static const Color surfaceVariantDark = Color(0xFF241E35);
  static const Color backgroundDark = Color(0xFF120E1E);
  static const Color outlineDark = Color(0xFF3D3450);
  static const Color outlineVariantDark = Color(0xFF2E2842);

  // Semantic
  static const Color success = Color(0xFF22C55E);
  static const Color successContainer = Color(0xFFDCFCE7);
  static const Color warning = Color(0xFFF59E0B);
  static const Color warningContainer = Color(0xFFFEF3C7);
  static const Color error = Color(0xFFEF4444);
  static const Color errorContainer = Color(0xFFFEE2E2);
  static const Color info = Color(0xFF3B82F6);
  static const Color infoContainer = Color(0xFFDBEAFE);

  // Text
  static const Color onPrimary = Color(0xFFFFFFFF);
  static const Color onSecondary = Color(0xFFFFFFFF);
  static const Color textPrimary = Color(0xFF1A1625);
  static const Color textSecondary = Color(0xFF6B5F8A);
  static const Color textDisabled = Color(0xFFB8AFD1);
  static const Color textPrimaryDark = Color(0xFFF0ECFF);
  static const Color textSecondaryDark = Color(0xFF9B90BC);
  static const Color textDisabledDark = Color(0xFF4A3F66);

  // Gradient stops
  static const LinearGradient brandGradient = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [primary, secondary],
  );

  static const LinearGradient subtleGradient = LinearGradient(
    begin: Alignment.topCenter,
    end: Alignment.bottomCenter,
    colors: [primaryContainer, surface],
  );
}
