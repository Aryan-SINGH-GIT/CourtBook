import { useState, useEffect } from 'react';
import { useTheme } from '../context/ThemeContext';
import { bookingAPI } from '../services/api';
import { Calendar, Clock, MapPin, CheckCircle, XCircle, AlertCircle } from 'lucide-react';

export default function MyBookings() {
    const { isDark } = useTheme();
    const [bookings, setBookings] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        loadBookings();
    }, []);

    const loadBookings = async () => {
        try {
            const response = await bookingAPI.getHistory(); // Using getHistory endpoint
            // Try to handle both array response and paginated response
            const data = response.data.results || response.data;
            if (Array.isArray(data)) {
                setBookings(data);
            } else {
                setBookings([]);
                console.error("Unexpected API response format for bookings:", response.data);
            }
        } catch (err) {
            console.error('Error loading bookings:', err);
            setError('Failed to load bookings');
        } finally {
            setLoading(false);
        }
    };

    const handleCancel = async (id) => {
        if (!confirm('Are you sure you want to cancel this booking?')) return;
        try {
            await bookingAPI.cancelBooking(id);
            loadBookings();
        } catch (err) {
            console.error('Cancel Error:', err);
            const msg = err.response?.data?.error || err.response?.data?.detail || 'Failed to cancel booking';
            setError(msg);
        }
    };

    return (
        <div className={`min-h-screen p-6 transition-colors duration-200 ${isDark ? 'bg-black text-white' : 'bg-white text-black'}`}>
            <h1 className="text-4xl font-display font-bold mb-2">My Bookings</h1>
            <p className={`text-lg mb-8 ${isDark ? 'text-zinc-400' : 'text-zinc-600'}`}>Manage your upcoming and past court reservations.</p>

            {error && (
                <div className="mb-6 p-4 bg-red-500/10 border border-red-500/50 text-red-500 rounded-xl flex items-center gap-2">
                    <AlertCircle size={20} />
                    {error}
                </div>
            )}

            {loading ? (
                <div className="text-center py-12 text-zinc-500">Loading bookings...</div>
            ) : null}

            {!loading && bookings.length === 0 ? (
                <div className={`${isDark ? 'bg-black' : 'bg-white'} rounded-xl p-12 border ${isDark ? 'border-zinc-800' : 'border-gray-200'} text-center`}>
                    <Calendar className="mx-auto mb-4 text-zinc-600" size={64} />
                    <h3 className={`text-xl font-semibold mb-2 ${isDark ? 'text-white' : 'text-gray-900'}`}>
                        No bookings yet
                    </h3>
                    <p className="text-zinc-500 mb-6">Start booking courts to see them here</p>
                    <a
                        href="/dashboard/book"
                        className="inline-block px-6 py-3 bg-[#1e40af] text-white rounded-lg font-semibold hover:opacity-90 transition"
                    >
                        Book a Court
                    </a>
                </div>
            ) : (
                <div className="space-y-4">
                    {bookings.map((booking) => (
                        <div
                            key={booking.id}
                            className={`${isDark ? 'bg-black' : 'bg-white'} rounded-xl p-6 border ${isDark ? 'border-zinc-800' : 'border-gray-200'} hover:border-brand-blue transition`}
                        >
                            <div className="flex items-start justify-between mb-4">
                                <div className="flex items-center gap-3">
                                    <div className={`p-3 rounded-lg ${booking.status === 'CONFIRMED' ? 'bg-[#1e40af] text-white' : 'bg-zinc-800 text-zinc-400'}`}>
                                        {booking.status === 'CONFIRMED' ? (
                                            <CheckCircle className="text-white" size={24} />
                                        ) : (
                                            <XCircle className="text-zinc-400" size={24} />
                                        )}
                                    </div>
                                    <div>
                                        <h3 className={`font-semibold text-lg ${isDark ? 'text-white' : 'text-gray-900'}`}>
                                            Booking #{booking.id}
                                        </h3>
                                        <span className={`text-sm font-bold ${booking.status === 'CONFIRMED' ? 'text-brand-blue' : 'text-zinc-500'}`}>
                                            {booking.status}
                                        </span>
                                    </div>
                                </div>

                                <div className="text-right">
                                    <p className={`text-2xl font-bold ${isDark ? 'text-cyan-500' : 'text-[#1e40af]'}`}>₹{booking.total_price}</p>
                                </div>
                            </div>

                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                                <div className="flex items-center gap-2 text-zinc-500">
                                    <Calendar size={18} />
                                    <span>{booking.date}</span>
                                </div>
                                <div className="flex items-center gap-2 text-zinc-500">
                                    <Clock size={18} />
                                    <span>{booking.start_time} - {booking.end_time}</span>
                                </div>
                                <div className="flex items-center gap-2 text-zinc-500">
                                    <MapPin size={18} />
                                    <span>{booking.resources.find(r => r.resource_type === 'COURT')?.resource_name || 'Court'}</span>
                                </div>
                            </div>

                            {booking.status === 'CONFIRMED' && (
                                <div className="flex justify-end pt-4 border-t border-zinc-100 dark:border-zinc-800">
                                    <button
                                        onClick={() => handleCancel(booking.id)}
                                        className="text-red-500 hover:text-red-400 font-medium text-sm transition-colors"
                                    >
                                        Cancel Booking
                                    </button>
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
