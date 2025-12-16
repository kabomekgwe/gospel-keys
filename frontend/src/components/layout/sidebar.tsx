import * as React from "react"
import { Link } from "@tanstack/react-router"
import {
  Home,
  BookOpen,
  Music,
  Calendar,
  BarChart3,
  Settings,
  Library,
  PlusCircle,
  GraduationCap
} from "lucide-react"
import { cn } from "@/lib/utils"
import { Badge } from "@/components/ui/badge"

interface SidebarProps {
  isOpen: boolean
  onClose: () => void
}

export function Sidebar({ isOpen, onClose }: SidebarProps) {
  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-slate-900/50 backdrop-blur-sm lg:hidden"
          onClick={onClose}
          aria-hidden="true"
        />
      )}

      {/* Sidebar */}
      <aside
        className={cn(
          "fixed top-0 left-0 z-50 h-full w-72 transform border-r border-slate-200 bg-white transition-transform duration-300 ease-in-out dark:border-slate-800 dark:bg-slate-950",
          "lg:sticky lg:top-16 lg:z-30 lg:h-[calc(100vh-4rem)] lg:translate-x-0",
          isOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"
        )}
      >
        <div className="flex h-full flex-col">
          {/* Sidebar Header (mobile only) */}
          <div className="flex h-16 items-center border-b border-slate-200 px-6 lg:hidden dark:border-slate-800">
            <Link
              to="/"
              className="flex items-center gap-2 font-bold text-xl"
              onClick={onClose}
            >
              <div className="flex size-8 items-center justify-center rounded-lg bg-gradient-to-br from-purple-500 to-pink-500">
                <Music className="size-5 text-white" />
              </div>
              <span className="bg-gradient-to-r from-purple-600 via-pink-600 to-blue-600 bg-clip-text text-transparent">
                Gospel Keys
              </span>
            </Link>
          </div>

          {/* Navigation */}
          <nav className="flex-1 overflow-y-auto p-4" role="navigation">
            <div className="space-y-1">
              {/* Main Navigation */}
              <NavSection title="Main">
                <NavItem
                  to="/"
                  icon={<Home className="size-5" />}
                  onClick={onClose}
                >
                  Home
                </NavItem>
                <NavItem
                  to="/curriculum"
                  icon={<BookOpen className="size-5" />}
                  onClick={onClose}
                >
                  My Curriculum
                </NavItem>
                <NavItem
                  to="/curriculum/daily"
                  icon={<Calendar className="size-5" />}
                  onClick={onClose}
                  badge={<Badge variant="new" size="sm">3</Badge>}
                >
                  Daily Practice
                </NavItem>
                <NavItem
                  to="/genres"
                  icon={<Library className="size-5" />}
                  onClick={onClose}
                >
                  Explore Genres
                </NavItem>
              </NavSection>

              {/* Quick Actions */}
              <NavSection title="Quick Actions">
                <NavItem
                  to="/curriculum/new"
                  icon={<PlusCircle className="size-5" />}
                  onClick={onClose}
                  className="text-purple-600 dark:text-purple-400"
                >
                  Create Curriculum
                </NavItem>
              </NavSection>

              {/* Genres */}
              <NavSection title="Genres">
                <GenreNavItem
                  to="/genres/gospel"
                  icon="🙏"
                  onClick={onClose}
                >
                  Gospel
                </GenreNavItem>
                <GenreNavItem
                  to="/genres/jazz"
                  icon="🎷"
                  onClick={onClose}
                >
                  Jazz
                </GenreNavItem>
                <GenreNavItem
                  to="/genres/blues"
                  icon="🎸"
                  onClick={onClose}
                >
                  Blues
                </GenreNavItem>
                <GenreNavItem
                  to="/genres/neosoul"
                  icon="✨"
                  onClick={onClose}
                >
                  Neo-Soul
                </GenreNavItem>
                <GenreNavItem
                  to="/genres/classical"
                  icon="🎹"
                  onClick={onClose}
                >
                  Classical
                </GenreNavItem>
                <GenreNavItem
                  to="/genres/reggae"
                  icon="🌴"
                  onClick={onClose}
                >
                  Reggae
                </GenreNavItem>
                <GenreNavItem
                  to="/genres/latin"
                  icon="🎺"
                  onClick={onClose}
                >
                  Latin
                </GenreNavItem>
                <GenreNavItem
                  to="/genres/rnb"
                  icon="🎤"
                  onClick={onClose}
                >
                  R&B
                </GenreNavItem>
              </NavSection>

              {/* Learning */}
              <NavSection title="Learning">
                <NavItem
                  to="/progress"
                  icon={<BarChart3 className="size-5" />}
                  onClick={onClose}
                  disabled
                >
                  Progress
                  <Badge variant="outline" size="sm" className="ml-auto">
                    Soon
                  </Badge>
                </NavItem>
                <NavItem
                  to="/achievements"
                  icon={<GraduationCap className="size-5" />}
                  onClick={onClose}
                  disabled
                >
                  Achievements
                  <Badge variant="outline" size="sm" className="ml-auto">
                    Soon
                  </Badge>
                </NavItem>
              </NavSection>
            </div>
          </nav>

          {/* Sidebar Footer */}
          <div className="border-t border-slate-200 p-4 dark:border-slate-800">
            <NavItem
              to="/settings"
              icon={<Settings className="size-5" />}
              onClick={onClose}
              disabled
            >
              Settings
            </NavItem>
          </div>
        </div>
      </aside>
    </>
  )
}

