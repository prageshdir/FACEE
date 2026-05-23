import 'package:intl/intl.dart';

extension DateTimeX on DateTime {
  String get timeAgo {
    final now = DateTime.now();
    final diff = now.difference(this);

    if (diff.inSeconds < 60) return 'Just now';
    if (diff.inMinutes < 60) return '${diff.inMinutes}m ago';
    if (diff.inHours < 24) return '${diff.inHours}h ago';
    if (diff.inDays < 7) return '${diff.inDays}d ago';
    if (diff.inDays < 30) return '${(diff.inDays / 7).floor()}w ago';
    if (diff.inDays < 365) return '${(diff.inDays / 30).floor()}mo ago';
    return '${(diff.inDays / 365).floor()}y ago';
  }

  String format(String pattern) => DateFormat(pattern).format(this);

  String get displayDate => format('MMM d, yyyy');
  String get displayTime => format('h:mm a');
  String get displayDateTime => format('MMM d, yyyy • h:mm a');
  String get isoDate => format('yyyy-MM-dd');
  String get shortMonth => format('MMM');
  String get dayOfMonth => format('d');
  String get fullMonth => format('MMMM');

  bool get isToday {
    final now = DateTime.now();
    return year == now.year && month == now.month && day == now.day;
  }

  bool get isYesterday {
    final yesterday = DateTime.now().subtract(const Duration(days: 1));
    return year == yesterday.year && month == yesterday.month && day == yesterday.day;
  }

  bool get isFuture => isAfter(DateTime.now());
  bool get isPast => isBefore(DateTime.now());

  String get conversationDate {
    if (isToday) return 'Today';
    if (isYesterday) return 'Yesterday';
    return displayDate;
  }
}

extension NullableDateTimeX on DateTime? {
  String get orDash => this?.displayDate ?? '—';
  String get timeAgoOrDash => this?.timeAgo ?? '—';
}
