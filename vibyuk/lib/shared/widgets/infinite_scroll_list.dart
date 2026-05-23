import 'package:flutter/material.dart';
import 'package:vibyuk/core/config/app_config.dart';
import 'package:vibyuk/core/error/failures.dart';
import 'package:vibyuk/core/pagination/pagination_state.dart';
import 'package:vibyuk/core/theme/app_spacing.dart';
import 'package:vibyuk/shared/widgets/app_error_widget.dart';
import 'package:vibyuk/shared/widgets/app_loading.dart';

class InfiniteScrollList<T> extends StatefulWidget {
  const InfiniteScrollList({
    super.key,
    required this.state,
    required this.itemBuilder,
    required this.onLoadMore,
    required this.onRefresh,
    this.emptyTitle = 'Nothing here yet',
    this.emptyMessage = 'Check back later.',
    this.emptyIcon = Icons.inbox_outlined,
    this.emptyAction,
    this.emptyActionLabel,
    this.separatorBuilder,
    this.padding,
    this.shrinkWrap = false,
    this.physics,
    this.header,
    this.footer,
    this.onRetry,
    this.loadingItemCount = 6,
    this.loadingItemBuilder,
    this.scrollController,
  });

  final PaginationState<T> state;
  final Widget Function(BuildContext context, T item, int index) itemBuilder;
  final VoidCallback onLoadMore;
  final Future<void> Function() onRefresh;
  final String emptyTitle;
  final String emptyMessage;
  final IconData emptyIcon;
  final VoidCallback? emptyAction;
  final String? emptyActionLabel;
  final IndexedWidgetBuilder? separatorBuilder;
  final EdgeInsetsGeometry? padding;
  final bool shrinkWrap;
  final ScrollPhysics? physics;
  final Widget? header;
  final Widget? footer;
  final VoidCallback? onRetry;
  final int loadingItemCount;
  final WidgetBuilder? loadingItemBuilder;
  final ScrollController? scrollController;

  @override
  State<InfiniteScrollList<T>> createState() => _InfiniteScrollListState<T>();
}

class _InfiniteScrollListState<T> extends State<InfiniteScrollList<T>> {
  late final ScrollController _scrollController;
  bool _usingInternalController = false;

  @override
  void initState() {
    super.initState();
    if (widget.scrollController == null) {
      _scrollController = ScrollController();
      _usingInternalController = true;
    } else {
      _scrollController = widget.scrollController!;
    }
    _scrollController.addListener(_onScroll);
  }

  @override
  void dispose() {
    _scrollController.removeListener(_onScroll);
    if (_usingInternalController) _scrollController.dispose();
    super.dispose();
  }

  void _onScroll() {
    if (!_scrollController.hasClients) return;
    final maxScroll = _scrollController.position.maxScrollExtent;
    final currentScroll = _scrollController.offset;
    final threshold = maxScroll * AppConfig.paginationScrollThreshold;
    if (currentScroll >= threshold && widget.state.canLoadMore) {
      widget.onLoadMore();
    }
  }

  @override
  Widget build(BuildContext context) {
    if (widget.state.isLoading) {
      return _LoadingList(
        count: widget.loadingItemCount,
        itemBuilder: widget.loadingItemBuilder,
        padding: widget.padding,
        header: widget.header,
      );
    }

    if (widget.state.isFailure && widget.state.items.isEmpty) {
      return AppErrorWidget(
        failure: widget.state.failure!,
        onRetry: widget.onRetry,
      );
    }

    if (widget.state.isEmpty) {
      return EmptyStateWidget(
        title: widget.emptyTitle,
        message: widget.emptyMessage,
        icon: widget.emptyIcon,
        action: widget.emptyAction,
        actionLabel: widget.emptyActionLabel,
      );
    }

    return RefreshIndicator(
      onRefresh: widget.onRefresh,
      child: CustomScrollView(
        controller: _scrollController,
        physics: widget.physics ?? const AlwaysScrollableScrollPhysics(),
        shrinkWrap: widget.shrinkWrap,
        slivers: [
          if (widget.header != null) SliverToBoxAdapter(child: widget.header),
          SliverPadding(
            padding: widget.padding ?? EdgeInsets.zero,
            sliver: SliverList(
              delegate: widget.separatorBuilder != null
                  ? SliverChildBuilderDelegate(
                      (context, index) {
                        final itemIndex = index ~/ 2;
                        if (index.isOdd) {
                          return widget.separatorBuilder!(context, itemIndex);
                        }
                        return widget.itemBuilder(
                          context,
                          widget.state.items[itemIndex],
                          itemIndex,
                        );
                      },
                      childCount: widget.state.items.length * 2 - 1,
                    )
                  : SliverChildBuilderDelegate(
                      (context, index) => widget.itemBuilder(
                        context,
                        widget.state.items[index],
                        index,
                      ),
                      childCount: widget.state.items.length,
                    ),
            ),
          ),
          if (widget.state.isLoadingMore)
            const SliverToBoxAdapter(
              child: Padding(
                padding: EdgeInsets.all(AppSpacing.xl),
                child: Center(child: AppLoadingIndicator()),
              ),
            ),
          if (widget.state.isFailure && widget.state.items.isNotEmpty)
            SliverToBoxAdapter(
              child: AppErrorWidget(
                failure: widget.state.failure!,
                onRetry: widget.onRetry,
                compact: true,
              ),
            ),
          if (widget.footer != null) SliverToBoxAdapter(child: widget.footer),
          // Safe area bottom
          const SliverToBoxAdapter(child: SizedBox(height: AppSpacing.xxxl)),
        ],
      ),
    );
  }
}

class _LoadingList extends StatelessWidget {
  const _LoadingList({
    required this.count,
    this.itemBuilder,
    this.padding,
    this.header,
  });

  final int count;
  final WidgetBuilder? itemBuilder;
  final EdgeInsetsGeometry? padding;
  final Widget? header;

  @override
  Widget build(BuildContext context) {
    return CustomScrollView(
      physics: const NeverScrollableScrollPhysics(),
      slivers: [
        if (header != null) SliverToBoxAdapter(child: header),
        SliverPadding(
          padding: padding ?? EdgeInsets.zero,
          sliver: SliverList(
            delegate: SliverChildBuilderDelegate(
              (context, index) => itemBuilder != null
                  ? itemBuilder!(context)
                  : const _DefaultSkeletonItem(),
              childCount: count,
            ),
          ),
        ),
      ],
    );
  }
}

class _DefaultSkeletonItem extends StatelessWidget {
  const _DefaultSkeletonItem();

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(
        horizontal: AppSpacing.lg,
        vertical: AppSpacing.sm,
      ),
      child: Row(
        children: [
          AppSkeletonLoader(width: 48, height: 48, borderRadius: 24),
          AppSpacing.hGapMd,
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                AppSkeletonLoader(width: double.infinity, height: 14),
                AppSpacing.vGapSm,
                AppSkeletonLoader(width: 140, height: 12),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
