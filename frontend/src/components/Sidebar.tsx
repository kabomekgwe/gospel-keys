/**
 * Sidebar Navigation Component
 * 
 * Main navigation for Piano Keys application
 */

import { Link, useRouterState } from '@tanstack/react-router';
import {
    Home,
    Library,
    Settings,
    Music,
    ChevronLeft,
    ChevronRight,
    Dumbbell,
    BookOpen,
    Compass,
    Sparkles,
    GraduationCap,
    Plus
} from 'lucide-react';
import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useUIStore } from '../lib/uiStore';
import { UploadModal } from './UploadModal';

interface NavItem {
    to: string;
    icon: React.ReactNode;
    label: string;
}

const navItems: NavItem[] = [
    { to: '/', icon: <Home className="w-5 h-5" />, label: 'Home' },
    { to: '/library', icon: <Library className="w-5 h-5" />, label: 'Library' },
    { to: '/discover', icon: <Compass className="w-5 h-5" />, label: 'Discover' },
    { to: '/practice', icon: <Dumbbell className="w-5 h-5" />, label: 'Practice' },
    { to: '/curriculum', icon: <GraduationCap className="w-5 h-5" />, label: 'Curriculum' },
    { to: '/generator', icon: <Sparkles className="w-5 h-5" />, label: 'Generator' },
    { to: '/theory', icon: <BookOpen className="w-5 h-5" />, label: 'Theory' },
];

const bottomItems: NavItem[] = [
    { to: '/settings', icon: <Settings className="w-5 h-5" />, label: 'Settings' },
];

export default function Sidebar() {
    const [collapsed, setCollapsed] = useState(false);
    const routerState = useRouterState();
    const currentPath = routerState.location.pathname;
    const { openUploadModal } = useUIStore();

    const isActive = (path: string) => {
        if (path === '/') return currentPath === '/';
        return currentPath.startsWith(path);
    };

    return (
        <>
            <motion.aside
                initial={false}
                animate={{ width: collapsed ? 72 : 240 }}
                className="h-screen bg-slate-900 border-r border-slate-800 flex flex-col sticky top-0"
            >
                {/* Logo */}
                <div className="h-16 flex items-center px-4 border-b border-slate-800">
                    <Music className="w-8 h-8 text-cyan-400 flex-shrink-0" />
                    <AnimatePresence>
                        {!collapsed && (
                            <motion.span
                                initial={{ opacity: 0, width: 0 }}
                                animate={{ opacity: 1, width: 'auto' }}
                                exit={{ opacity: 0, width: 0 }}
                                className="ml-3 text-xl font-bold text-white whitespace-nowrap overflow-hidden"
                            >
                                Piano Keys
                            </motion.span>
                        )}
                    </AnimatePresence>
                </div>

                {/* Navigation */}
                <nav className="flex-1 py-4 px-3 flex flex-col gap-4">
                    {/* New Song CTA */}
                    <button
                        onClick={openUploadModal}
                        className={`
                            flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200
                            bg-gradient-to-r from-cyan-500 to-blue-500 hover:from-cyan-600 hover:to-blue-600 text-white shadow-lg shadow-cyan-500/20 group
                            ${collapsed ? 'justify-center' : ''}
                        `}
                    >
                        <Plus className="w-5 h-5 flex-shrink-0" />
                        <AnimatePresence>
                            {!collapsed && (
                                <motion.span
                                    initial={{ opacity: 0, width: 0 }}
                                    animate={{ opacity: 1, width: 'auto' }}
                                    exit={{ opacity: 0, width: 0 }}
                                    className="font-medium whitespace-nowrap overflow-hidden"
                                >
                                    New Song
                                </motion.span>
                            )}
                        </AnimatePresence>
                    </button>

                    <ul className="space-y-1">
                        {navItems.map((item) => (
                            <li key={item.to}>
                                <Link
                                    to={item.to}
                                    className={`
                      flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200
                      ${isActive(item.to)
                                            ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30'
                                            : 'text-slate-400 hover:text-white hover:bg-slate-800'}
                    `}
                                >
                                    <span className="flex-shrink-0">{item.icon}</span>
                                    <AnimatePresence>
                                        {!collapsed && (
                                            <motion.span
                                                initial={{ opacity: 0 }}
                                                animate={{ opacity: 1 }}
                                                exit={{ opacity: 0 }}
                                                className="font-medium whitespace-nowrap"
                                            >
                                                {item.label}
                                            </motion.span>
                                        )}
                                    </AnimatePresence>
                                </Link>
                            </li>
                        ))}
                    </ul>
                </nav>

                {/* Bottom Items */}
                <div className="py-4 px-3 border-t border-slate-800">
                    <ul className="space-y-1">
                        {bottomItems.map((item) => (
                            <li key={item.to}>
                                <Link
                                    to={item.to}
                                    className={`
                      flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200
                      ${isActive(item.to)
                                            ? 'bg-cyan-500/20 text-cyan-400'
                                            : 'text-slate-400 hover:text-white hover:bg-slate-800'}
                    `}
                                >
                                    <span className="flex-shrink-0">{item.icon}</span>
                                    <AnimatePresence>
                                        {!collapsed && (
                                            <motion.span
                                                initial={{ opacity: 0 }}
                                                animate={{ opacity: 1 }}
                                                exit={{ opacity: 0 }}
                                                className="font-medium whitespace-nowrap"
                                            >
                                                {item.label}
                                            </motion.span>
                                        )}
                                    </AnimatePresence>
                                </Link>
                            </li>
                        ))}
                    </ul>

                    {/* Collapse Toggle */}
                    <button
                        onClick={() => setCollapsed(!collapsed)}
                        className="mt-4 w-full flex items-center justify-center gap-2 px-3 py-2 text-slate-500 hover:text-white hover:bg-slate-800 rounded-lg transition-colors"
                    >
                        {collapsed ? (
                            <ChevronRight className="w-5 h-5" />
                        ) : (
                            <>
                                <ChevronLeft className="w-5 h-5" />
                                <span className="text-sm">Collapse</span>
                            </>
                        )}
                    </button>
                </div>
            </motion.aside>
            <UploadModal />
        </>
    );
}
