import 'package:dartz/dartz.dart';
import 'package:dio/dio.dart';
import 'package:vibyuk/core/error/exceptions.dart';
import 'package:vibyuk/core/error/failures.dart';
import 'package:vibyuk/core/logging/app_logger.dart';

typedef ResultFuture<T> = Future<Either<Failure, T>>;
typedef ResultStream<T> = Stream<Either<Failure, T>>;
typedef VoidResult = Future<Either<Failure, void>>;

abstract final class ErrorHandler {
  static Failure mapExceptionToFailure(AppException exception) {
    return switch (exception) {
      UnauthorizedException() => const UnauthorizedFailure(),
      ForbiddenException() => const ForbiddenFailure(),
      NotFoundException() => const NotFoundFailure(),
      NoInternetException() => const NoInternetFailure(),
      ServerException() => const ServerFailure(),
      ValidationException(:final message, :final code, :final fieldErrors) =>
        ValidationFailure(message: message, code: code, fieldErrors: fieldErrors),
      NetworkException(:final message, :final code, :final statusCode) =>
        NetworkFailure(message: message, code: code, statusCode: statusCode),
      CacheException(:final message, :final code) =>
        CacheFailure(message: message, code: code),
      StorageException(:final message, :final code) =>
        StorageFailure(message: message, code: code),
      ParseException(:final message, :final code) =>
        ParseFailure(message: message, code: code),
      TokenException(:final message) =>
        UnauthorizedFailure(message: message),
      _ => const UnknownFailure(),
    };
  }

  static Future<Either<Failure, T>> guard<T>(
    Future<T> Function() call, {
    String? context,
  }) async {
    try {
      final result = await call();
      return Right(result);
    } on AppException catch (e, stackTrace) {
      AppLogger.error(
        'AppException in ${context ?? 'guard'}',
        error: e,
        stackTrace: stackTrace,
      );
      return Left(mapExceptionToFailure(e));
    } on DioException catch (e, stackTrace) {
      AppLogger.error(
        'DioException in ${context ?? 'guard'}',
        error: e,
        stackTrace: stackTrace,
      );
      final networkEx = NetworkException.fromDioException(e);
      return Left(mapExceptionToFailure(networkEx));
    } catch (e, stackTrace) {
      AppLogger.error(
        'Unhandled error in ${context ?? 'guard'}',
        error: e,
        stackTrace: stackTrace,
      );
      return const Left(UnknownFailure());
    }
  }
}
