import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/curriculum/')({
  component: RouteComponent,
})

function RouteComponent() {
  return <div>Hello "/curriculum/"!</div>
}
