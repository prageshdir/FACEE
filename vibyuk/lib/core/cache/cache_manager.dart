import 'dart:convert';

import 'package:hive_flutter/hive_flutter.dart';
import 'package:vibyuk/core/config/app_config.dart';
import 'package:vibyuk/core/logging/app_logger.dart';

class CacheEntry {
  const CacheEntry({
    required this.data,
    required this.cachedAt,
  });

  final Map<String, dynamic> data;
  final DateTime cachedAt;

  bool isExpired(Duration maxAge) =>
      DateTime.now().isAfter(cachedAt.add(maxAge));

  Map<String, dynamic> toJson() => {
        'data': data,
        'cachedAt': cachedAt.millisecondsSinceEpoch,
      };

  factory CacheEntry.fromJson(Map<String, dynamic> json) => CacheEntry(
        data: Map<String, dynamic>.from(json['data'] as Map),
        cachedAt: DateTime.fromMillisecondsSinceEpoch(json['cachedAt'] as int),
      );
}

class CacheManager {
  CacheManager(this._box);

  final Box<String> _box;

  static const String _boxName = 'vibyuk_cache';

  static Future<CacheManager> open() async {
    final box = await Hive.openBox<String>(_boxName);
    return CacheManager(box);
  }

  Future<void> write(
    String key,
    Map<String, dynamic> data, {
    Duration? maxAge,
  }) async {
    try {
      final entry = CacheEntry(data: data, cachedAt: DateTime.now());
      await _box.put(key, jsonEncode(entry.toJson()));
      AppLogger.verbose('CacheManager: written key=$key');
    } catch (e) {
      AppLogger.warning('CacheManager: write failed for key=$key', error: e);
    }
  }

  Future<Map<String, dynamic>?> read(
    String key, {
    Duration? maxAge,
  }) async {
    try {
      final raw = _box.get(key);
      if (raw == null) return null;

      final entry = CacheEntry.fromJson(
        Map<String, dynamic>.from(jsonDecode(raw) as Map),
      );

      final effectiveMaxAge = maxAge ??
          const Duration(seconds: AppConfig.defaultCacheMaxAgeSeconds);

      if (entry.isExpired(effectiveMaxAge)) {
        AppLogger.verbose('CacheManager: expired key=$key');
        await _box.delete(key);
        return null;
      }

      return entry.data;
    } catch (e) {
      AppLogger.warning('CacheManager: read failed for key=$key', error: e);
      return null;
    }
  }

  Future<void> invalidate(String key) async {
    await _box.delete(key);
    AppLogger.verbose('CacheManager: invalidated key=$key');
  }

  Future<void> invalidatePattern(String pattern) async {
    final keys = _box.keys
        .whereType<String>()
        .where((k) => k.contains(pattern))
        .toList();
    await _box.deleteAll(keys);
    AppLogger.verbose('CacheManager: invalidated ${keys.length} keys matching "$pattern"');
  }

  Future<void> clear() async {
    await _box.clear();
    AppLogger.info('CacheManager: all cache cleared');
  }

  int get size => _box.length;
}
