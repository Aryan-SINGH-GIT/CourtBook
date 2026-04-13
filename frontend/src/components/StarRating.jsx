import React, { useState } from 'react';

const StarRating = ({ rating, setRating, readOnly = false }) => {
  const [hover, setHover] = useState(0);

  return (
    <div className="flex items-center">
      {[...Array(5)].map((_, index) => {
        const ratingValue = index + 1;

        return (
          <button
            type="button"
            key={ratingValue}
            className={`text-2xl focus:outline-none transition-colors duration-150 ${readOnly ? 'cursor-default' : 'cursor-pointer'
              } ${ratingValue <= (hover || rating) ? 'text-yellow-400' : 'text-gray-300'
              }`}
            onClick={() => {
              if (!readOnly && setRating) {
                setRating(ratingValue);
              }
            }}
            onMouseEnter={() => {
              if (!readOnly) {
                setHover(ratingValue);
              }
            }}
            onMouseLeave={() => {
              if (!readOnly) {
                setHover(0);
              }
            }}
            disabled={readOnly}
          >
            ★
          </button>
        );
      })}
    </div>
  );
};

export default StarRating;
