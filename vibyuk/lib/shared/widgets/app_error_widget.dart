import 'package:flutter/material.dart';
import 'package:vibyuk/core/error/failures.dart';
import 'package:vibyuk/core/theme/app_colors.dart';
import 'package:vibyuk/core/theme/app_spacing.dart';
import 'package:vibyuk/shared/widgets/app_button.dart';

class AppErrorWidget extends StatelessWidget {
  const AppErrorWidget({
    super.key,
    required this.failure,
    this.onRetry,
    this.compact = false,
  });

  final Failure failure;
  final VoidCallback? onRetry;
  final bool compact;

  @override
  Widget build(BuildContext context) {
    if (compact) return _CompactError(failure: failure, onRetry: onRetry);

    return Center(
      child: Padding(
        padding: const EdgeInsets.all(AppSpacing.xl),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            _ErrorIcon(failure: failure),
            AppSpacing.vGapLg,
            Text(
              _title,
              style: Theme.of(context).textTheme.titleMedium,
              textAlign: TextAlign.center,
            ),
            AppSpacing.vGapSm,
            Text(
              failure.message,
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: Theme.of(context).colorScheme.onSurfaceVariant,
                  ),
              textAlign: TextAlign.center,
            ),
            if (onRetry != null) ...[
              AppSpacing.vGapXl,
              AppButton(
                label: 'Try Again',
                onPressed: onRetry,
                variant: AppButtonVariant.outlined,
                size: AppButtonSize.medium,
                icon: Icons.refresh_rounded,
                width: 160,
              ),
            ],
          ],
        ),
      ),
    );
  }

  String get _title => switch (failure) {
        NoInternetFailure() => 'No Connection',
        UnauthorizedFailure() => 'Session Expired',
        NotFoundFailure() => 'Not Found',
        ServerFailure() => 'Server Error',
        _ => 'Something Went Wrong',
      };
}

class _ErrorIcon extends StatelessWidget {
  const _ErrorIcon({required this.failure});

  final Failure failure;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 80,
      height: 80,
      decoration: BoxDecoration(
        color: AppColors.errorContainer,
        shape: BoxShape.circle,
      ),
      child: Icon(_icon, size: 36, color: AppColors.error),
    );
  }

  IconData get _icon => switch (failure) {
        NoInternetFailure() => Icons.wifi_off_rounded,
        UnauthorizedFailure() => Icons.lock_outline_rounded,
        NotFoundFailure() => Icons.search_off_rounded,
        ServerFailure() => Icons.cloud_off_rounded,
        _ => Icons.error_outline_rounded,
      };
}

class _CompactError extends StatelessWidget {
  const _CompactError({required this.failure, this.onRetry});

  final Failure failure;
  final VoidCallback? onRetry;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(AppSpacing.lg),
      child: Row(
        children: [
          Icon(Icons.error_outline_rounded, color: AppColors.error, size: 20),
          AppSpacing.hGapSm,
          Expanded(
            child: Text(
              failure.message,
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: AppColors.error,
                  ),
            ),
          ),
          if (onRetry != null)
            IconButton(
              icon: const Icon(Icons.refresh_rounded, size: 20),
              onPressed: onRetry,
              padding: EdgeInsets.zero,
              constraints: const BoxConstraints(minWidth: 32, minHeight: 32),
            ),
        ],
      ),
    );
  }
}

class EmptyStateWidget extends StatelessWidget {
  const EmptyStateWidget({
    super.key,
    required this.title,
    required this.message,
    this.icon = Icons.inbox_outlined,
    this.action,
    this.actionLabel,
  });

  final String title;
  final String message;
  final IconData icon;
  final VoidCallback? action;
  final String? actionLabel;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(AppSpacing.xxl),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              width: 88,
              height: 88,
              decoration: BoxDecoration(
                color: Theme.of(context).colorScheme.surfaceContainerHighest,
                shape: BoxShape.circle,
              ),
              child: Icon(
                icon,
                size: 40,
                color: Theme.of(context).colorScheme.onSurfaceVariant,
              ),
            ),
            AppSpacing.vGapLg,
            Text(
              title,
              style: Theme.of(context).textTheme.titleMedium,
              textAlign: TextAlign.center,
            ),
            AppSpacing.vGapSm,
            Text(
              message,
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: Theme.of(context).colorScheme.onSurfaceVariant,
                  ),
              textAlign: TextAlign.center,
            ),
            if (action != null && actionLabel != null) ...[
              AppSpacing.vGapXl,
              AppButton(
                label: actionLabel!,
                onPressed: action,
                size: AppButtonSize.medium,
                width: 180,
              ),
            ],
          ],
        ),
      ),
    );
  }
}
