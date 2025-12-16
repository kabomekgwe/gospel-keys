import { createRouter } from '@tanstack/react-router'
import { setupRouterSsrQueryIntegration } from '@tanstack/react-router-ssr-query'
import { Link } from '@tanstack/react-router'
import * as TanstackQuery from './integrations/tanstack-query/root-provider'

// Import the generated route tree
import { routeTree } from './routeTree.gen'

// Default Not Found Component
function NotFoundComponent() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <div className="text-center px-6">
        <div className="text-8xl font-bold text-purple-400 mb-4">404</div>
        <h1 className="text-3xl font-bold text-white mb-2">Page Not Found</h1>
        <p className="text-slate-400 mb-8 max-w-md">
          The page you're looking for doesn't exist or has been moved.
        </p>
        <Link
          to="/"
          className="inline-flex items-center gap-2 px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white font-medium rounded-lg transition-colors"
        >
          ← Back to Home
        </Link>
      </div>
    </div>
  )
}

// Create a new router instance
export const getRouter = () => {
  const rqContext = TanstackQuery.getContext()

  const router = createRouter({
    routeTree,
    context: { ...rqContext },
    defaultPreload: 'intent',
    defaultNotFoundComponent: NotFoundComponent,
    Wrap: (props: { children: React.ReactNode }) => {
      return (
        <TanstackQuery.Provider {...rqContext}>
          {props.children}
        </TanstackQuery.Provider>
      )
    },
  })

  setupRouterSsrQueryIntegration({ router, queryClient: rqContext.queryClient })

  return router
}
