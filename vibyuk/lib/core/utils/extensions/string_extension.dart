extension StringX on String {
  String get capitalize =>
      isEmpty ? this : '${this[0].toUpperCase()}${substring(1).toLowerCase()}';

  String get titleCase => split(' ').map((w) => w.capitalize).join(' ');

  bool get isEmail => RegExp(r'^[\w.+-]+@[\w-]+\.[\w.]+$').hasMatch(this);

  bool get isUrl => Uri.tryParse(this)?.hasAbsolutePath ?? false;

  String truncate(int maxLength, {String ellipsis = '...'}) =>
      length <= maxLength ? this : '${substring(0, maxLength - ellipsis.length)}$ellipsis';

  String get initials {
    final parts = trim().split(RegExp(r'\s+'));
    if (parts.isEmpty) return '';
    if (parts.length == 1) return parts[0][0].toUpperCase();
    return '${parts[0][0]}${parts[parts.length - 1][0]}'.toUpperCase();
  }

  String? get nullIfEmpty => isEmpty ? null : this;

  String toSnakeCase() => replaceAllMapped(
        RegExp('([A-Z])'),
        (m) => '_${m.group(0)!.toLowerCase()}',
      ).replaceFirst(RegExp('^_'), '');

  bool get isNotBlank => trim().isNotEmpty;
  bool get isBlank => trim().isEmpty;
}

extension NullableStringX on String? {
  bool get isNullOrEmpty => this == null || this!.isEmpty;
  bool get isNotNullOrEmpty => !isNullOrEmpty;
  String get orEmpty => this ?? '';
}
