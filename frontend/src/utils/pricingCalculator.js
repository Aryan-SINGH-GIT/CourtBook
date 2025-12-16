/**
 * Modular Pricing Calculator Utility
 * Calculates dynamic prices based on rules from the database
 */

/**
 * Calculate price for a given scenario
 * @param {number} basePrice - Base court price per hour
 * @param {object} rules - Pricing rules { peak: 10, weekend: 15, indoor: 5 }
 * @param {object} scenario - Scenario flags { isPeak: bool, isWeekend: bool, isIndoor: bool }
 * @returns {object} - { breakdown: string, total: number, details: array }
 */
export function calculatePrice(basePrice, rules, scenario) {
    let total = basePrice;
    const components = [];
    const breakdownParts = [`₹${basePrice} base`];

    if (scenario.isPeak && rules.peak) {
        const peakAmount = (basePrice * rules.peak) / 100;
        total += peakAmount;
        components.push({ label: `${rules.peak}% peak`, amount: peakAmount });
        breakdownParts.push(`₹${Math.round(peakAmount)} (${rules.peak}% peak)`);
    }

    if (scenario.isWeekend && rules.weekend) {
        const weekendAmount = (basePrice * rules.weekend) / 100;
        total += weekendAmount;
        components.push({ label: `${rules.weekend}% weekend`, amount: weekendAmount });
        breakdownParts.push(`₹${Math.round(weekendAmount)} (${rules.weekend}% weekend)`);
    }

    if (scenario.isIndoor && rules.indoor) {
        const indoorAmount = (basePrice * rules.indoor) / 100;
        total += indoorAmount;
        components.push({ label: `${rules.indoor}% indoor`, amount: indoorAmount });
        breakdownParts.push(`₹${Math.round(indoorAmount)} (${rules.indoor}% indoor)`);
    }

    return {
        breakdown: breakdownParts.join(' + ') + ` = ₹${Math.round(total)}`,
        total: Math.round(total),
        components
    };
}

/**
 * Generate example scenarios based on pricing config
 * @param {number} courtPrice - Base court price
 * @param {object} rules - { peak: number, weekend: number, indoor: number }
 * @returns {array} - Array of example objects
 */
export function generatePricingExamples(courtPrice, rules) {
    return [
        {
            scenario: 'Weekday Morning',
            details: 'Indoor court, 10 AM - 11 AM',
            ...calculatePrice(courtPrice, rules, { isPeak: false, isWeekend: false, isIndoor: true })
        },
        {
            scenario: 'Weekday Evening (Peak)',
            details: 'Indoor court, 7 PM - 8 PM',
            ...calculatePrice(courtPrice, rules, { isPeak: true, isWeekend: false, isIndoor: true })
        },
        {
            scenario: 'Weekend Morning',
            details: 'Indoor court + Weekend rate',
            ...calculatePrice(courtPrice, rules, { isPeak: false, isWeekend: true, isIndoor: true })
        },
        {
            scenario: 'Weekend Evening (Peak)',
            details: 'Indoor + Peak (7 PM) + Weekend',
            ...calculatePrice(courtPrice, rules, { isPeak: true, isWeekend: true, isIndoor: true })
        }
    ];
}
