import React from 'react';
import { ResponsiveContainer, LineChart, Line, YAxis } from 'recharts';
import { motion } from 'framer-motion';
import AnimatedCounter from './AnimatedCounter';
import './InsightCard.css';

/**
 * InsightCard - A minimal glassmorphism card displaying a key insight with sparkline
 * 
 * @param {Object} props
 * @param {string} props.title - Card title
 * @param {string} props.value - Main metric value
 * @param {string} props.unit - Unit for the value (optional)
 * @param {string} props.trend - Trend indicator (+12%, -5%, etc)
 * @param {string} props.trendDirection - 'up' or 'down'
 * @param {Array} props.chartData - Array of data points for sparkline
 * @param {string} props.timeRange - Time range description
 * @param {string} props.color - Accent color (default: #6366f1)
 * @param {string} props.icon - Icon component to display
 */
const InsightCard = ({
  title,
  value,
  unit = '',
  trend,
  trendDirection,
  chartData = [],
  timeRange,
  color = '#6366f1',
  icon: Icon
}) => {
  // Default data if none provided
  const data = chartData.length > 0 ? chartData : [
    { value: 30 }, { value: 40 }, { value: 35 }, { value: 50 }, 
    { value: 43 }, { value: 65 }, { value: 58 }, { value: 70 }, 
    { value: 72 }, { value: 60 }, { value: 55 }, { value: 80 }
  ];

  return (
    <motion.div 
      className="insight-card" 
      style={{ '--card-accent-color': color }}
      whileHover={{ 
        y: -8,
        boxShadow: '0 14px 28px rgba(0, 0, 0, 0.15)',
        transition: { type: "spring", stiffness: 400, damping: 10 }
      }}
    >
      <motion.div 
        className="insight-card-content"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.6 }}
      >
        <motion.div 
          className="insight-card-header"
          initial={{ x: -20, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ delay: 0.1, duration: 0.4 }}
        >
          {Icon && (
            <motion.div 
              className="insight-card-icon"
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ 
                type: "spring", 
                stiffness: 260, 
                damping: 20, 
                delay: 0.2 
              }}
            >
              <Icon />
            </motion.div>
          )}
          <h3 className="insight-card-title">{title}</h3>
        </motion.div>
        
        <motion.div 
          className="insight-card-metric"
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.2, duration: 0.4 }}
        >
          <motion.div 
            className="insight-card-value"
            initial={{ scale: 0.9 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.3, duration: 0.3 }}
          >
            <AnimatedCounter 
              value={value} 
              unit={unit}
              isPercentage={unit === '%'}
            />
          </motion.div>
          
          {trend && (
            <motion.div 
              className={`insight-card-trend ${trendDirection}`}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4, duration: 0.3 }}
            >
              {trend}
            </motion.div>
          )}
        </motion.div>
        
        <motion.div 
          className="insight-card-chart"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5, duration: 0.6 }}
        >
          <ResponsiveContainer width="100%" height={40}>
            <LineChart data={data}>
              <YAxis domain={['dataMin', 'dataMax']} hide />
              <Line 
                type="monotone" 
                dataKey="value" 
                stroke={color} 
                strokeWidth={2} 
                dot={false} 
                isAnimationActive={true}
                animationDuration={1500}
              />
            </LineChart>
          </ResponsiveContainer>
        </motion.div>
        
        {timeRange && (
          <motion.div 
            className="insight-card-footer"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.6, duration: 0.3 }}
          >
            <span className="insight-card-timerange">{timeRange}</span>
          </motion.div>
        )}
      </motion.div>
    </motion.div>
  );
};

export default InsightCard; 