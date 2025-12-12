/**
 * Test Utilities
 * 
 * Custom render function with providers and helpful utilities
 */
import { render, type RenderOptions } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { createMemoryHistory, RouterProvider, createRouter, createRootRoute, createRoute } from '@tanstack/react-router';
import type { ReactElement, ReactNode } from 'react';

// Create a fresh QueryClient for each test
function createTestQueryClient() {
    return new QueryClient({
        defaultOptions: {
            queries: {
                retry: false,
                gcTime: 0,
            },
            mutations: {
                retry: false,
            },
        },
    });
}

// All providers wrapper
interface ProvidersProps {
    children: ReactNode;
    queryClient?: QueryClient;
}

function Providers({ children, queryClient }: ProvidersProps) {
    const client = queryClient || createTestQueryClient();

    return (
        <QueryClientProvider client={client}>
            {children}
        </QueryClientProvider>
    );
}

// Custom render function
interface CustomRenderOptions extends Omit<RenderOptions, 'wrapper'> {
    queryClient?: QueryClient;
}

function customRender(
    ui: ReactElement,
    options: CustomRenderOptions = {}
) {
    const { queryClient, ...renderOptions } = options;

    return render(ui, {
        wrapper: ({ children }) => (
            <Providers queryClient={queryClient}>{children}</Providers>
        ),
        ...renderOptions,
    });
}

// Re-export everything
export * from '@testing-library/react';
export { customRender as render };
export { createTestQueryClient };

// Helper for creating mock routes for testing
export function createMockRouter(component: ReactElement) {
    const rootRoute = createRootRoute();
    const indexRoute = createRoute({
        getParentRoute: () => rootRoute,
        path: '/',
        component: () => component,
    });

    const router = createRouter({
        routeTree: rootRoute.addChildren([indexRoute]),
        history: createMemoryHistory({ initialEntries: ['/'] }),
    });

    return router;
}

// Helper for waiting for async operations
export function waitForLoadingToFinish() {
    return new Promise((resolve) => setTimeout(resolve, 0));
}
