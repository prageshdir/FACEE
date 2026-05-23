import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:vibyuk/core/error/exceptions.dart';
import 'package:vibyuk/core/logging/app_logger.dart';

class SecureStorage {
  SecureStorage(this._storage);

  final FlutterSecureStorage _storage;

  static const _androidOptions = AndroidOptions(
    encryptedSharedPreferences: true,
  );

  static const _iosOptions = IOSOptions(
    accessibility: KeychainAccessibility.first_unlock_this_device,
  );

  Future<void> write({required String key, required String value}) async {
    try {
      await _storage.write(
        key: key,
        value: value,
        aOptions: _androidOptions,
        iOptions: _iosOptions,
      );
    } catch (e, st) {
      AppLogger.error('SecureStorage: write failed for key=$key', error: e, stackTrace: st);
      throw StorageException(message: 'Failed to write secure value: $e');
    }
  }

  Future<String?> read({required String key}) async {
    try {
      return await _storage.read(
        key: key,
        aOptions: _androidOptions,
        iOptions: _iosOptions,
      );
    } catch (e, st) {
      AppLogger.error('SecureStorage: read failed for key=$key', error: e, stackTrace: st);
      throw StorageException(message: 'Failed to read secure value: $e');
    }
  }

  Future<void> delete({required String key}) async {
    try {
      await _storage.delete(
        key: key,
        aOptions: _androidOptions,
        iOptions: _iosOptions,
      );
    } catch (e, st) {
      AppLogger.error('SecureStorage: delete failed for key=$key', error: e, stackTrace: st);
      throw StorageException(message: 'Failed to delete secure value: $e');
    }
  }

  Future<void> deleteAll() async {
    try {
      await _storage.deleteAll(
        aOptions: _androidOptions,
        iOptions: _iosOptions,
      );
    } catch (e, st) {
      AppLogger.error('SecureStorage: deleteAll failed', error: e, stackTrace: st);
      throw StorageException(message: 'Failed to clear secure storage: $e');
    }
  }

  Future<Map<String, String>> readAll() async {
    try {
      return await _storage.readAll(
        aOptions: _androidOptions,
        iOptions: _iosOptions,
      );
    } catch (e, st) {
      AppLogger.error('SecureStorage: readAll failed', error: e, stackTrace: st);
      throw StorageException(message: 'Failed to read all secure values: $e');
    }
  }

  Future<bool> containsKey({required String key}) async {
    try {
      return await _storage.containsKey(
        key: key,
        aOptions: _androidOptions,
        iOptions: _iosOptions,
      );
    } catch (e, st) {
      AppLogger.error('SecureStorage: containsKey failed for key=$key', error: e, stackTrace: st);
      throw StorageException(message: 'Failed to check key existence: $e');
    }
  }
}
