import 'package:equatable/equatable.dart';
import 'package:vibyuk/core/config/app_config.dart';

class PaginationParams extends Equatable {
  const PaginationParams({
    this.page = 1,
    this.limit = AppConfig.defaultPageSize,
    this.search,
    this.sortBy,
    this.sortOrder = SortOrder.desc,
    this.filters = const {},
  });

  final int page;
  final int limit;
  final String? search;
  final String? sortBy;
  final SortOrder sortOrder;
  final Map<String, dynamic> filters;

  Map<String, dynamic> toQueryParameters() => {
        'page': page,
        'limit': limit,
        if (search != null && search!.isNotEmpty) 'search': search,
        if (sortBy != null) 'sort_by': sortBy,
        'sort_order': sortOrder.value,
        ...filters,
      };

  PaginationParams copyWith({
    int? page,
    int? limit,
    String? search,
    String? sortBy,
    SortOrder? sortOrder,
    Map<String, dynamic>? filters,
  }) =>
      PaginationParams(
        page: page ?? this.page,
        limit: limit ?? this.limit,
        search: search ?? this.search,
        sortBy: sortBy ?? this.sortBy,
        sortOrder: sortOrder ?? this.sortOrder,
        filters: filters ?? this.filters,
      );

  PaginationParams nextPage() => copyWith(page: page + 1);
  PaginationParams resetPage() => copyWith(page: 1);

  @override
  List<Object?> get props => [page, limit, search, sortBy, sortOrder, filters];
}

enum SortOrder {
  asc('asc'),
  desc('desc');

  const SortOrder(this.value);
  final String value;
}
