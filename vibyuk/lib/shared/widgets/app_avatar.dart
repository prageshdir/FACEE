import 'package:cached_network_image/cached_network_image.dart';
import 'package:flutter/material.dart';
import 'package:vibyuk/core/theme/app_colors.dart';
import 'package:vibyuk/core/utils/extensions/string_extension.dart';

enum AvatarSize { xs, sm, md, lg, xl }

class AppAvatar extends StatelessWidget {
  const AppAvatar({
    super.key,
    this.imageUrl,
    this.name,
    this.size = AvatarSize.md,
    this.isOnline,
    this.onTap,
    this.borderColor,
    this.borderWidth = 0,
  });

  final String? imageUrl;
  final String? name;
  final AvatarSize size;
  final bool? isOnline;
  final VoidCallback? onTap;
  final Color? borderColor;
  final double borderWidth;

  @override
  Widget build(BuildContext context) {
    final diameter = _diameter;

    return GestureDetector(
      onTap: onTap,
      child: Stack(
        children: [
          Container(
            width: diameter,
            height: diameter,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              border: borderWidth > 0
                  ? Border.all(
                      color: borderColor ?? AppColors.primary,
                      width: borderWidth,
                    )
                  : null,
            ),
            child: ClipOval(child: _buildImage(context, diameter)),
          ),
          if (isOnline != null)
            Positioned(
              right: 0,
              bottom: 0,
              child: Container(
                width: _onlineIndicatorSize,
                height: _onlineIndicatorSize,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: isOnline! ? AppColors.success : AppColors.textDisabled,
                  border: Border.all(
                    color: Theme.of(context).colorScheme.surface,
                    width: 2,
                  ),
                ),
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildImage(BuildContext context, double diameter) {
    if (imageUrl != null && imageUrl!.isNotEmpty) {
      return CachedNetworkImage(
        imageUrl: imageUrl!,
        width: diameter,
        height: diameter,
        fit: BoxFit.cover,
        placeholder: (_, __) => _Initials(name: name, diameter: diameter, size: size),
        errorWidget: (_, __, ___) => _Initials(name: name, diameter: diameter, size: size),
      );
    }
    return _Initials(name: name, diameter: diameter, size: size);
  }

  double get _diameter => switch (size) {
        AvatarSize.xs => 24,
        AvatarSize.sm => 32,
        AvatarSize.md => 44,
        AvatarSize.lg => 64,
        AvatarSize.xl => 96,
      };

  double get _onlineIndicatorSize => switch (size) {
        AvatarSize.xs => 7,
        AvatarSize.sm => 9,
        AvatarSize.md => 11,
        AvatarSize.lg => 14,
        AvatarSize.xl => 18,
      };
}

class _Initials extends StatelessWidget {
  const _Initials({this.name, required this.diameter, required this.size});

  final String? name;
  final double diameter;
  final AvatarSize size;

  @override
  Widget build(BuildContext context) {
    final initials = name?.initials ?? '?';
    final fontSize = switch (size) {
      AvatarSize.xs => 9.0,
      AvatarSize.sm => 12.0,
      AvatarSize.md => 16.0,
      AvatarSize.lg => 24.0,
      AvatarSize.xl => 36.0,
    };

    return Container(
      width: diameter,
      height: diameter,
      color: AppColors.primaryContainer,
      alignment: Alignment.center,
      child: Text(
        initials,
        style: TextStyle(
          fontSize: fontSize,
          fontWeight: FontWeight.w700,
          color: AppColors.primary,
          height: 1,
        ),
      ),
    );
  }
}
