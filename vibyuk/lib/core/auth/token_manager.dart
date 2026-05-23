import 'dart:async';

import 'package:vibyuk/core/config/app_config.dart';
import 'package:vibyuk/core/error/exceptions.dart';
import 'package:vibyuk/core/logging/app_logger.dart';
import 'package:vibyuk/core/storage/secure_storage.dart';
import 'package:vibyuk/core/storage/storage_keys.dart';

class TokenManager {
  TokenManager(this._storage);

  final SecureStorage _storage;

  String? _cachedAccessToken;
  String? _cachedRefreshToken;
  DateTime? _cachedExpiry;

  Future<void> saveTokens({
    required String accessToken,
    required String refreshToken,
    required DateTime expiresAt,
  }) async {
    try {
      await Future.wait([
        _storage.write(key: StorageKeys.accessToken, value: accessToken),
        _storage.write(key: StorageKeys.refreshToken, value: refreshToken),
        _storage.write(
          key: StorageKeys.tokenExpiry,
          value: expiresAt.millisecondsSinceEpoch.toString(),
        ),
      ]);
      _cachedAccessToken = accessToken;
      _cachedRefreshToken = refreshToken;
      _cachedExpiry = expiresAt;
      AppLogger.debug('TokenManager: tokens saved, expires at $expiresAt');
    } catch (e) {
      throw TokenException(message: 'Failed to save tokens: $e');
    }
  }

  Future<String?> getAccessToken() async {
    if (_cachedAccessToken != null) return _cachedAccessToken;
    _cachedAccessToken = await _storage.read(key: StorageKeys.accessToken);
    return _cachedAccessToken;
  }

  Future<String?> getRefreshToken() async {
    if (_cachedRefreshToken != null) return _cachedRefreshToken;
    _cachedRefreshToken = await _storage.read(key: StorageKeys.refreshToken);
    return _cachedRefreshToken;
  }

  Future<bool> hasValidToken() async {
    final token = await getAccessToken();
    if (token == null || token.isEmpty) return false;
    final expiry = await _getExpiry();
    if (expiry == null) return false;
    return expiry.isAfter(DateTime.now());
  }

  Future<bool> isTokenExpiringSoon() async {
    final expiry = await _getExpiry();
    if (expiry == null) return true;
    final threshold = Duration(seconds: AppConfig.tokenRefreshThresholdSeconds);
    return expiry.isBefore(DateTime.now().add(threshold));
  }

  Future<void> clearTokens() async {
    try {
      await Future.wait([
        _storage.delete(key: StorageKeys.accessToken),
        _storage.delete(key: StorageKeys.refreshToken),
        _storage.delete(key: StorageKeys.tokenExpiry),
      ]);
      _cachedAccessToken = null;
      _cachedRefreshToken = null;
      _cachedExpiry = null;
      AppLogger.debug('TokenManager: tokens cleared');
    } catch (e) {
      throw TokenException(message: 'Failed to clear tokens: $e');
    }
  }

  Future<DateTime?> _getExpiry() async {
    if (_cachedExpiry != null) return _cachedExpiry;
    final raw = await _storage.read(key: StorageKeys.tokenExpiry);
    if (raw == null) return null;
    final ms = int.tryParse(raw);
    if (ms == null) return null;
    _cachedExpiry = DateTime.fromMillisecondsSinceEpoch(ms);
    return _cachedExpiry;
  }
}
