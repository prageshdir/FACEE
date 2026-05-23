import 'package:dartz/dartz.dart';
import 'package:vibyuk/core/error/failures.dart';

extension EitherX<L extends Failure, R> on Either<L, R> {
  R? get rightOrNull => fold((_) => null, (r) => r);
  L? get leftOrNull => fold((l) => l, (_) => null);
  bool get isRight => fold((_) => false, (_) => true);
  bool get isLeft => !isRight;

  Either<L, T> flatMap<T>(Either<L, T> Function(R r) f) =>
      fold((l) => Left(l), (r) => f(r));

  R getOrElse(R Function(L failure) orElse) =>
      fold((l) => orElse(l), (r) => r);
}
