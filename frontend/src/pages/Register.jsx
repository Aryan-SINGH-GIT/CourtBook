import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { User, Mail, Lock, UserPlus } from 'lucide-react';

export default function Register() {
    const navigate = useNavigate();
    const { register } = useAuth();
    const [formData, setFormData] = useState({
        username: '',
        email: '',
        password: '',
        password2: '',
        first_name: '',
        last_name: '',
    });
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        if (formData.password !== formData.password2) {
            setError('Passwords do not match');
            return;
        }

        setLoading(true);
        const result = await register(formData);
        setLoading(false);

        if (result.success) {
            navigate('/login', { state: { message: 'Registration successful! Please login.' } });
        } else {
            setError(typeof result.error === 'string' ? result.error : JSON.stringify(result.error));
        }
    };

    return (
        <div className="min-h-screen bg-black flex items-center justify-center p-4">
            <div className="max-w-md w-full">
                <div className="text-center mb-8">
                    <h2 className="text-4xl font-bold text-white mb-2">Create Account</h2>
                    <p className="text-gray-400">Join us to start booking courts</p>
                </div>

                <div className="bg-zinc-900 rounded-2xl shadow-2xl p-8 border border-zinc-800">
                    <form onSubmit={handleSubmit} className="space-y-4">
                        {error && (
                            <div className="bg-red-500/10 border border-red-500/50 text-red-400 px-4 py-3 rounded-lg">
                                {error}
                            </div>
                        )}

                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-300 mb-2">First Name</label>
                                <div className="relative">
                                    <User className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
                                    <input
                                        type="text"
                                        name="first_name"
                                        required
                                        value={formData.first_name}
                                        onChange={handleChange}
                                        className="w-full pl-10 pr-4 py-3 bg-black border border-zinc-700 rounded-lg text-white placeholder-zinc-500 focus:border-brand-blue focus:ring-2 focus:ring-brand-blue/20 transition"
                                        placeholder="John"
                                    />
                                </div>
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-300 mb-2">Last Name</label>
                                <div className="relative">
                                    <User className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
                                    <input
                                        type="text"
                                        name="last_name"
                                        required
                                        value={formData.last_name}
                                        onChange={handleChange}
                                        className="w-full pl-10 pr-4 py-3 bg-black border border-zinc-700 rounded-lg text-white placeholder-zinc-500 focus:border-brand-blue focus:ring-2 focus:ring-brand-blue/20 transition"
                                        placeholder="Doe"
                                    />
                                </div>
                            </div>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-300 mb-2">Username</label>
                            <div className="relative">
                                <UserPlus className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
                                <input
                                    type="text"
                                    name="username"
                                    required
                                    value={formData.username}
                                    onChange={handleChange}
                                    className="w-full pl-10 pr-4 py-3 bg-black border border-zinc-700 rounded-lg text-white placeholder-zinc-500 focus:border-brand-blue focus:ring-2 focus:ring-brand-blue/20 transition"
                                    placeholder="johndoe"
                                />
                            </div>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-300 mb-2">Email</label>
                            <div className="relative">
                                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
                                <input
                                    type="email"
                                    name="email"
                                    required
                                    value={formData.email}
                                    onChange={handleChange}
                                    className="w-full pl-10 pr-4 py-3 bg-black border border-zinc-700 rounded-lg text-white placeholder-zinc-500 focus:border-brand-blue focus:ring-2 focus:ring-brand-blue/20 transition"
                                    placeholder="john@example.com"
                                />
                            </div>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-300 mb-2">Password</label>
                            <div className="relative">
                                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
                                <input
                                    type="password"
                                    name="password"
                                    required
                                    value={formData.password}
                                    onChange={handleChange}
                                    className="w-full pl-10 pr-4 py-3 bg-black border border-zinc-700 rounded-lg text-white placeholder-zinc-500 focus:border-brand-blue focus:ring-2 focus:ring-brand-blue/20 transition"
                                    placeholder="••••••••"
                                />
                            </div>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-300 mb-2">Confirm Password</label>
                            <div className="relative">
                                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
                                <input
                                    type="password"
                                    name="password2"
                                    required
                                    value={formData.password2}
                                    onChange={handleChange}
                                    className="w-full pl-10 pr-4 py-3 bg-black border border-zinc-700 rounded-lg text-white placeholder-zinc-500 focus:border-brand-blue focus:ring-2 focus:ring-brand-blue/20 transition"
                                    placeholder="••••••••"
                                />
                            </div>
                        </div>

                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full py-3 bg-brand-blue text-white rounded-lg font-bold hover:opacity-90 transition transform hover:scale-[1.02] disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
                        >
                            {loading ? 'Creating Account...' : 'Create Account'}
                        </button>
                    </form>

                    <p className="mt-6 text-center text-gray-400">
                        Already have an account?{' '}
                        <Link to="/login" className="text-brand-blue hover:text-blue-400 font-bold transition">
                            Login here
                        </Link>
                    </p>
                </div>
            </div>
        </div>
    );
}
