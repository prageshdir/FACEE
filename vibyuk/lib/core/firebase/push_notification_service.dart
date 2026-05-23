import 'dart:async';

import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:vibyuk/core/logging/app_logger.dart';
import 'package:vibyuk/core/storage/secure_storage.dart';
import 'package:vibyuk/core/storage/storage_keys.dart';

@pragma('vm:entry-point')
Future<void> _onBackgroundMessage(RemoteMessage message) async {
  AppLogger.info('PushNotificationService: background message — ${message.messageId}');
  // Heavy processing should be deferred to when app is foregrounded.
}

class PushNotificationService {
  PushNotificationService({
    required SecureStorage secureStorage,
  }) : _secureStorage = secureStorage;

  final SecureStorage _secureStorage;
  final FirebaseMessaging _fcm = FirebaseMessaging.instance;

  final _messageController = StreamController<RemoteMessage>.broadcast();

  Stream<RemoteMessage> get onMessage => _messageController.stream;

  Future<void> initialize() async {
    FirebaseMessaging.onBackgroundMessage(_onBackgroundMessage);

    final settings = await _fcm.requestPermission(
      alert: true,
      badge: true,
      sound: true,
      provisional: false,
    );

    AppLogger.info(
      'PushNotificationService: permission=${settings.authorizationStatus}',
    );

    if (settings.authorizationStatus == AuthorizationStatus.authorized ||
        settings.authorizationStatus == AuthorizationStatus.provisional) {
      await _subscribeTo();
    }

    // Foreground messages
    FirebaseMessaging.onMessage.listen(_handleForegroundMessage);

    // App opened from background notification
    FirebaseMessaging.onMessageOpenedApp.listen(_handleNotificationTap);

    // App launched from terminated via notification
    final initial = await _fcm.getInitialMessage();
    if (initial != null) _handleNotificationTap(initial);
  }

  Future<void> _subscribeTo() async {
    final token = await _fcm.getToken();
    if (token != null) {
      await _secureStorage.write(key: StorageKeys.fcmToken, value: token);
      AppLogger.info('PushNotificationService: FCM token obtained');
    }

    _fcm.onTokenRefresh.listen((newToken) async {
      await _secureStorage.write(key: StorageKeys.fcmToken, value: newToken);
      AppLogger.info('PushNotificationService: FCM token refreshed');
      // TODO: Notify backend of new token via repository.
    });
  }

  void _handleForegroundMessage(RemoteMessage message) {
    AppLogger.debug('PushNotificationService: foreground — ${message.messageId}');
    _messageController.add(message);
  }

  void _handleNotificationTap(RemoteMessage message) {
    AppLogger.info('PushNotificationService: notification tapped — ${message.messageId}');
    // Route based on message.data['type'] once feature modules exist.
  }

  Future<String?> getToken() => _fcm.getToken();

  Future<void> deleteToken() => _fcm.deleteToken();

  Future<void> subscribeToTopic(String topic) async {
    await _fcm.subscribeToTopic(topic);
    AppLogger.info('PushNotificationService: subscribed to topic=$topic');
  }

  Future<void> unsubscribeFromTopic(String topic) async {
    await _fcm.unsubscribeFromTopic(topic);
    AppLogger.info('PushNotificationService: unsubscribed from topic=$topic');
  }

  void dispose() {
    _messageController.close();
  }
}
