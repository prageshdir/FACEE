import 'package:equatable/equatable.dart';

sealed class Failure extends Equatable {
  final String message;
  final String? code;

  const Failure({required this.message, this.code});

  @override
  List<Object?> get props => [message, code];
}

final class NetworkFailure extends Failure {
  final int? statusCode;

  const NetworkFailure({
    required super.message,
    super.code,
    this.statusCode,
  });

  @override
  List<Object?> get props => [message, code, statusCode];
}

final class UnauthorizedFailure extends Failure {
  const UnauthorizedFailure({
    super.message = 'Session expired. Please log in again.',
    super.code = 'UNAUTHORIZED',
  });
}

final class ForbiddenFailure extends Failure {
  const ForbiddenFailure({
    super.message = 'You do not have permission to perform this action.',
    super.code = 'FORBIDDEN',
  });
}

final class NotFoundFailure extends Failure {
  const NotFoundFailure({
    super.message = 'The requested resource was not found.',
    super.code = 'NOT_FOUND',
  });
}

final class ValidationFailure extends Failure {
  final Map<String, List<String>>? fieldErrors;

  const ValidationFailure({
    super.message = 'Validation failed.',
    super.code = 'VALIDATION_ERROR',
    this.fieldErrors,
  });

  @override
  List<Object?> get props => [message, code, fieldErrors];
}

final class CacheFailure extends Failure {
  const CacheFailure({
    required super.message,
    super.code = 'CACHE_ERROR',
  });
}

final class StorageFailure extends Failure {
  const StorageFailure({
    required super.message,
    super.code = 'STORAGE_ERROR',
  });
}

final class ParseFailure extends Failure {
  const ParseFailure({
    required super.message,
    super.code = 'PARSE_ERROR',
  });
}

final class NoInternetFailure extends Failure {
  const NoInternetFailure({
    super.message = 'No internet connection.',
    super.code = 'NO_INTERNET',
  });
}

final class ServerFailure extends Failure {
  const ServerFailure({
    super.message = 'An internal server error occurred.',
    super.code = 'SERVER_ERROR',
  });
}

final class UnknownFailure extends Failure {
  const UnknownFailure({
    super.message = 'An unexpected error occurred.',
    super.code = 'UNKNOWN',
  });
}
