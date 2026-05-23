enum Flavor { dev, staging, production }

class FlavorConfig {
  final Flavor flavor;
  final String name;
  final String baseUrl;
  final String wsUrl;
  final bool enableLogging;
  final bool enableCrashlytics;
  final bool enableAnalytics;
  final bool enableMockData;

  const FlavorConfig({
    required this.flavor,
    required this.name,
    required this.baseUrl,
    required this.wsUrl,
    required this.enableLogging,
    required this.enableCrashlytics,
    required this.enableAnalytics,
    this.enableMockData = false,
  });

  static FlavorConfig? _instance;

  static FlavorConfig get instance {
    assert(_instance != null, 'FlavorConfig must be initialized before use.');
    return _instance!;
  }

  static void initialize(FlavorConfig config) => _instance = config;

  bool get isDev => flavor == Flavor.dev;
  bool get isStaging => flavor == Flavor.staging;
  bool get isProduction => flavor == Flavor.production;

  static const FlavorConfig dev = FlavorConfig(
    flavor: Flavor.dev,
    name: 'VIBYUK Dev',
    baseUrl: 'https://api.dev.vibyuk.com/v1',
    wsUrl: 'wss://ws.dev.vibyuk.com',
    enableLogging: true,
    enableCrashlytics: false,
    enableAnalytics: false,
    enableMockData: false,
  );

  static const FlavorConfig staging = FlavorConfig(
    flavor: Flavor.staging,
    name: 'VIBYUK Staging',
    baseUrl: 'https://api.staging.vibyuk.com/v1',
    wsUrl: 'wss://ws.staging.vibyuk.com',
    enableLogging: true,
    enableCrashlytics: true,
    enableAnalytics: false,
    enableMockData: false,
  );

  static const FlavorConfig production = FlavorConfig(
    flavor: Flavor.production,
    name: 'VIBYUK',
    baseUrl: 'https://api.vibyuk.com/v1',
    wsUrl: 'wss://ws.vibyuk.com',
    enableLogging: false,
    enableCrashlytics: true,
    enableAnalytics: true,
    enableMockData: false,
  );
}