interface NavSectionProps {
  title: string
  children: React.ReactNode
}

function NavSection({ title, children }: NavSectionProps) {
  return (
    <div className="mb-4">
      <h3 className="mb-2 px-3 text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
        {title}
      </h3>
      <div className="space-y-1">
        {children}
      </div>
    </div>
  )
}

interface NavItemProps {
  to: string
  icon: React.ReactNode
  children: React.ReactNode
  onClick?: () => void
  badge?: React.ReactNode
  disabled?: boolean
  className?: string
}

function NavItem({ to, icon, children, onClick, badge, disabled, className }: NavItemProps) {
  if (disabled) {
    return (
      <div
        className={cn(
          "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-slate-400 cursor-not-allowed",
          className
        )}
      >
        {icon}
        <span className="flex-1">{children}</span>
        {badge}
      </div>
    )
  }

  return (
    <Link
      to={to}
      onClick={onClick}
      className={cn(
        "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-slate-700 transition-colors hover:bg-slate-100 hover:text-slate-900 dark:text-slate-300 dark:hover:bg-slate-800 dark:hover:text-slate-100",
        className
      )}
      activeProps={{
        className: "bg-purple-50 text-purple-700 hover:bg-purple-100 hover:text-purple-900 dark:bg-purple-950/50 dark:text-purple-400 dark:hover:bg-purple-950/80"
      }}
    >
      {icon}
      <span className="flex-1">{children}</span>
      {badge}
    </Link>
  )
}

interface GenreNavItemProps {
  to: string
  icon: string
  children: React.ReactNode
  onClick?: () => void
}

function GenreNavItem({ to, icon, children, onClick }: GenreNavItemProps) {
  return (
    <Link
      to={to}
      onClick={onClick}
      className="flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-slate-700 transition-colors hover:bg-slate-100 hover:text-slate-900 dark:text-slate-300 dark:hover:bg-slate-800 dark:hover:text-slate-100"
      activeProps={{
        className: "bg-purple-50 text-purple-700 hover:bg-purple-100 hover:text-purple-900 dark:bg-purple-950/50 dark:text-purple-400 dark:hover:bg-purple-950/80"
      }}
    >
      <span className="text-lg" aria-hidden="true">{icon}</span>
      <span>{children}</span>
    </Link>
  )
}
