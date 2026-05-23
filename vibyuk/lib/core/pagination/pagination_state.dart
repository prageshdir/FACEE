import 'package:equatable/equatable.dart';
import 'package:vibyuk/core/error/failures.dart';
import 'package:vibyuk/core/pagination/pagination_params.dart';

enum PaginationStatus { initial, loading, loadingMore, success, failure, empty }

class PaginationState<T> extends Equatable {
  const PaginationState({
    this.status = PaginationStatus.initial,
    this.items = const [],
    this.params = const PaginationParams(),
    this.failure,
    this.hasReachedEnd = false,
    this.totalItems = 0,
  });

  final PaginationStatus status;
  final List<T> items;
  final PaginationParams params;
  final Failure? failure;
  final bool hasReachedEnd;
  final int totalItems;

  bool get isInitial => status == PaginationStatus.initial;
  bool get isLoading => status == PaginationStatus.loading;
  bool get isLoadingMore => status == PaginationStatus.loadingMore;
  bool get isSuccess => status == PaginationStatus.success;
  bool get isFailure => status == PaginationStatus.failure;
  bool get isEmpty => status == PaginationStatus.empty;
  bool get canLoadMore => isSuccess && !hasReachedEnd && !isLoadingMore;

  PaginationState<T> copyWith({
    PaginationStatus? status,
    List<T>? items,
    PaginationParams? params,
    Failure? failure,
    bool? hasReachedEnd,
    int? totalItems,
  }) =>
      PaginationState(
        status: status ?? this.status,
        items: items ?? this.items,
        params: params ?? this.params,
        failure: failure,
        hasReachedEnd: hasReachedEnd ?? this.hasReachedEnd,
        totalItems: totalItems ?? this.totalItems,
      );

  @override
  List<Object?> get props => [status, items, params, failure, hasReachedEnd, totalItems];
}
