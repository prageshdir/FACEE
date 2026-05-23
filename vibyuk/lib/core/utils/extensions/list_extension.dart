extension ListX<T> on List<T> {
  T? get firstOrNull => isEmpty ? null : first;
  T? get lastOrNull => isEmpty ? null : last;

  List<T> separated(T separator) {
    if (isEmpty) return this;
    return [
      for (int i = 0; i < length; i++) ...[
        this[i],
        if (i < length - 1) separator,
      ],
    ];
  }

  List<List<T>> chunked(int size) {
    final chunks = <List<T>>[];
    for (var i = 0; i < length; i += size) {
      chunks.add(sublist(i, (i + size).clamp(0, length)));
    }
    return chunks;
  }

  List<T> unique({Object? Function(T element)? by}) {
    final seen = <Object?>{};
    return where((e) => seen.add(by != null ? by(e) : e)).toList();
  }

  Map<K, List<T>> groupBy<K>(K Function(T element) keyOf) {
    final map = <K, List<T>>{};
    for (final e in this) {
      (map[keyOf(e)] ??= []).add(e);
    }
    return map;
  }
}
