import * as React from "react"
import { Link } from "@tanstack/react-router"
import { Menu, X, Music2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

interface NavbarProps {
  onMenuToggle: () => void
  isSidebarOpen: boolean
}

export function Navbar({ onMenuToggle, isSidebarOpen }: NavbarProps) {
  return (
    <header className="sticky top-0 z-40 w-full border-b border-slate-200 bg-white/95 backdrop-blur supports-[backdrop-filter]:bg-white/80 dark:border-slate-800 dark:bg-slate-950/95">
      <div className="flex h-16 items-center px-4 sm:px-6 lg:px-8">
        {/* Mobile menu button */}
        <Button
          variant="ghost"
          size="icon"
          onClick={onMenuToggle}
          className="lg:hidden"
          aria-label={isSidebarOpen ? "Close menu" : "Open menu"}
        >
          {isSidebarOpen ? (
            <X className="size-5" />
          ) : (
            <Menu className="size-5" />
          )}
        </Button>

        {/* Logo and Brand */}
        <Link
          to="/"
          className="flex items-center gap-2 font-bold text-xl hover:opacity-80 transition-opacity"
        >
          <div className="flex size-8 items-center justify-center rounded-lg bg-gradient-to-br from-purple-500 to-pink-500">
            <Music2 className="size-5 text-white" />
          </div>
          <span className="hidden sm:inline-block bg-gradient-to-r from-purple-600 via-pink-600 to-blue-600 bg-clip-text text-transparent">
            Gospel Keys
          </span>
        </Link>

        {/* Desktop Navigation */}
        <nav className="hidden lg:flex ml-8 gap-6" role="navigation">
          <NavLink to="/">Home</NavLink>
          <NavLink to="/curriculum">My Learning</NavLink>
          <NavLink to="/genres">Genres</NavLink>
        </nav>

        {/* Right side actions */}
        <div className="ml-auto flex items-center gap-3">
          <Button asChild variant="ghost" className="hidden sm:inline-flex">
            <Link to="/curriculum">Dashboard</Link>
          </Button>
          <Button asChild variant="primary">
            <Link to="/curriculum/new">Get Started</Link>
          </Button>
        </div>
      </div>
    </header>
  )
}

interface NavLinkProps {
  to: string
  children: React.ReactNode
}

function NavLink({ to, children }: NavLinkProps) {
  return (
    <Link
      to={to}
      className="text-sm font-medium text-slate-700 hover:text-slate-900 dark:text-slate-300 dark:hover:text-slate-100 transition-colors"
      activeProps={{
        className: "text-purple-600 dark:text-purple-400 font-semibold"
      }}
    >
      {children}
    </Link>
  )
}
