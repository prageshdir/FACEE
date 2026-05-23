import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:vibyuk/core/navigation/route_guards.dart';
import 'package:vibyuk/core/navigation/routes.dart';
import 'package:vibyuk/shared/widgets/app_loading.dart';

class AppRouter {
  AppRouter({required AuthGuard authGuard}) : _authGuard = authGuard;

  final AuthGuard _authGuard;

  late final GoRouter router = GoRouter(
    initialLocation: Routes.splash,
    debugLogDiagnostics: false,
    redirect: (context, state) => _authGuard.redirect(state),
    errorBuilder: (context, state) => _RouteErrorPage(error: state.error),
    routes: [
      GoRoute(
        path: Routes.splash,
        builder: (context, state) => const _SplashPage(),
      ),
      GoRoute(
        path: Routes.onboarding,
        builder: (context, state) => const _PlaceholderPage(title: 'Onboarding'),
      ),

      // Auth routes
      GoRoute(
        path: Routes.login,
        builder: (context, state) => const _PlaceholderPage(title: 'Login'),
      ),
      GoRoute(
        path: Routes.register,
        builder: (context, state) => const _PlaceholderPage(title: 'Register'),
      ),
      GoRoute(
        path: Routes.forgotPassword,
        builder: (context, state) => const _PlaceholderPage(title: 'Forgot Password'),
      ),
      GoRoute(
        path: Routes.resetPassword,
        builder: (context, state) => const _PlaceholderPage(title: 'Reset Password'),
      ),
      GoRoute(
        path: Routes.verifyEmail,
        builder: (context, state) => const _PlaceholderPage(title: 'Verify Email'),
      ),

      // Main shell with bottom navigation
      StatefulShellRoute.indexedStack(
        builder: (context, state, shell) => _MainShell(shell: shell),
        branches: [
          StatefulShellBranch(routes: [
            GoRoute(
              path: Routes.home,
              builder: (context, state) => const _PlaceholderPage(title: 'Home'),
            ),
          ]),
          StatefulShellBranch(routes: [
            GoRoute(
              path: Routes.explore,
              builder: (context, state) => const _PlaceholderPage(title: 'Explore'),
            ),
          ]),
          StatefulShellBranch(routes: [
            GoRoute(
              path: Routes.bookings,
              builder: (context, state) => const _PlaceholderPage(title: 'Bookings'),
            ),
          ]),
          StatefulShellBranch(routes: [
            GoRoute(
              path: Routes.messages,
              builder: (context, state) => const _PlaceholderPage(title: 'Messages'),
            ),
          ]),
          StatefulShellBranch(routes: [
            GoRoute(
              path: Routes.profile,
              builder: (context, state) => const _PlaceholderPage(title: 'Profile'),
            ),
          ]),
        ],
      ),

      // Notifications
      GoRoute(
        path: Routes.notifications,
        builder: (context, state) => const _PlaceholderPage(title: 'Notifications'),
      ),

      // Settings
      GoRoute(
        path: Routes.settings,
        builder: (context, state) => const _PlaceholderPage(title: 'Settings'),
        routes: [
          GoRoute(
            path: 'account',
            builder: (context, state) => const _PlaceholderPage(title: 'Account Settings'),
          ),
          GoRoute(
            path: 'notifications',
            builder: (context, state) => const _PlaceholderPage(title: 'Notification Settings'),
          ),
          GoRoute(
            path: 'privacy',
            builder: (context, state) => const _PlaceholderPage(title: 'Privacy Settings'),
          ),
        ],
      ),
    ],
  );
}

class _SplashPage extends StatefulWidget {
  const _SplashPage();

  @override
  State<_SplashPage> createState() => _SplashPageState();
}

class _SplashPageState extends State<_SplashPage> {
  @override
  void initState() {
    super.initState();
    // Router redirect handles navigation after auth check completes.
  }

  @override
  Widget build(BuildContext context) {
    return const Scaffold(body: Center(child: AppLoadingIndicator()));
  }
}

// Shell widget housing the main bottom navigation bar.
class _MainShell extends StatelessWidget {
  const _MainShell({required this.shell});

  final StatefulNavigationShell shell;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: shell,
      bottomNavigationBar: NavigationBar(
        selectedIndex: shell.currentIndex,
        onDestinationSelected: shell.goBranch,
        destinations: const [
          NavigationDestination(icon: Icon(Icons.home_outlined), selectedIcon: Icon(Icons.home), label: 'Home'),
          NavigationDestination(icon: Icon(Icons.explore_outlined), selectedIcon: Icon(Icons.explore), label: 'Explore'),
          NavigationDestination(icon: Icon(Icons.calendar_today_outlined), selectedIcon: Icon(Icons.calendar_today), label: 'Bookings'),
          NavigationDestination(icon: Icon(Icons.chat_bubble_outline), selectedIcon: Icon(Icons.chat_bubble), label: 'Messages'),
          NavigationDestination(icon: Icon(Icons.person_outline), selectedIcon: Icon(Icons.person), label: 'Profile'),
        ],
      ),
    );
  }
}

class _PlaceholderPage extends StatelessWidget {
  const _PlaceholderPage({required this.title});

  final String title;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text(title)),
      body: Center(child: Text(title, style: Theme.of(context).textTheme.headlineMedium)),
    );
  }
}

class _RouteErrorPage extends StatelessWidget {
  const _RouteErrorPage({this.error});

  final Exception? error;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.error_outline, size: 64, color: Colors.red),
            const SizedBox(height: 16),
            Text('Page not found', style: Theme.of(context).textTheme.headlineSmall),
            const SizedBox(height: 8),
            TextButton(
              onPressed: () => context.go(Routes.home),
              child: const Text('Go Home'),
            ),
          ],
        ),
      ),
    );
  }
}
