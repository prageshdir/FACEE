import 'package:freezed_annotation/freezed_annotation.dart';

part 'api_response.freezed.dart';
part 'api_response.g.dart';

@freezed
class ApiResponse<T> with _$ApiResponse<T> {
  const factory ApiResponse({
    required bool success,
    String? message,
    T? data,
    ApiMeta? meta,
    Map<String, dynamic>? errors,
  }) = _ApiResponse;

  factory ApiResponse.fromJson(
    Map<String, dynamic> json,
    T Function(Object?) fromJsonT,
  ) =>
      _$ApiResponseFromJson(json, fromJsonT);
}

@freezed
class ApiMeta with _$ApiMeta {
  const factory ApiMeta({
    required int currentPage,
    required int lastPage,
    required int perPage,
    required int total,
    String? nextPageUrl,
    String? prevPageUrl,
  }) = _ApiMeta;

  factory ApiMeta.fromJson(Map<String, dynamic> json) => _$ApiMetaFromJson(json);
}

@freezed
class PaginatedData<T> with _$PaginatedData<T> {
  const factory PaginatedData({
    required List<T> items,
    required int currentPage,
    required int totalPages,
    required int totalItems,
    required int perPage,
    @Default(false) bool hasNextPage,
    @Default(false) bool hasPrevPage,
  }) = _PaginatedData;
}
