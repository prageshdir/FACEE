import 'package:logger/logger.dart';
import 'package:vibyuk/core/config/app_config.dart';

enum LogLevel { verbose, debug, info, warning, error, fatal }

abstract final class AppLogger {
  static Logger? _logger;

  static void initialize() {
    _logger = Logger(
      level: AppConfig.enableLogging ? Level.trace : Level.off,
      printer: PrettyPrinter(
        methodCount: 2,
        errorMethodCount: 8,
        lineLength: 120,
        colors: true,
        printEmojis: true,
        dateTimeFormat: DateTimeFormat.onlyTimeAndSinceStart,
      ),
      output: AppConfig.isDebug ? ConsoleOutput() : _ProductionOutput(),
    );
  }

  static Logger get _log {
    assert(_logger != null, 'AppLogger not initialized. Call AppLogger.initialize() first.');
    return _logger!;
  }

  static void verbose(String message, {Object? error, StackTrace? stackTrace}) {
    _log.t(message, error: error, stackTrace: stackTrace);
  }

  static void debug(String message, {Object? error, StackTrace? stackTrace}) {
    _log.d(message, error: error, stackTrace: stackTrace);
  }

  static void info(String message, {Object? error, StackTrace? stackTrace}) {
    _log.i(message, error: error, stackTrace: stackTrace);
  }

  static void warning(String message, {Object? error, StackTrace? stackTrace}) {
    _log.w(message, error: error, stackTrace: stackTrace);
  }

  static void error(String message, {Object? error, StackTrace? stackTrace}) {
    _log.e(message, error: error, stackTrace: stackTrace);
  }

  static void fatal(String message, {Object? error, StackTrace? stackTrace}) {
    _log.f(message, error: error, stackTrace: stackTrace);
  }
}

class _ProductionOutput extends LogOutput {
  @override
  void output(OutputEvent event) {
    // In production: forward to crash reporting (Crashlytics/Sentry).
    // Only log warnings and above to avoid PII leakage.
    if (event.level.index >= Level.warning.index) {
      // CrashlyticsService.recordLog(event.lines.join('\n'));
    }
  }
}
