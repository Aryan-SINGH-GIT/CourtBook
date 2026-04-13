import React, { useState } from 'react';
import StarRating from './StarRating';
import api from '../services/api';
import { useTheme } from '../context/ThemeContext';
import { X } from 'lucide-react';

const ReviewModal = ({ booking, isOpen, onClose, onReviewSubmitted }) => {
  const { isDark } = useTheme();
  const [rating, setRating] = useState(5);
  const [comment, setComment] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      await api.post('/reviews/', {
        booking: booking.id,
        rating,
        comment
      });
      onReviewSubmitted();
      onClose();
    } catch (err) {
      console.error('Review submission error:', err);
      // Try to extract readable error message from Django DRF response
      let errorMessage = 'Failed to submit review';
      if (err.response?.data) {
        if (typeof err.response.data === 'object') {
          // Join all errors
          errorMessage = Object.entries(err.response.data)
            .map(([key, val]) => `${key}: ${val}`)
            .join(', ');
        } else {
          errorMessage = err.response.data;
        }
      } else if (err.message) {
        errorMessage = err.message;
      }
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className={`rounded-3xl shadow-2xl p-6 w-full max-w-md relative animate-fade-in border ${isDark ? 'bg-black border-zinc-800 text-white' : 'bg-white border-zinc-200 text-gray-900'
        }`}>

        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-display font-bold">Rate Experience</h2>
          <button
            onClick={onClose}
            className={`p-2 rounded-full transition-colors ${isDark ? 'hover:bg-zinc-800 text-zinc-400' : 'hover:bg-gray-100 text-gray-500'
              }`}
          >
            <X size={20} />
          </button>
        </div>

        {error && (
          <div className="bg-red-500/10 border border-red-500/50 text-red-500 px-4 py-3 rounded-xl mb-6 text-sm flex items-center gap-2">
            <span>!</span> {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="mb-6 text-center">
            <label className={`block text-sm font-bold mb-3 ${isDark ? 'text-zinc-400' : 'text-gray-600'}`}>
              How was your session?
            </label>
            <div className="flex justify-center">
              <StarRating rating={rating} setRating={setRating} />
            </div>
          </div>

          <div className="mb-6">
            <label className={`block text-sm font-bold mb-2 ${isDark ? 'text-zinc-400' : 'text-gray-600'}`}>
              Feedback (Optional)
            </label>
            <textarea
              className={`w-full p-4 rounded-xl border outline-none transition-all placeholder:text-zinc-500 min-h-[120px] resize-none ${isDark
                ? 'bg-zinc-900 border-zinc-800 focus:border-brand-blue text-white'
                : 'bg-gray-50 border-gray-200 focus:border-brand-blue text-gray-900'
                }`}
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              placeholder="Tell us about the court quality or coach..."
            />
          </div>

          <div className="flex gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              className={`flex-1 py-3 rounded-xl font-bold transition-colors ${isDark
                ? 'bg-zinc-900 text-zinc-400 hover:bg-zinc-800'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              disabled={loading}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="flex-1 py-3 bg-[#1e40af] hover:bg-blue-700 text-white font-bold rounded-xl shadow-lg shadow-blue-500/20 transition-all transform hover:scale-[1.02] active:scale-[0.98]"
              disabled={loading}
            >
              {loading ? 'Submitting...' : 'Submit Review'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ReviewModal;
