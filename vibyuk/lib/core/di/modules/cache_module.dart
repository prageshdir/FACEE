import 'package:get_it/get_it.dart';
import 'package:vibyuk/core/cache/cache_manager.dart';

Future<void> registerCacheModule(GetIt sl) async {
  final cacheManager = await CacheManager.open();
  sl.registerSingleton<CacheManager>(cacheManager);
}
