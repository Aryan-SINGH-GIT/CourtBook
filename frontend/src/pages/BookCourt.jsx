import { useState, useEffect } from 'react';
import { useTheme } from '../context/ThemeContext';
import { bookingAPI, pricingAPI } from '../services/api';
import { ChevronLeft, ChevronRight, ShoppingCart, Info, Check, Plus, Minus, X, Users, Dumbbell } from 'lucide-react';

export default function BookCourt() {
    const { isDark } = useTheme();
    // Helper to format date as YYYY-MM-DD in local time
    const formatDateLocal = (date) => {
        const offset = date.getTimezoneOffset();
        const localDate = new Date(date.getTime() - (offset * 60 * 1000));
        return localDate.toISOString().split('T')[0];
    };

    const [selectedDate, setSelectedDate] = useState(formatDateLocal(new Date()));
    const [matrix, setMatrix] = useState([]);
    const [loading, setLoading] = useState(true);
    const [selectedSlots, setSelectedSlots] = useState([]);
    const [dates, setDates] = useState([]);
    const [pricing, setPricing] = useState({ court: 200, coach: 500, equipment: 100 });

    // Addon Modal State
    const [showAddonModal, setShowAddonModal] = useState(false);
    const [addonLoading, setAddonLoading] = useState(false);
    const [availableCoaches, setAvailableCoaches] = useState([]);
    const [availableEquipment, setAvailableEquipment] = useState([]);

    // Selected Addons
    const [selectedEquipment, setSelectedEquipment] = useState({}); // { id: quantity }
    const [selectedCoach, setSelectedCoach] = useState(null); // coachId or null

    // Fetch pricing config
    useEffect(() => {
        const fetchPricing = async () => {
            try {
                const response = await pricingAPI.getConfig();
                const courtPrice = response.data.base_prices.find(p => p.resource_type === 'COURT_HOUR')?.price || 200;
                const coachPrice = response.data.base_prices.find(p => p.resource_type === 'COACH_HOUR')?.price || 500;
                const equipPrice = response.data.base_prices.find(p => p.resource_type === 'EQUIPMENT_HOUR')?.price || 100;
                setPricing({ court: parseFloat(courtPrice), coach: parseFloat(coachPrice), equipment: parseFloat(equipPrice) });
            } catch (error) {
                console.error('Failed to fetch pricing:', error);
            }
        };
        fetchPricing();
    }, []);

    // Generate next 7 days for DateStrip
    useEffect(() => {
        const today = new Date();
        const nextDays = [];
        for (let i = 0; i < 7; i++) {
            const date = new Date(today);
            date.setDate(today.getDate() + i);
            nextDays.push({
                full: formatDateLocal(date),
                day: date.toLocaleDateString('en-US', { weekday: 'short' }),
                date: date.getDate(),
                month: date.toLocaleDateString('en-US', { month: 'short' })
            });
        }
        setDates(nextDays);
    }, []);

    // Fetch matrix when date changes
    useEffect(() => {
        loadMatrix();
        setSelectedSlots([]); // Clear selection on date change
    }, [selectedDate]);

    const loadMatrix = async () => {
        setLoading(true);
        try {
            const response = await bookingAPI.getDailyMatrix(selectedDate);
            setMatrix(response.data);
        } catch (error) {
            console.error("Failed to load availability", error);
        } finally {
            setLoading(false);
        }
    };

    const handleSlotClick = (courtId, timeSlot) => {
        if (timeSlot.is_booked && !timeSlot.is_user_booking) return;

        const slotId = `${courtId}-${timeSlot.time}`;
        const isSelected = selectedSlots.some(s => s.id === slotId);

        if (isSelected) {
            setSelectedSlots(selectedSlots.filter(s => s.id !== slotId));
        } else {
            // Enforce single court selection for simplicity in this version
            const differentCourt = selectedSlots.find(s => s.courtId !== courtId);
            if (differentCourt) {
                if (!confirm("You can only book one court at a time. Clear previous selection?")) return;
                setSelectedSlots([{
                    id: slotId,
                    courtId,
                    courtName: matrix.find(c => c.id === courtId)?.name,
                    time: timeSlot.time,
                    price: parseFloat(timeSlot.price || pricing.court)
                }]);
                return;
            }

            setSelectedSlots([...selectedSlots, {
                id: slotId,
                courtId,
                courtName: matrix.find(c => c.id === courtId)?.name,
                time: timeSlot.time,
                price: parseFloat(timeSlot.price || pricing.court)
            }]);
        }
    };

    const getSlotStatus = (courtId, timeSlot) => {
        const slotId = `${courtId}-${timeSlot.time}`;
        if (selectedSlots.some(s => s.id === slotId)) return 'selected';
        if (timeSlot.is_user_booking) return 'my-booking';
        if (timeSlot.is_booked) return 'booked';
        return 'available';
    };

    const initiateBooking = async () => {
        if (selectedSlots.length === 0) return;

        // Open Modal and Fetch Addons
        setShowAddonModal(true);
        setAddonLoading(true);

        // Calculate time range
        const times = selectedSlots.map(s => s.time).sort();
        const startTime = times[0].substring(0, 5);
        // End time is last slot + 1 hour
        const lastHour = parseInt(times[times.length - 1].split(':')[0]);
        const endTime = `${(lastHour + 1).toString().padStart(2, '0')}:00`;

        try {
            const response = await bookingAPI.getAddonAvailability(selectedDate, startTime, endTime);
            setAvailableCoaches(response.data.coaches);
            setAvailableEquipment(response.data.equipment);
        } catch (error) {
            console.error("Failed to load addons", error);
            alert("Could not load add-on options. Please try again.");
            setShowAddonModal(false);
        } finally {
            setAddonLoading(false);
        }
    };

    const confirmBooking = async () => {
        // Prepare booking data
        const courtId = selectedSlots[0].courtId;
        const times = selectedSlots.map(s => s.time).sort();
        const startTime = times[0].substring(0, 5);
        const lastHour = parseInt(times[times.length - 1].split(':')[0]);
        const endTime = `${(lastHour + 1).toString().padStart(2, '0')}:00`;

        // Prepare equipment list
        const equipmentList = Object.entries(selectedEquipment).map(([id, quantity]) => ({
            id: parseInt(id),
            quantity
        }));

        try {
            await bookingAPI.createBooking({
                date: selectedDate,
                start_time: startTime,
                end_time: endTime,
                court_id: parseInt(courtId),
                equipment: equipmentList,
                coach_id: selectedCoach
            });
            alert('Booking Successful!');
            setShowAddonModal(false);
            setSelectedEquipment({});
            setSelectedCoach(null);
            loadMatrix();
            setSelectedSlots([]);
        } catch (err) {
            alert('Booking Failed: ' + (err.response?.data?.error || err.message));
        }
    };

    // Addon helpers
    const updateEquipment = (id, delta, max) => {
        const current = selectedEquipment[id] || 0;
        const potential = current + delta;

        if (potential >= 0 && potential <= max) {
            const newCounts = { ...selectedEquipment };
            if (potential === 0) delete newCounts[id];
            else newCounts[id] = potential;
            setSelectedEquipment(newCounts);
        }
    };

    return (
        <div className={`min-h-screen p-6 transition-colors duration-200 ${isDark ? 'bg-brand-black text-brand-light' : 'bg-brand-white text-brand-black'}`}>
            {/* Header Section */}
            <div className="flex flex-col md:flex-row justify-between items-center mb-10 max-w-7xl mx-auto">
                <div>
                    <h1 className="text-4xl font-display font-bold mb-2 tracking-tight">Reserve Your Court</h1>
                    <p className={`text-lg ${isDark ? 'text-zinc-400' : 'text-zinc-500'}`}>Select a time slot to start your game.</p>
                </div>
                <div className="flex items-center gap-4 mt-4 md:mt-0">
                    <div className="text-right bg-brand-blue/10 px-6 py-3 rounded-2xl border border-brand-blue/20">
                        <p className="text-2xl font-bold font-display text-brand-blue">From ₹{pricing.court}<span className="text-sm font-normal text-zinc-500 ml-1">/hour</span></p>
                    </div>
                </div>
            </div>

            <div className="flex flex-col lg:flex-row gap-8 max-w-7xl mx-auto">
                {/* Main Booking Area */}
                <div className="flex-1">
                    {/* Date Strip */}
                    <div className="flex items-center gap-3 mb-8 overflow-x-auto pb-4 no-scrollbar">
                        {dates.map((d) => (
                            <button
                                key={d.full}
                                onClick={() => setSelectedDate(d.full)}
                                className={`flex flex-col items-center justify-center min-w-[90px] p-4 rounded-xl border-2 transition-all duration-200 ${selectedDate === d.full
                                    ? 'bg-[#1e40af] border-[#1e40af] text-white shadow-lg transform scale-105'
                                    : 'bg-transparent border-zinc-200 dark:border-black hover:border-brand-blue dark:hover:border-brand-blue text-zinc-500 dark:text-white'
                                    }`}
                            >
                                <span className="text-xs font-bold uppercase tracking-wider opacity-80 mb-1">{d.day}</span>
                                <span className="text-2xl font-bold font-display">{d.date}</span>
                            </button>
                        ))}
                    </div>

                    {/* Booking Grid */}
                    <div className={`rounded-3xl shadow-sm border overflow-hidden ${isDark ? 'bg-brand-dark border-black' : 'bg-white border-zinc-200'}`}>
                        {loading ? (
                            <div className="p-20 text-center text-zinc-500 animate-pulse">Loading schedule...</div>
                        ) : (
                            <div className="overflow-x-auto">
                                <div className="min-w-[600px] p-6">
                                    {/* Grid Header */}
                                    <div className="grid grid-cols-[80px_repeat(auto-fit,minmax(100px,1fr))] gap-4 mb-4">
                                        <div className={`text-center self-end pb-2 font-medium text-sm ${isDark ? 'text-white' : 'text-zinc-400'}`}>Time</div>
                                        {matrix.map(court => (
                                            <div key={court.id} className={`p-3 text-center font-bold rounded-t-lg ${isDark ? 'text-white' : 'text-zinc-700'}`}>
                                                {court.name}
                                            </div>
                                        ))}
                                    </div>

                                    {/* Grid Body */}
                                    <div className="space-y-3">
                                        {matrix.length > 0 && matrix[0].slots.map((slot, timeIndex) => (
                                            <div key={timeIndex} className="grid grid-cols-[80px_repeat(auto-fit,minmax(100px,1fr))] gap-4 items-center group">
                                                {/* Time Label */}
                                                <div className={`text-center text-sm font-medium ${isDark ? 'text-white' : 'text-zinc-400'}`}>
                                                    {slot.time.substring(0, 5)}
                                                </div>

                                                {/* Court Slots */}
                                                {matrix.map(court => {
                                                    const courtSlot = court.slots[timeIndex];
                                                    const status = getSlotStatus(court.id, courtSlot);

                                                    return (
                                                        <button
                                                            key={`${court.id}-${timeIndex}`}
                                                            onClick={() => handleSlotClick(court.id, courtSlot)}
                                                            disabled={status === 'booked' || status === 'my-booking'}
                                                            title={status === 'available' ? `₹${courtSlot.price}` : ''}
                                                            className={`
                                                                h-12 rounded-lg border transition-all duration-200 w-full relative group flex items-center justify-center overflow-hidden
                                                                ${status === 'available' ?
                                                                    (isDark
                                                                        ? 'bg-zinc-900/30 border-zinc-800 text-zinc-500 hover:border-[#1e40af] hover:text-[#1e40af] hover:bg-[#1e40af]/10'
                                                                        : 'bg-white border-zinc-200 text-zinc-400 hover:border-[#1e40af] hover:text-[#1e40af] hover:bg-[#1e40af]/5')
                                                                    : ''}
                                                                ${status === 'available' && parseFloat(courtSlot.price || 0) > 440 ? (isDark ? 'border-amber-900/30 bg-amber-900/5' : 'border-amber-200 bg-amber-50') : ''}
                                                                ${status === 'selected' ? '!bg-[#1e40af] !border-[#1e40af] text-white shadow-[0_0_20px_rgba(30,64,175,0.4)] scale-[1.02] z-10' : ''}
                                                                ${status === 'booked' ? 'bg-zinc-100 dark:bg-zinc-900 border-transparent cursor-not-allowed opacity-40' : ''}
                                                                ${status === 'my-booking' ? 'bg-[#1e40af]/10 border-[#1e40af]/50 text-[#1e40af] cursor-not-allowed' : ''}
                                                            `}
                                                        >
                                                            {status === 'available' && (
                                                                <>
                                                                    {parseFloat(courtSlot.price || 0) > 440 && (
                                                                        <div className="absolute top-1 right-1 w-1.5 h-1.5 rounded-full bg-amber-500 shadow-[0_0_5px_rgba(245,158,11,0.5)]"></div>
                                                                    )}

                                                                    <div className="flex flex-col items-center">
                                                                        <span className={`text-xs font-bold ${parseFloat(courtSlot.price || 0) > 440 ? 'text-amber-500/80 group-hover:text-amber-600' : ''}`}>+</span>
                                                                        <span className="text-[10px] font-medium opacity-0 group-hover:opacity-100 absolute bottom-0.5 transition-opacity">₹{courtSlot.price}</span>
                                                                    </div>
                                                                </>
                                                            )}
                                                            {status === 'selected' && <Check size={18} className="mx-auto" />}
                                                            {status === 'booked' && <X size={16} className="mx-auto text-zinc-400" />}
                                                            {status === 'my-booking' && <Users size={16} className="mx-auto" />}
                                                        </button>
                                                    );
                                                })}
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>
                </div>

                {/* Sidebar / Summary */}
                <div className="lg:w-96">
                    <div className={`rounded-3xl shadow-xl border p-8 sticky top-24 ${isDark ? 'bg-brand-dark border-black' : 'bg-white border-zinc-200'}`}>
                        <h3 className="text-2xl font-bold mb-8 font-display">Summary</h3>

                        {selectedSlots.length === 0 ? (
                            <div className="text-center py-12">
                                <div className={`w-16 h-16 mx-auto mb-4 rounded-full flex items-center justify-center ${isDark ? 'bg-zinc-800 text-white' : 'bg-zinc-100 text-zinc-300'}`}>
                                    <ShoppingCart size={24} />
                                </div>
                                <p className={`${isDark ? 'text-white' : 'text-zinc-500'}`}>Select a slot on the grid to book.</p>
                            </div>
                        ) : (
                            <div className="space-y-6">
                                <div className="space-y-3">
                                    {selectedSlots.map(slot => (
                                        <div key={slot.id} className={`flex justify-between items-center p-4 rounded-2xl border ${isDark ? 'bg-zinc-900/50 border-zinc-800' : 'bg-zinc-50 border-zinc-100'}`}>
                                            <div>
                                                <p className="font-bold">{slot.courtName}</p>
                                                <p className={`text-sm ${isDark ? 'text-zinc-300' : 'text-zinc-500'}`}>
                                                    {slot.time.substring(0, 5)} - {(parseInt(slot.time.split(':')[0]) + 1).toString().padStart(2, '0')}:00
                                                </p>
                                            </div>
                                            <div className="flex items-center gap-3">
                                                <span className="font-bold text-brand-blue">₹{slot.price}</span>
                                                <button
                                                    onClick={() => handleSlotClick(slot.courtId, { time: slot.time })}
                                                    className="p-2 hover:bg-red-500/10 text-zinc-400 hover:text-red-500 rounded-lg transition-colors"
                                                >
                                                    <X size={18} />
                                                </button>
                                            </div>
                                        </div>
                                    ))}
                                </div>

                                <div className={`border-t pt-6 ${isDark ? 'border-zinc-800' : 'border-zinc-100'}`}>
                                    <div className="flex justify-between items-end mb-2">
                                        <span className={`text-sm ${isDark ? 'text-white' : 'text-zinc-500'}`}>Total Amount</span>
                                        <span className="text-3xl font-bold font-display">₹{selectedSlots.reduce((sum, slot) => sum + slot.price, 0)}</span>
                                    </div>
                                </div>

                                <button
                                    onClick={initiateBooking}
                                    className="w-full py-4 bg-transparent border-2 border-[#1e40af] text-[#1e40af] rounded-xl font-bold text-lg hover:bg-[#1e40af] hover:text-white transition-all shadow-lg shadow-brand-blue/10"
                                >
                                    Proceed to Add-ons
                                </button>
                            </div>
                        )}

                        {/* Legend */}
                        <div className={`mt-8 pt-8 border-t ${isDark ? 'border-zinc-800' : 'border-zinc-100'}`}>
                            <div className="grid grid-cols-2 gap-4 text-sm">
                                <div className="flex items-center gap-2">
                                    <div className={`w-3 h-3 rounded-full border ${isDark ? 'border-zinc-500 bg-zinc-900' : 'border-zinc-300 bg-white'}`}></div>
                                    <span className="text-zinc-500 dark:text-zinc-400">Available</span>
                                </div>
                                <div className="flex items-center gap-2">
                                    <div className="w-3 h-3 rounded-full bg-[#1e40af] shadow-[0_0_5px_rgba(30,64,175,0.5)]"></div>
                                    <span className="text-zinc-500 dark:text-white">Selected</span>
                                </div>
                                <div className="flex items-center gap-2">
                                    <div className={`w-3 h-3 rounded-full ${isDark ? 'bg-zinc-800' : 'bg-zinc-200'}`}></div>
                                    <span className="text-zinc-500 dark:text-zinc-500">Booked</span>
                                </div>
                                <div className="flex items-center gap-2">
                                    <div className="w-3 h-3 rounded-full bg-[#1e40af]/20 border border-[#1e40af]/50"></div>
                                    <span className="text-zinc-500 dark:text-white">Your Booking</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Add-on Modal */}
            {showAddonModal && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
                    <div className={`w-full max-w-2xl rounded-3xl shadow-2xl border overflow-hidden max-h-[90vh] flex flex-col animate-fade-in ${isDark ? 'bg-brand-black border-zinc-800' : 'bg-white border-zinc-200'}`}>
                        <div className={`p-6 border-b flex justify-between items-center ${isDark ? 'border-zinc-800 bg-brand-black' : 'border-zinc-100 bg-zinc-50/50'}`}>
                            <h2 className={`text-2xl font-display font-bold ${isDark ? 'text-white' : 'text-gray-900'}`}>Enhance Your Game</h2>
                            <button onClick={() => setShowAddonModal(false)} className={`p-2 hover:bg-zinc-100 dark:hover:bg-zinc-800 rounded-full transition-colors ${isDark ? 'text-white' : 'text-gray-500'}`}>
                                <X size={24} />
                            </button>
                        </div>

                        <div className="p-8 overflow-y-auto flex-1">
                            {addonLoading ? (
                                <div className="flex flex-col items-center justify-center py-12">
                                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-brand-blue mb-4"></div>
                                    <span className="text-zinc-500">Checking availability...</span>
                                </div>
                            ) : (
                                <div className="space-y-10">
                                    {/* Equipment Section */}
                                    <div>
                                        <div className="flex items-center gap-3 mb-6">
                                            <div className="bg-brand-blue/10 p-2 rounded-lg text-brand-blue"><Dumbbell size={24} /></div>
                                            <h3 className={`text-xl font-bold ${isDark ? 'text-white' : 'text-gray-900'}`}>Equipment Rental</h3>
                                        </div>
                                        {availableEquipment.length === 0 ? (
                                            <div className="text-center p-8 rounded-2xl bg-zinc-50 dark:bg-zinc-900 border border-dashed border-zinc-200 dark:border-zinc-800">
                                                <p className="text-zinc-500 italic">No equipment available for this time.</p>
                                            </div>
                                        ) : (
                                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                                                {availableEquipment.map(item => (
                                                    <div key={item.id} className={`flex justify-between items-center p-5 rounded-2xl border transition-colors ${isDark ? 'bg-zinc-900 border-black' : 'bg-zinc-50 border-zinc-100'}`}>
                                                        <div>
                                                            <p className={`font-bold text-lg ${isDark ? 'text-white' : 'text-gray-900'}`}>{item.name}</p>
                                                            <p className="text-sm text-zinc-400 mb-2">{item.available_quantity} available</p>
                                                            <div className={`inline-block px-2 py-1 rounded text-xs font-bold ${isDark ? 'bg-zinc-800 text-zinc-300' : 'bg-gray-200 text-gray-700'}`}>₹{pricing.equipment.toFixed(2)}</div>
                                                        </div>
                                                        <div className="flex items-center gap-3">
                                                            <button
                                                                onClick={() => updateEquipment(item.id, -1, item.available_quantity)}
                                                                className={`w-10 h-10 flex items-center justify-center rounded-xl border hover:border-brand-blue transition-colors ${isDark ? 'bg-black border-zinc-800 text-white' : 'bg-white border-zinc-200 text-gray-700'}`}
                                                            >
                                                                <Minus size={16} />
                                                            </button>
                                                            <span className={`font-bold w-6 text-center text-lg ${isDark ? 'text-white' : 'text-gray-900'}`}>{selectedEquipment[item.id] || 0}</span>
                                                            <button
                                                                onClick={() => updateEquipment(item.id, 1, item.available_quantity)}
                                                                disabled={(selectedEquipment[item.id] || 0) >= item.available_quantity}
                                                                className={`w-10 h-10 flex items-center justify-center rounded-xl border hover:border-brand-blue text-brand-blue transition-colors disabled:opacity-50 disabled:cursor-not-allowed ${isDark ? 'bg-black border-zinc-800' : 'bg-white border-zinc-200'}`}
                                                            >
                                                                <Plus size={16} />
                                                            </button>
                                                        </div>
                                                    </div>
                                                ))}
                                            </div>
                                        )}
                                    </div>

                                    {/* Coach Section */}
                                    <div>
                                        <div className="flex items-center gap-3 mb-6">
                                            <div className="bg-brand-blue/10 p-2 rounded-lg text-brand-blue"><Users size={24} /></div>
                                            <h3 className={`text-xl font-bold ${isDark ? 'text-white' : 'text-gray-900'}`}>Professional Coaching</h3>
                                        </div>
                                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                                            <div
                                                onClick={() => setSelectedCoach(null)}
                                                className={`cursor-pointer p-5 rounded-2xl border transition-all ${selectedCoach === null ? 'border-brand-blue bg-brand-blue/10' : (isDark ? 'border-black bg-zinc-900 hover:border-zinc-700' : 'border-zinc-100 bg-zinc-50 hover:border-zinc-200')}`}
                                            >
                                                <p className={`font-bold text-lg ${isDark ? 'text-white' : 'text-gray-900'}`}>No Coach</p>
                                                <p className="text-sm text-zinc-400">I'll play independently</p>
                                            </div>
                                            {availableCoaches.map(coach => (
                                                <div
                                                    key={coach.id}
                                                    onClick={() => setSelectedCoach(coach.id)}
                                                    className={`cursor-pointer p-5 rounded-2xl border transition-all ${selectedCoach === coach.id ? 'border-brand-blue bg-brand-blue/10' : (isDark ? 'border-black bg-zinc-900 hover:border-zinc-700' : 'border-zinc-100 bg-zinc-50 hover:border-zinc-200')}`}
                                                >
                                                    <p className={`font-bold text-lg ${isDark ? 'text-white' : 'text-gray-900'}`}>{coach.name}</p>
                                                    <p className="text-sm text-zinc-400 mb-2">Professional Coach</p>
                                                    <div className="inline-block px-2 py-1 bg-brand-blue text-white rounded text-xs font-bold">₹{pricing.coach}/hr</div>
                                                </div>
                                            ))}
                                        </div>
                                    </div>


                                    {/* Price Breakdown Section */}
                                    <div className={`mt-8 p-6 rounded-2xl ${isDark ? 'bg-zinc-900 border border-zinc-800' : 'bg-zinc-50 border border-zinc-100'}`}>
                                        <h3 className={`text-xl font-bold mb-4 font-display ${isDark ? 'text-white' : 'text-gray-900'}`}>Bill Summary</h3>
                                        <div className="space-y-3">
                                            {/* Court Breakdown */}
                                            <div className="flex justify-between items-start">
                                                <div className="text-sm">
                                                    <p className={`font-medium ${isDark ? 'text-zinc-300' : 'text-zinc-700'}`}>Court Rental ({selectedSlots.length} hours)</p>
                                                    <div className="text-xs text-zinc-500 mt-1">
                                                        {selectedSlots.map(s => (
                                                            <span key={s.id} className="block">{s.time.substring(0, 5)} - {(parseInt(s.time.split(':')[0]) + 1).toString().padStart(2, '0')}:00 (₹{s.price})</span>
                                                        ))}
                                                    </div>
                                                </div>
                                                <span className={`font-medium ${isDark ? 'text-white' : 'text-gray-900'}`}>₹{selectedSlots.reduce((sum, s) => sum + s.price, 0)}</span>
                                            </div>

                                            {/* Equipment Breakdown */}
                                            {Object.entries(selectedEquipment).length > 0 && (
                                                <div className="flex justify-between items-start">
                                                    <div>
                                                        <p className={`text-sm font-medium ${isDark ? 'text-zinc-300' : 'text-zinc-700'}`}>Equipment</p>
                                                        <div className="text-xs text-zinc-500 mt-1">
                                                            {Object.entries(selectedEquipment).map(([id, qty]) => {
                                                                const item = availableEquipment.find(e => e.id === parseInt(id));
                                                                return item ? <span key={id} className="block">{qty}x {item.name} (@ ₹{pricing.equipment})</span> : null;
                                                            })}
                                                        </div>
                                                    </div>
                                                    <span className={`font-medium ${isDark ? 'text-white' : 'text-gray-900'}`}>
                                                        ₹{Object.entries(selectedEquipment).reduce((sum, [id, qty]) => sum + (qty * pricing.equipment), 0)}
                                                    </span>
                                                </div>
                                            )}

                                            {/* Coach Breakdown */}
                                            {selectedCoach && (
                                                <div className="flex justify-between items-center">
                                                    <div>
                                                        <p className={`text-sm font-medium ${isDark ? 'text-zinc-300' : 'text-zinc-700'}`}>Professional Coach</p>
                                                        <p className="text-xs text-zinc-500">{selectedSlots.length} hours @ ₹{pricing.coach}/hr</p>
                                                    </div>
                                                    <span className={`font-medium ${isDark ? 'text-white' : 'text-gray-900'}`}>
                                                        ₹{selectedSlots.length * pricing.coach}
                                                    </span>
                                                </div>
                                            )}

                                            <div className={`border-t my-3 ${isDark ? 'border-zinc-800' : 'border-zinc-200'}`}></div>

                                            {/* Total */}
                                            <div className="flex justify-between items-center">
                                                <span className={`text-lg font-bold ${isDark ? 'text-white' : 'text-gray-900'}`}>Grand Total</span>
                                                <span className="text-2xl font-bold text-brand-blue font-display">
                                                    ₹{
                                                        selectedSlots.reduce((sum, s) => sum + s.price, 0) +
                                                        Object.entries(selectedEquipment).reduce((sum, [_, qty]) => sum + (qty * pricing.equipment), 0) +
                                                        (selectedCoach ? selectedSlots.length * pricing.coach : 0)
                                                    }
                                                </span>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            )}
                        </div>

                        <div className={`p-6 border-t flex justify-end gap-3 ${isDark ? 'border-zinc-800 bg-brand-black' : 'border-zinc-100 bg-zinc-50/50'}`}>
                            <button
                                onClick={() => setShowAddonModal(false)}
                                className={`px-6 py-3 rounded-xl font-bold hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors ${isDark ? 'text-zinc-400' : 'text-zinc-500'}`}
                            >
                                Cancel
                            </button>
                            <button
                                onClick={confirmBooking}
                                className="px-8 py-3 rounded-xl font-bold bg-[#1e40af] text-white hover:opacity-90 shadow-lg shadow-blue-500/20 transition-all transform hover:scale-[1.02] active:scale-[0.98]"
                            >
                                Confirm & Pay
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
