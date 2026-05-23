import 'dart:async';

import 'package:dartz/dartz.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:rxdart/rxdart.dart';
import 'package:vibyuk/core/config/app_config.dart';
import 'package:vibyuk/core/error/failures.dart';
import 'package:vibyuk/core/logging/app_logger.dart';
import 'package:vibyuk/core/pagination/paginated_response.dart';
import 'package:vibyuk/core/pagination/pagination_event.dart';
import 'package:vibyuk/core/pagination/pagination_params.dart';
import 'package:vibyuk/core/pagination/pagination_state.dart';

typedef PaginatedFetcher<T> = Future<Either<Failure, PaginatedResponse<T>>> Function(
  PaginationParams params,
);

abstract class PaginationBloc<T>
    extends Bloc<PaginationEvent, PaginationState<T>> {
  PaginationBloc() : super(const PaginationState()) {
    on<PaginationFetchStarted>(_onFetchStarted);
    on<PaginationNextPageRequested>(_onNextPageRequested);
    on<PaginationRefreshRequested>(_onRefreshRequested);
    on<PaginationSearchChanged>(
      _onSearchChanged,
      transformer: (events, mapper) => events
          .debounceTime(const Duration(milliseconds: 400))
          .switchMap(mapper),
    );
    on<PaginationFiltersApplied>(_onFiltersApplied);
  }

  /// Subclasses implement this to provide data.
  Future<Either<Failure, PaginatedResponse<T>>> fetchPage(PaginationParams params);

  Future<void> _onFetchStarted(
    PaginationFetchStarted event,
    Emitter<PaginationState<T>> emit,
  ) async {
    final params = event.params ?? const PaginationParams();
    emit(state.copyWith(status: PaginationStatus.loading, params: params));
    await _load(params, emit, isRefresh: false);
  }

  Future<void> _onNextPageRequested(
    PaginationNextPageRequested event,
    Emitter<PaginationState<T>> emit,
  ) async {
    if (!state.canLoadMore) return;
    final nextParams = state.params.nextPage();
    emit(state.copyWith(status: PaginationStatus.loadingMore, params: nextParams));
    await _load(nextParams, emit, isRefresh: false, append: true);
  }

  Future<void> _onRefreshRequested(
    PaginationRefreshRequested event,
    Emitter<PaginationState<T>> emit,
  ) async {
    final freshParams = state.params.resetPage();
    emit(state.copyWith(
      status: PaginationStatus.loading,
      params: freshParams,
      items: [],
      hasReachedEnd: false,
    ));
    await _load(freshParams, emit, isRefresh: true);
  }

  Future<void> _onSearchChanged(
    PaginationSearchChanged event,
    Emitter<PaginationState<T>> emit,
  ) async {
    final params = state.params.copyWith(search: event.query, page: 1);
    emit(state.copyWith(
      status: PaginationStatus.loading,
      params: params,
      items: [],
      hasReachedEnd: false,
    ));
    await _load(params, emit, isRefresh: true);
  }

  Future<void> _onFiltersApplied(
    PaginationFiltersApplied event,
    Emitter<PaginationState<T>> emit,
  ) async {
    final params = state.params.copyWith(filters: event.filters, page: 1);
    emit(state.copyWith(
      status: PaginationStatus.loading,
      params: params,
      items: [],
      hasReachedEnd: false,
    ));
    await _load(params, emit, isRefresh: true);
  }

  Future<void> _load(
    PaginationParams params,
    Emitter<PaginationState<T>> emit, {
    required bool isRefresh,
    bool append = false,
  }) async {
    final result = await fetchPage(params);

    result.fold(
      (failure) {
        AppLogger.warning('PaginationBloc: fetch failed — $failure');
        emit(state.copyWith(status: PaginationStatus.failure, failure: failure));
      },
      (response) {
        final allItems = append ? [...state.items, ...response.items] : response.items;
        emit(state.copyWith(
          status: allItems.isEmpty ? PaginationStatus.empty : PaginationStatus.success,
          items: allItems,
          hasReachedEnd: response.isLastPage,
          totalItems: response.totalItems,
          failure: null,
        ));
      },
    );
  }
}
