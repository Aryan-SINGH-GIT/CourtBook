import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Calendar, DollarSign, Users, Shield, ArrowRight } from 'lucide-react';
import badmintonBg from '../assets/Gemini_Generated_Image_404ew6404ew6404e.png';
import courtImg from '../assets/court.png';
import equipImg from '../assets/equip.png';
import { resourcesAPI } from '../services/api';

export default function Landing() {
    const [coaches, setCoaches] = useState([]);
    const [loading, setLoading] = useState(true);

    // Coach specialty/bio mapping based on name
    const coachDetailsMap = {
        'Rajesh Sharma': {
            specialty: 'Head Coach - Singles Specialist',
            bio: '15+ years of experience. Former national player specializing in advanced singles techniques and footwork training.',
            initials: 'RS'
        },
        'Priya Kumar': {
            specialty: 'Senior Coach - Doubles Expert',
            bio: '12+ years coaching experience. Specializes in doubles strategy, coordination, and competitive tournament preparation.',
            initials: 'PK'
        },
        'Amit Mehta': {
            specialty: 'Youth Coach - Beginners',
            bio: '8+ years experience. Patient and encouraging approach perfect for beginners and young players learning the fundamentals.',
            initials: 'AM'
        }
    };

    // Default fallback coaches
    const defaultCoaches = [
        { id: 1, name: 'Rajesh Sharma' },
        { id: 2, name: 'Priya Kumar' },
        { id: 3, name: 'Amit Mehta' }
    ];

    useEffect(() => {
        const fetchCoaches = async () => {
            try {
                const response = await resourcesAPI.getCoaches();
                // Ensure response.data is an array
                const coachData = Array.isArray(response.data) ? response.data : defaultCoaches;
                setCoaches(coachData);
            } catch (error) {
                console.error('Failed to fetch coaches:', error);
                // Use default coaches if API fails
                setCoaches(defaultCoaches);
            } finally {
                setLoading(false);
            }
        };

        fetchCoaches();
    }, []);

    const features = [
        {
            icon: Calendar,
            title: 'Easy Booking',
            description: 'Book courts, equipment, and coaches in just a few clicks',
        },
        {
            icon: DollarSign,
            title: 'Dynamic Pricing',
            description: 'Transparent pricing with peak hour and weekend rates',
        },
        {
            icon: Users,
            title: 'Coach Availability',
            description: 'Book professional coaches based on their availability',
        },
        {
            icon: Shield,
            title: 'Secure & Reliable',
            description: 'Your bookings are protected with atomic transactions',
        },
    ];

    return (
        <div className="min-h-screen">
            {/* Hero Section */}
            <div className="relative h-screen">
                {/* Background Image with Overlay */}
                <div className="absolute inset-0">
                    <img
                        src={badmintonBg}
                        alt="Badminton Court"
                        className="w-full h-full object-cover"
                    />
                    <div className="absolute inset-0 bg-black/80"></div>
                </div>

                {/* Content */}
                <div className="relative z-10 h-full flex flex-col items-center justify-center px-4 text-center">
                    <h1 className="text-6xl md:text-8xl font-extrabold text-white mb-8 animate-fade-in drop-shadow-xl tracking-tight">
                        Badminton Court
                        <span className="block mt-2 text-white/90 font-cursive">
                            Booking System
                        </span>
                    </h1>

                    <p className="text-2xl md:text-3xl text-gray-200 mb-12 max-w-3xl mx-auto font-light animate-fade-in-delay drop-shadow-md">
                        The professional way to book courts, equipment, and coaches.
                        <span className="block mt-2 font-normal">Play more, worry less.</span>
                    </p>

                    <Link
                        to="/login"
                        className="group px-10 py-5 bg-brand-blue text-white rounded-full font-bold text-xl hover:bg-blue-600 transition-all transform hover:scale-105 shadow-xl flex items-center gap-3 animate-fade-in-delay-2"
                    >
                        Get Started
                        <ArrowRight className="group-hover:translate-x-1 transition-transform" size={24} />
                    </Link>
                </div>

                {/* Scroll Indicator */}
                <div className="absolute bottom-10 left-1/2 -translate-x-1/2 animate-bounce">
                    <div className="w-8 h-12 border-2 border-white/30 rounded-full flex items-start justify-center p-2 backdrop-blur-sm">
                        <div className="w-1.5 h-3 bg-white rounded-full animate-scroll"></div>
                    </div>
                </div>
            </div>

            {/* Courts Section */}
            <div className="relative py-24 bg-black">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="grid md:grid-cols-2 gap-12 items-center">
                        {/* Description - Left */}
                        <div className="space-y-6">
                            <h2 className="text-5xl font-bold text-white">
                                Our Premium Courts
                            </h2>
                            <p className="text-xl text-gray-300 leading-relaxed">
                                We have <span className="text-brand-blue font-semibold">4 premium courts</span> - both indoor and outdoor facilities with professional-grade flooring and lighting for the best gaming experience.
                            </p>
                            <p className="text-lg text-gray-400 leading-relaxed">
                                Whether you prefer the controlled environment of our indoor courts or the fresh air of outdoor play, each court is meticulously maintained to international standards. Perfect lighting ensures optimal visibility during evening sessions, while our cushioned flooring reduces strain and prevents injuries.
                            </p>
                            <Link
                                to="/login"
                                className="inline-flex items-center gap-2 px-8 py-4 bg-brand-blue text-white rounded-lg font-semibold hover:bg-blue-600 transition-all transform hover:scale-105"
                            >
                                Book a Court
                                <ArrowRight size={20} />
                            </Link>
                        </div>

                        {/* Image - Right */}
                        <div className="relative">
                            <div className="relative rounded-2xl overflow-hidden shadow-2xl border-4 border-zinc-800 hover:border-brand-blue transition-all duration-300 transform hover:scale-105">
                                <img
                                    src={courtImg}
                                    alt="Our Premium Badminton Courts"
                                    className="w-full h-auto"
                                />
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Equipment Section */}
            <div className="relative py-24 bg-black border-t border-zinc-900">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="grid md:grid-cols-2 gap-12 items-center">
                        {/* Image - Left */}
                        <div className="relative order-2 md:order-1">
                            <div className="relative rounded-2xl overflow-hidden shadow-2xl border-4 border-zinc-800 hover:border-brand-blue transition-all duration-300 transform hover:scale-105">
                                <img
                                    src={equipImg}
                                    alt="Quality Badminton Equipment"
                                    className="w-full h-auto"
                                />
                            </div>
                        </div>

                        {/* Description - Right */}
                        <div className="space-y-6 order-1 md:order-2">
                            <h2 className="text-5xl font-bold text-white">
                                Quality Equipment
                            </h2>
                            <p className="text-xl text-gray-300 leading-relaxed">
                                Quality equipment including <span className="text-brand-blue font-semibold">premium badminton shuttlecocks</span>, professional rackets, and specialized court shoes available for rent.
                            </p>
                            <p className="text-lg text-gray-400 leading-relaxed">
                                All our equipment is regularly maintained and replaced to ensure peak performance. From tournament-grade feather shuttlecocks to high-tension rackets and non-marking court shoes - we've got everything you need to play your best game.
                            </p>
                            <div className="flex flex-wrap gap-4 pt-4">
                                <div className="bg-zinc-900 px-6 py-3 rounded-lg border border-zinc-800">
                                    <p className="text-white font-semibold">🏸 Shuttlecocks</p>
                                </div>
                                <div className="bg-zinc-900 px-6 py-3 rounded-lg border border-zinc-800">
                                    <p className="text-white font-semibold">🎾 Rackets</p>
                                </div>
                                <div className="bg-zinc-900 px-6 py-3 rounded-lg border border-zinc-800">
                                    <p className="text-white font-semibold">👟 Court Shoes</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Coaches Section */}
            <div className="relative py-24 bg-black border-t border-zinc-900">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="text-center mb-16">
                        <h2 className="text-5xl font-bold text-white mb-6">
                            Our Expert Coaches
                        </h2>
                        <p className="text-xl text-gray-300 max-w-3xl mx-auto">
                            Learn from the best with our team of certified professional coaches
                        </p>
                    </div>

                    <div className="grid md:grid-cols-3 gap-8">
                        {loading ? (
                            <div className="col-span-3 text-center text-gray-400">
                                Loading coaches...
                            </div>
                        ) : (
                            coaches.map((coach) => {
                                const details = coachDetailsMap[coach.name] || {
                                    specialty: 'Professional Coach',
                                    bio: 'Experienced badminton coach dedicated to helping players improve their game.',
                                    initials: coach.name.split(' ').map(n => n[0]).join('')
                                };

                                return (
                                    <div key={coach.id} className="bg-zinc-900/50 backdrop-blur-md rounded-2xl p-8 border border-zinc-800 hover:border-brand-blue transition-all duration-300 hover:-translate-y-2 group">
                                        <div className="w-24 h-24 bg-gradient-to-br from-brand-blue to-blue-600 rounded-full mx-auto mb-6 flex items-center justify-center text-white text-4xl font-bold">
                                            {details.initials}
                                        </div>
                                        <h3 className="text-2xl font-bold text-white mb-3 text-center">
                                            {coach.name}
                                        </h3>
                                        <p className="text-brand-blue font-semibold text-center mb-4">
                                            {details.specialty}
                                        </p>
                                        <p className="text-gray-400 text-center leading-relaxed">
                                            {details.bio}
                                        </p>
                                    </div>
                                );
                            })
                        )}
                    </div>
                </div>
            </div>

            {/* Footer */}
            <footer className="bg-black py-12 px-4 border-t border-zinc-800">
                <div className="max-w-6xl mx-auto text-center">
                    <p className="text-zinc-500 text-lg mb-4">
                        &copy; 2025 CourtBook System. All rights reserved.
                    </p>
                    <p className="text-zinc-600 text-sm">
                        Your professional badminton court booking solution
                    </p>
                </div>
            </footer>
        </div>
    );
}
