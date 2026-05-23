import 'package:dartz/dartz.dart';
import 'package:vibyuk/core/cache/cache_manager.dart';
import 'package:vibyuk/core/error/error_handler.dart';
import 'package:vibyuk/core/error/failures.dart';
import 'package:vibyuk/core/logging/app_logger.dart';

abstract class BaseRepository {
  const BaseRepository({
    required CacheManager cacheManager,
  }) : _cacheManager = cacheManager;

  final CacheManager _cacheManager;

  /// Executes [networkCall] and on success caches the result under [cacheKey].
  /// On failure uses cached data if available (stale-while-revalidate).
  Future<Either<Failure, T>> executeWithCache<T>({
    required String cacheKey,
    required Future<T> Function() networkCall,
    required T Function(Map<String, dynamic> json) fromCache,
    required Map<String, dynamic> Function(T data) toCache,
    Duration? maxAge,
    bool forceRefresh = false,
  }) async {
    if (!forceRefresh) {
      final cached = await _tryReadCache<T>(
        cacheKey: cacheKey,
        fromCache: fromCache,
        maxAge: maxAge,
      );
      if (cached != null) {
        AppLogger.debug('BaseRepository: cache hit for $cacheKey');
        return Right(cached);
      }
    }

    final result = await ErrorHandler.guard(networkCall, context: cacheKey);

    result.fold(
      (failure) {
        AppLogger.warning('BaseRepository: network failed for $cacheKey — $failure');
      },
      (data) async {
        try {
          await _cacheManager.write(cacheKey, toCache(data), maxAge: maxAge);
        } catch (e) {
          AppLogger.warning('BaseRepository: cache write failed for $cacheKey', error: e);
        }
      },
    );

    // Fallback to stale cache on failure
    if (result.isLeft()) {
      final stale = await _tryReadCache<T>(
        cacheKey: cacheKey,
        fromCache: fromCache,
      );
      if (stale != null) {
        AppLogger.info('BaseRepository: returning stale cache for $cacheKey');
        return Right(stale);
      }
    }

    return result;
  }

  /// Executes a network call without caching.
  Future<Either<Failure, T>> execute<T>(
    Future<T> Function() call, {
    String? context,
  }) =>
      ErrorHandler.guard(call, context: context);

  Future<T?> _tryReadCache<T>({
    required String cacheKey,
    required T Function(Map<String, dynamic> json) fromCache,
    Duration? maxAge,
  }) async {
    try {
      final entry = await _cacheManager.read(cacheKey, maxAge: maxAge);
      if (entry != null) return fromCache(entry);
    } catch (e) {
      AppLogger.warning('BaseRepository: cache read failed for $cacheKey', error: e);
    }
    return null;
  }

  Future<void> invalidateCache(String cacheKey) =>
      _cacheManager.invalidate(cacheKey);

  Future<void> invalidateCachePattern(String pattern) =>
      _cacheManager.invalidatePattern(pattern);
}
