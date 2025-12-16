import { useState, useEffect } from 'react';
import { useTheme } from '../context/ThemeContext';
import { resourcesAPI, bookingAPI } from '../services/api';
import { Calendar, Activity, Layers, Users } from 'lucide-react';

export default function Dashboard() {
    const { isDark } = useTheme();
    const [stats, setStats] = useState({
        totalBookings: 0,
        activeCourts: 0,
        availableEquipment: 0,
        activeCoaches: 0
    });
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadDashboardData();
    }, []);

    const loadDashboardData = async () => {
        try {
            const [bookingsRes, courtsRes, equipmentRes, coachesRes] = await Promise.all([
                bookingAPI.getBookings(),
                resourcesAPI.getCourts(),
                resourcesAPI.getEquipment(),
                resourcesAPI.getCoaches(),
            ]);

            const bookings = bookingsRes.data.results || bookingsRes.data;
            const courts = courtsRes.data.results || courtsRes.data;
            const equipment = equipmentRes.data.results || equipmentRes.data;
            const coaches = coachesRes.data.results || coachesRes.data;

            // Calculate stats
            const totalBookings = bookings.length;
            const activeCourts = courts.filter(c => c.is_active).length;
            const availableEquipment = equipment.reduce((sum, item) => sum + (item.quantity || 0), 0);
            const activeCoaches = coaches.filter(c => c.is_active !== false).length;

            setStats({ totalBookings, activeCourts, availableEquipment, activeCoaches });
        } catch (error) {
            console.error('Error loading dashboard:', error);
        } finally {
            setLoading(false);
        }
    };

    const statCards = [
        {
            title: 'Total Bookings',
            value: stats.totalBookings,
            icon: Calendar,
            color: 'text-zinc-600 dark:text-white',
        },
        {
            title: 'Active Courts',
            value: stats.activeCourts,
            icon: Activity,
            color: 'text-zinc-600 dark:text-white',
        },
        {
            title: 'Equipment Items',
            value: stats.availableEquipment,
            icon: Layers,
            color: 'text-zinc-600 dark:text-white',
        },
        {
            title: 'Active Coaches',
            value: stats.activeCoaches,
            icon: Users,
            color: 'text-zinc-600 dark:text-white',
        },
    ];

    return (
        <div className={`min-h-screen p-6 transition-colors duration-200 ${isDark ? 'bg-black text-white' : 'bg-white text-black'}`}>
            <h1 className="text-4xl font-display font-bold mb-2">Dashboard</h1>
            <p className={`text-lg mb-8 ${isDark ? 'text-zinc-400' : 'text-zinc-600'}`}>Welcome back to your court management overview.</p>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                {statCards.map((stat, index) => (
                    <div
                        key={index}
                        className={`${isDark ? 'bg-black border-zinc-800' : 'bg-white border-gray-200'
                            } border rounded-2xl p-6 hover:shadow-lg transition-shadow`}
                    >
                        <div className="flex items-start justify-between mb-4">
                            <div className={`p-3 rounded-xl ${isDark ? 'bg-zinc-900' : 'bg-gray-50'}`}>
                                <stat.icon className={stat.color} size={24} />
                            </div>
                        </div>
                        <h3 className={`text-sm font-medium ${isDark ? 'text-zinc-500' : 'text-gray-500'} mb-1`}>
                            {stat.title}
                        </h3>
                        <p className={`text-3xl font-bold ${isDark ? 'text-white' : 'text-gray-900'}`}>
                            {stat.value}
                        </p>
                    </div>
                ))}
            </div>

            {/* Quick Actions */}
            <div className={`${isDark ? 'bg-black border-zinc-800' : 'bg-white border-gray-200'} border rounded-2xl p-6`}>
                <h2 className={`text-xl font-bold mb-4 ${isDark ? 'text-white' : 'text-gray-900'}`}>
                    Quick Actions
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <a
                        href="/dashboard/book"
                        className={`p-4 bg-transparent border border-brand-blue rounded-xl hover:bg-brand-blue/10 transition text-center font-bold ${isDark ? 'text-white' : 'text-brand-blue'}`}
                    >
                        Book a Court
                    </a>
                    <a
                        href="/dashboard/bookings"
                        className={`p-4 bg-transparent border ${isDark ? 'border-zinc-700' : 'border-gray-300'} hover:border-brand-blue hover:text-brand-blue rounded-xl transition text-center font-bold ${isDark ? 'text-white' : 'text-gray-700'}`}
                    >
                        View My Bookings
                    </a>
                    <a
                        href="/dashboard/pricing"
                        className={`p-4 bg-transparent border ${isDark ? 'border-zinc-700' : 'border-gray-300'} hover:border-brand-blue hover:text-brand-blue rounded-xl transition text-center font-bold ${isDark ? 'text-white' : 'text-gray-700'}`}
                    >
                        Check Pricing
                    </a>
                </div>
            </div>
        </div>
    );
}
