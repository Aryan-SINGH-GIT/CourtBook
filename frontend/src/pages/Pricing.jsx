import { useState, useEffect } from 'react';
import { Calendar, DollarSign, TrendingUp } from 'lucide-react';
import { useTheme } from '../context/ThemeContext';
import { pricingAPI } from '../services/api';
import { generatePricingExamples } from '../utils/pricingCalculator';

export default function Pricing() {
    const { isDark } = useTheme();
    const [loading, setLoading] = useState(true);
    const [config, setConfig] = useState({ base_prices: [], rules: [] });

    useEffect(() => {
        const fetchPricing = async () => {
            try {
                const response = await pricingAPI.getConfig();
                setConfig(response.data);
            } catch (error) {
                console.error('Failed to fetch pricing config:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchPricing();
    }, []);

    // Helper to map DB resource types to UI format
    const formatBasePrice = (bp) => {
        let label = '';
        let icon = Calendar;

        switch (bp.resource_type) {
            case 'COURT_HOUR':
                label = 'Court Rental';
                icon = Calendar;
                break;
            case 'EQUIPMENT_HOUR':
                label = 'Equipment Rental';
                icon = DollarSign;
                break;
            case 'COACH_HOUR':
                label = 'Coach Booking';
                icon = TrendingUp;
                break;
            default:
                label = bp.resource_type;
        }

        return {
            item: label,
            price: `₹${parseInt(bp.price)}/hour`,
            icon: icon
        };
    };

    // Helper to map DB rules to UI format
    const formatRule = (rule) => {
        let color = 'blue';
        let title = '';

        switch (rule.rule_type) {
            case 'PEAK_HOUR':
                color = 'rose';
                title = 'Peak Hours';
                break;
            case 'WEEKEND':
                color = 'amber';
                title = 'Weekend Rate';
                break;
            case 'INDOOR_COURT':
                color = 'emerald';
                title = 'Indoor Court';
                break;
            default:
                color = 'blue';
                title = rule.rule_type.replace('_', ' ');
        }

        return {
            rule: title,
            time: '', // Remove the description subtitle
            surcharge: rule.is_percentage ? `+${parseInt(rule.value)}%` : `+₹${rule.value}`,
            color: color
        };
    };

    const basePricesUI = config.base_prices.map(formatBasePrice);
    const rulesUI = config.rules.map(formatRule);

    // Extract pricing values for examples
    const courtPrice = config.base_prices.find(p => p.resource_type === 'COURT_HOUR')?.price || 200;
    const peakRule = config.rules.find(r => r.rule_type === 'PEAK_HOUR')?.value || 10;
    const weekendRule = config.rules.find(r => r.rule_type === 'WEEKEND')?.value || 15;
    const indoorRule = config.rules.find(r => r.rule_type === 'INDOOR_COURT')?.value || 5;

    // Generate dynamic examples
    const examples = generatePricingExamples(
        parseFloat(courtPrice),
        {
            peak: parseFloat(peakRule),
            weekend: parseFloat(weekendRule),
            indoor: parseFloat(indoorRule)
        }
    ).map(ex => ({
        scenario: ex.scenario,
        details: ex.details,
        calculation: ex.breakdown,
        total: `₹${ex.total}`
    }));

    if (loading) {
        return <div className={`min-h-screen flex items-center justify-center ${isDark ? 'bg-black text-white' : 'bg-white text-black'}`}>Loading prices...</div>;
    }

    return (
        <div className={`min-h-screen p-6 transition-colors duration-200 ${isDark ? 'bg-black text-white' : 'bg-white text-black'}`}>
            <h1 className="text-4xl font-display font-bold mb-2">Pricing</h1>
            <p className={`text-lg mb-8 ${isDark ? 'text-zinc-400' : 'text-zinc-600'}`}>
                Simple, transparent pricing with no hidden fees.
            </p>

            {/* Base Prices */}
            <div className={`${isDark ? 'bg-black' : 'bg-white'} rounded-xl p-6 border ${isDark ? 'border-zinc-800' : 'border-gray-200'} mb-6`}>
                <h2 className={`text-xl font-bold mb-4 ${isDark ? 'text-white' : 'text-gray-900'}`}>
                    Base Prices
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {basePricesUI.map((item, index) => (
                        <div
                            key={index}
                            className={`p-4 rounded-lg border ${isDark ? 'border-zinc-800 bg-zinc-900' : 'border-gray-200 bg-gray-50'}`}
                        >
                            <item.icon className={`${isDark ? 'text-white' : 'text-gray-900'} mb-2`} size={32} />
                            <h3 className={`font-semibold ${isDark ? 'text-white' : 'text-gray-900'}`}>
                                {item.item}
                            </h3>
                            <p className="text-2xl font-bold mt-2 text-brand-blue">{item.price}</p>
                        </div>
                    ))}
                </div>
            </div>

            {/* Pricing Rules */}
            <div className={`${isDark ? 'bg-black' : 'bg-white'} rounded-xl p-6 border ${isDark ? 'border-zinc-800' : 'border-gray-200'} mb-6`}>
                <h2 className={`text-xl font-bold mb-4 ${isDark ? 'text-white' : 'text-gray-900'}`}>
                    Surcharges & Rules
                </h2>
                <div className="space-y-4">
                    {rulesUI.map((rule, index) => (
                        <div
                            key={index}
                            className={`flex items-center justify-between p-4 rounded-lg ${isDark ? 'bg-zinc-900/50' : 'bg-gray-50'}`}
                        >
                            <div className="flex items-center gap-3">
                                <div className={`w-3 h-3 rounded-full bg-brand-blue`}></div>
                                <div>
                                    <h3 className={`font-semibold ${isDark ? 'text-white' : 'text-gray-900'}`}>
                                        {rule.rule}
                                    </h3>
                                    <p className="text-sm text-gray-500">{rule.time}</p>
                                </div>
                            </div>
                            <span className="text-lg font-bold text-brand-blue">{rule.surcharge}</span>
                        </div>
                    ))}
                </div>

                <div className={`mt-4 p-4 rounded-lg ${isDark ? 'bg-zinc-900 border border-zinc-800' : 'bg-blue-50 border border-blue-200'}`}>
                    <p className={`text-sm ${isDark ? 'text-zinc-400' : 'text-blue-700'}`}>
                        <strong>Note:</strong> Rules stack additively. For example, if both peak hour and weekend apply, you'll pay base + 20% + 15% = base + 35%.
                    </p>
                </div>
            </div>

            {/* Examples (Static for now, but helpful context) */}
            <div className={`${isDark ? 'bg-black' : 'bg-white'} rounded-xl p-6 border ${isDark ? 'border-zinc-800' : 'border-gray-200'}`}>
                <h2 className={`text-xl font-bold mb-4 ${isDark ? 'text-white' : 'text-gray-900'}`}>
                    Pricing Examples
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {examples.map((example, index) => (
                        <div
                            key={index}
                            className={`p-4 rounded-lg border ${isDark ? 'border-zinc-800 bg-zinc-900/30' : 'border-gray-200 bg-white'}`}
                        >
                            <div className="flex justify-between items-start mb-2">
                                <h3 className={`font-semibold ${isDark ? 'text-white' : 'text-gray-900'}`}>{example.scenario}</h3>
                                <span className={`text-xs px-2 py-1 rounded-full ${isDark ? 'bg-zinc-800 text-zinc-400' : 'bg-gray-100 text-gray-600'}`}>Example</span>
                            </div>
                            <p className="text-sm text-gray-500 mb-2">{example.details}</p>
                            <p className={`text-sm mb-2 ${isDark ? 'text-gray-300' : 'text-gray-700'}`}>
                                {example.calculation}
                            </p>
                            <div className={`pt-3 border-t ${isDark ? 'border-zinc-800' : 'border-gray-300'} flex justify-between items-center`}>
                                <span className="font-semibold">Total:</span>
                                <span className="text-xl font-bold text-brand-blue">{example.total}</span>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
