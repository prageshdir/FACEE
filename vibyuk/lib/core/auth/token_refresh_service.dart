import 'dart:async';

import 'package:dio/dio.dart';
import 'package:vibyuk/core/auth/token_manager.dart';
import 'package:vibyuk/core/error/exceptions.dart';
import 'package:vibyuk/core/logging/app_logger.dart';

class TokenRefreshService {
  TokenRefreshService({
    required TokenManager tokenManager,
    required Dio httpClient,
    required String refreshEndpoint,
  })  : _tokenManager = tokenManager,
        _httpClient = httpClient,
        _refreshEndpoint = refreshEndpoint;

  final TokenManager _tokenManager;
  final Dio _httpClient;
  final String _refreshEndpoint;

  Completer<String?>? _refreshCompleter;

  /// Ensures only one refresh is in-flight at a time.
  /// Concurrent callers await the same future.
  Future<String?> refreshIfNeeded() async {
    if (_refreshCompleter != null) {
      AppLogger.debug('TokenRefreshService: joining in-flight refresh');
      return _refreshCompleter!.future;
    }
    _refreshCompleter = Completer<String?>();
    try {
      final newToken = await _doRefresh();
      _refreshCompleter!.complete(newToken);
      return newToken;
    } catch (e) {
      _refreshCompleter!.completeError(e);
      rethrow;
    } finally {
      _refreshCompleter = null;
    }
  }

  Future<String?> _doRefresh() async {
    final refreshToken = await _tokenManager.getRefreshToken();
    if (refreshToken == null || refreshToken.isEmpty) {
      throw const TokenException(message: 'No refresh token available.');
    }

    AppLogger.info('TokenRefreshService: refreshing access token');

    final response = await _httpClient.post<Map<String, dynamic>>(
      _refreshEndpoint,
      data: {'refresh_token': refreshToken},
    );

    final data = response.data;
    if (data == null) throw const TokenException(message: 'Empty refresh response.');

    final accessToken = data['access_token'] as String?;
    final newRefreshToken = data['refresh_token'] as String?;
    final expiresIn = data['expires_in'] as int?;

    if (accessToken == null) {
      throw const TokenException(message: 'Missing access_token in refresh response.');
    }

    final expiresAt = DateTime.now().add(Duration(seconds: expiresIn ?? 3600));

    await _tokenManager.saveTokens(
      accessToken: accessToken,
      refreshToken: newRefreshToken ?? refreshToken,
      expiresAt: expiresAt,
    );

    AppLogger.info('TokenRefreshService: token refreshed successfully');
    return accessToken;
  }
}
