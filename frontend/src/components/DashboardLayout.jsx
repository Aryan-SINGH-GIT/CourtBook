import { Outlet, Link, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import { Home, Calendar, DollarSign, List, LogOut, Sun, Moon, Menu, X } from 'lucide-react';
import { useState } from 'react';

export default function DashboardLayout({ children }) {
    const { user, logout } = useAuth();
    const { isDark, toggleTheme } = useTheme();
    const location = useLocation();
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

    const navigation = [
        { name: 'Dashboard', href: '/dashboard', icon: Home },
        { name: 'Book Court', href: '/dashboard/book', icon: Calendar },
        { name: 'My Bookings', href: '/dashboard/bookings', icon: List },
        { name: 'Pricing', href: '/dashboard/pricing', icon: DollarSign },
    ];

    const isActive = (path) => location.pathname === path;

    return (
        <div className={`min-h-screen flex flex-col transition-colors duration-200 ${isDark ? 'bg-black text-white' : 'bg-white text-black'}`}>

            {/* Top Navigation Bar */}
            <nav className={`sticky top-0 z-50 transition-colors duration-200 border-b ${isDark ? 'bg-black/80 border-zinc-800 backdrop-blur-md' : 'bg-white/80 border-zinc-200 backdrop-blur-md'
                }`}>
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex justify-between items-center h-16">

                        {/* Logo */}
                        <div className="flex-shrink-0 flex items-center gap-2">
                            {/* Logo Icon */}
                            <div className="w-8 h-8 bg-[#1e40af] rounded-lg flex items-center justify-center shadow-lg shadow-brand-blue/30">
                                <span className="text-white font-bold text-lg">C</span>
                            </div>
                            <span className="font-display font-bold text-xl tracking-tight">CourtBook</span>
                        </div>

                        {/* Desktop Navigation */}
                        <div className="hidden md:flex items-center space-x-1">
                            {navigation.map((item) => (
                                <Link
                                    key={item.name}
                                    to={item.href}
                                    className={`px-4 py-2 rounded-full text-sm font-medium transition-all duration-200 flex items-center gap-2 ${isActive(item.href)
                                        ? 'bg-[#1e40af] text-white shadow-md shadow-brand-blue/20'
                                        : 'text-zinc-500 hover:text-black hover:bg-zinc-100 dark:text-zinc-400 dark:hover:text-white dark:hover:bg-zinc-900'
                                        }`}
                                >
                                    <item.icon size={16} />
                                    {item.name}
                                </Link>
                            ))}
                        </div>

                        {/* Right Actions */}
                        <div className="hidden md:flex items-center gap-4">
                            <button
                                onClick={toggleTheme}
                                className={`p-2 rounded-full transition-colors ${isDark ? 'hover:bg-zinc-800 text-zinc-400 hover:text-white' : 'hover:bg-zinc-100 text-zinc-500 hover:text-black'
                                    }`}
                                aria-label="Toggle Theme"
                            >
                                {isDark ? <Sun size={20} /> : <Moon size={20} />}
                            </button>

                            <div className={`h-6 w-px ${isDark ? 'bg-zinc-800' : 'bg-zinc-200'}`}></div>

                            <div className="flex items-center gap-3">
                                <div className="text-right">
                                    <p className="text-sm font-medium leading-none">{user?.username || 'Guest'}</p>
                                </div>
                                <button
                                    onClick={logout}
                                    className="p-2 rounded-full hover:bg-zinc-100 dark:hover:bg-zinc-800 text-zinc-400 hover:text-red-500 transition-colors"
                                    title="Logout"
                                >
                                    <LogOut size={20} />
                                </button>
                            </div>
                        </div>

                        {/* Mobile Menu Button */}
                        <div className="flex md:hidden items-center gap-4">
                            <button
                                onClick={toggleTheme}
                                className={`p-2 rounded-full transition-colors ${isDark ? 'text-zinc-400 hover:text-white' : 'text-zinc-500 hover:text-black'
                                    }`}
                            >
                                {isDark ? <Sun size={20} /> : <Moon size={20} />}
                            </button>
                            <button
                                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                                className="p-2 rounded-md text-zinc-500 hover:bg-zinc-100 dark:hover:bg-zinc-900 transition-colors"
                            >
                                {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
                            </button>
                        </div>
                    </div>
                </div>

                {/* Mobile Navigation Menu */}
                {mobileMenuOpen && (
                    <div className={`md:hidden border-t ${isDark ? 'border-zinc-800 bg-black' : 'border-zinc-200 bg-white'}`}>
                        <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3">
                            {navigation.map((item) => (
                                <Link
                                    key={item.name}
                                    to={item.href}
                                    onClick={() => setMobileMenuOpen(false)}
                                    className={`block px-3 py-2 rounded-md text-base font-medium flex items-center gap-3 ${isActive(item.href)
                                        ? 'bg-brand-blue text-white'
                                        : 'text-zinc-500 hover:text-black hover:bg-zinc-100 dark:text-zinc-400 dark:hover:text-white dark:hover:bg-zinc-900'
                                        }`}
                                >
                                    <item.icon size={20} />
                                    {item.name}
                                </Link>
                            ))}
                            <button
                                onClick={logout}
                                className="w-full text-left block px-3 py-2 rounded-md text-base font-medium text-zinc-500 hover:text-red-500 hover:bg-zinc-100 dark:hover:bg-zinc-900 flex items-center gap-3 mt-4"
                            >
                                <LogOut size={20} />
                                Logout
                            </button>
                        </div>
                    </div>
                )}
            </nav>

            {/* Main Content Area */}
            <main className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-8">
                {children}
            </main>
        </div>
    );
}
