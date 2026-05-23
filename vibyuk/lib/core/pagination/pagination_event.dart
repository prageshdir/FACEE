import 'package:equatable/equatable.dart';
import 'package:vibyuk/core/pagination/pagination_params.dart';

sealed class PaginationEvent extends Equatable {
  const PaginationEvent();

  @override
  List<Object?> get props => [];
}

final class PaginationFetchStarted extends PaginationEvent {
  const PaginationFetchStarted({this.params});
  final PaginationParams? params;

  @override
  List<Object?> get props => [params];
}

final class PaginationNextPageRequested extends PaginationEvent {
  const PaginationNextPageRequested();
}

final class PaginationRefreshRequested extends PaginationEvent {
  const PaginationRefreshRequested();
}

final class PaginationSearchChanged extends PaginationEvent {
  const PaginationSearchChanged(this.query);
  final String query;

  @override
  List<Object?> get props => [query];
}

final class PaginationFiltersApplied extends PaginationEvent {
  const PaginationFiltersApplied(this.filters);
  final Map<String, dynamic> filters;

  @override
  List<Object?> get props => [filters];
}
