import 'package:flutter/material.dart';
import 'package:vibyuk/core/theme/app_spacing.dart';
import 'package:vibyuk/shared/widgets/app_loading.dart';

enum AppButtonVariant { filled, outlined, text, destructive }

enum AppButtonSize { small, medium, large }

class AppButton extends StatelessWidget {
  const AppButton({
    super.key,
    required this.label,
    required this.onPressed,
    this.variant = AppButtonVariant.filled,
    this.size = AppButtonSize.large,
    this.isLoading = false,
    this.isEnabled = true,
    this.icon,
    this.trailingIcon,
    this.width,
  });

  final String label;
  final VoidCallback? onPressed;
  final AppButtonVariant variant;
  final AppButtonSize size;
  final bool isLoading;
  final bool isEnabled;
  final IconData? icon;
  final IconData? trailingIcon;
  final double? width;

  @override
  Widget build(BuildContext context) {
    final effectiveCallback = (!isEnabled || isLoading) ? null : onPressed;

    return SizedBox(
      width: width,
      height: _height,
      child: switch (variant) {
        AppButtonVariant.filled => _FilledButton(
            label: label,
            onPressed: effectiveCallback,
            isLoading: isLoading,
            icon: icon,
            trailingIcon: trailingIcon,
            size: size,
          ),
        AppButtonVariant.outlined => _OutlinedButton(
            label: label,
            onPressed: effectiveCallback,
            isLoading: isLoading,
            icon: icon,
            trailingIcon: trailingIcon,
            size: size,
          ),
        AppButtonVariant.text => _TextButton(
            label: label,
            onPressed: effectiveCallback,
            isLoading: isLoading,
            icon: icon,
            size: size,
          ),
        AppButtonVariant.destructive => _DestructiveButton(
            label: label,
            onPressed: effectiveCallback,
            isLoading: isLoading,
            icon: icon,
            size: size,
          ),
      },
    );
  }

  double get _height => switch (size) {
        AppButtonSize.small => 36,
        AppButtonSize.medium => 44,
        AppButtonSize.large => 52,
      };
}

class _FilledButton extends StatelessWidget {
  const _FilledButton({
    required this.label,
    required this.onPressed,
    required this.isLoading,
    required this.size,
    this.icon,
    this.trailingIcon,
  });

  final String label;
  final VoidCallback? onPressed;
  final bool isLoading;
  final AppButtonSize size;
  final IconData? icon;
  final IconData? trailingIcon;

  @override
  Widget build(BuildContext context) {
    return FilledButton(
      onPressed: onPressed,
      child: _ButtonContent(
        label: label,
        isLoading: isLoading,
        icon: icon,
        trailingIcon: trailingIcon,
        size: size,
      ),
    );
  }
}

class _OutlinedButton extends StatelessWidget {
  const _OutlinedButton({
    required this.label,
    required this.onPressed,
    required this.isLoading,
    required this.size,
    this.icon,
    this.trailingIcon,
  });

  final String label;
  final VoidCallback? onPressed;
  final bool isLoading;
  final AppButtonSize size;
  final IconData? icon;
  final IconData? trailingIcon;

  @override
  Widget build(BuildContext context) {
    return OutlinedButton(
      onPressed: onPressed,
      child: _ButtonContent(
        label: label,
        isLoading: isLoading,
        icon: icon,
        trailingIcon: trailingIcon,
        size: size,
      ),
    );
  }
}

class _TextButton extends StatelessWidget {
  const _TextButton({
    required this.label,
    required this.onPressed,
    required this.isLoading,
    required this.size,
    this.icon,
  });

  final String label;
  final VoidCallback? onPressed;
  final bool isLoading;
  final AppButtonSize size;
  final IconData? icon;

  @override
  Widget build(BuildContext context) {
    return TextButton(
      onPressed: onPressed,
      child: _ButtonContent(
        label: label,
        isLoading: isLoading,
        icon: icon,
        size: size,
      ),
    );
  }
}

class _DestructiveButton extends StatelessWidget {
  const _DestructiveButton({
    required this.label,
    required this.onPressed,
    required this.isLoading,
    required this.size,
    this.icon,
  });

  final String label;
  final VoidCallback? onPressed;
  final bool isLoading;
  final AppButtonSize size;
  final IconData? icon;

  @override
  Widget build(BuildContext context) {
    final color = Theme.of(context).colorScheme.error;
    return FilledButton(
      onPressed: onPressed,
      style: FilledButton.styleFrom(backgroundColor: color),
      child: _ButtonContent(
        label: label,
        isLoading: isLoading,
        icon: icon,
        size: size,
      ),
    );
  }
}

class _ButtonContent extends StatelessWidget {
  const _ButtonContent({
    required this.label,
    required this.isLoading,
    required this.size,
    this.icon,
    this.trailingIcon,
  });

  final String label;
  final bool isLoading;
  final AppButtonSize size;
  final IconData? icon;
  final IconData? trailingIcon;

  @override
  Widget build(BuildContext context) {
    if (isLoading) {
      return AppLoadingIndicator(
        size: _iconSize * 0.9,
        color: IconTheme.of(context).color,
      );
    }

    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        if (icon != null) ...[
          Icon(icon, size: _iconSize),
          AppSpacing.hGapSm,
        ],
        Text(label),
        if (trailingIcon != null) ...[
          AppSpacing.hGapSm,
          Icon(trailingIcon, size: _iconSize),
        ],
      ],
    );
  }

  double get _iconSize => switch (size) {
        AppButtonSize.small => 16,
        AppButtonSize.medium => 18,
        AppButtonSize.large => 20,
      };
}
