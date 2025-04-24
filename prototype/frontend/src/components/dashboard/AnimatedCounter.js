import React, { useState, useEffect } from 'react';
import { motion, useAnimationControls, useMotionValue, useTransform } from 'framer-motion';

/**
 * AnimatedCounter - A component that animates counting up to a target value
 * 
 * @param {Object} props
 * @param {string|number} props.value - The target value to count to
 * @param {string} props.unit - Optional unit to display after the value
 * @param {number} props.duration - Animation duration in seconds
 * @param {boolean} props.isPercentage - Whether the value is a percentage (affects formatting)
 */
const AnimatedCounter = ({ 
  value, 
  unit = '', 
  duration = 1.5, 
  isPercentage = false,
  className = '' 
}) => {
  const controls = useAnimationControls();
  const count = useMotionValue(0);
  const [targetValue, setTargetValue] = useState(0);
  const [displayValue, setDisplayValue] = useState('0');
  
  // Handle string values with commas, percentages, etc.
  useEffect(() => {
    let parsedValue;
    if (typeof value === 'string') {
      // Remove commas and other non-numeric characters except decimals
      parsedValue = parseFloat(value.replace(/[^\d.-]/g, ''));
    } else {
      parsedValue = value;
    }
    
    if (isNaN(parsedValue)) {
      setDisplayValue(value); // If not a number, just display as is
      return;
    }
    
    setTargetValue(parsedValue);
    
    // Animate from current value to target value
    controls.start({
      from: count.get(),
      to: parsedValue,
      duration: duration,
      onUpdate: latest => {
        count.set(latest);
        
        // Format the display value appropriately
        if (typeof value === 'string' && value.includes(',')) {
          // If original had commas for thousands
          setDisplayValue(latest.toLocaleString(undefined, { 
            maximumFractionDigits: 0 
          }));
        } else if (isPercentage) {
          setDisplayValue(latest.toFixed(1));
        } else if (Number.isInteger(parsedValue)) {
          setDisplayValue(Math.round(latest).toString());
        } else {
          setDisplayValue(latest.toFixed(1));
        }
      }
    });
    
  }, [value, controls, count, duration, isPercentage]);
  
  // For non-numeric values, just return as is
  if (isNaN(targetValue) && typeof value === 'string') {
    return (
      <span className={className}>
        {value}{unit}
      </span>
    );
  }
  
  return (
    <motion.span className={className}>
      {displayValue}
      {unit}
    </motion.span>
  );
};

export default AnimatedCounter; 