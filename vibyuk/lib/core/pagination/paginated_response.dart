import 'package:equatable/equatable.dart';

class PaginatedResponse<T> extends Equatable {
  const PaginatedResponse({
    required this.items,
    required this.currentPage,
    required this.totalPages,
    required this.totalItems,
    required this.perPage,
  });

  final List<T> items;
  final int currentPage;
  final int totalPages;
  final int totalItems;
  final int perPage;

  bool get hasNextPage => currentPage < totalPages;
  bool get hasPrevPage => currentPage > 1;
  bool get isLastPage => currentPage >= totalPages;
  bool get isEmpty => items.isEmpty;

  factory PaginatedResponse.fromJson(
    Map<String, dynamic> json,
    T Function(Map<String, dynamic>) fromJson,
  ) {
    final rawItems = json['data'] ?? json['items'] ?? [];
    final meta = json['meta'] as Map<String, dynamic>?;

    return PaginatedResponse(
      items: (rawItems as List)
          .map((e) => fromJson(Map<String, dynamic>.from(e as Map)))
          .toList(),
      currentPage: meta?['current_page'] as int? ?? 1,
      totalPages: meta?['last_page'] as int? ?? 1,
      totalItems: meta?['total'] as int? ?? 0,
      perPage: meta?['per_page'] as int? ?? rawItems.length,
    );
  }

  PaginatedResponse<T> appendItems(List<T> newItems) => PaginatedResponse(
        items: [...items, ...newItems],
        currentPage: currentPage + 1,
        totalPages: totalPages,
        totalItems: totalItems,
        perPage: perPage,
      );

  @override
  List<Object?> get props => [items, currentPage, totalPages, totalItems, perPage];
}
