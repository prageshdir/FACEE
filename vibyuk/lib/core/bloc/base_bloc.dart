import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:vibyuk/core/logging/app_logger.dart';

abstract class BaseBloc<E, S> extends Bloc<E, S> {
  BaseBloc(super.initialState);

  @override
  void onEvent(E event) {
    AppLogger.debug('${runtimeType}: event ${event.runtimeType}');
    super.onEvent(event);
  }

  @override
  void onTransition(Transition<E, S> transition) {
    AppLogger.verbose(
      '${runtimeType}: ${transition.currentState.runtimeType} → '
      '${transition.nextState.runtimeType}',
    );
    super.onTransition(transition);
  }

  @override
  void onError(Object error, StackTrace stackTrace) {
    AppLogger.error(
      '${runtimeType}: unhandled error',
      error: error,
      stackTrace: stackTrace,
    );
    super.onError(error, stackTrace);
  }
}
