import React, { useState } from 'react';
import InsightCard from './InsightCard';
import { FiTrendingUp, FiTrendingDown, FiActivity, FiUser, FiShoppingBag } from 'react-icons/fi';
import { motion } from 'framer-motion';
import './InsightCardDemo.css';

const InsightCardDemo = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [timeFilter, setTimeFilter] = useState('month');

  // Sample data for the cards
  const insightData = [
    {
      title: '긍정적 반응',
      value: timeFilter === 'month' ? '76' : '82',
      unit: '%',
      trend: timeFilter === 'month' ? '+12%' : '+16%',
      trendDirection: 'up',
      timeRange: timeFilter === 'month' ? '지난 30일 대비' : '지난 7일 대비',
      color: '#6366f1',
      icon: FiTrendingUp,
      chartData: timeFilter === 'month' 
        ? [
            { value: 40 }, { value: 45 }, { value: 50 }, { value: 55 }, 
            { value: 60 }, { value: 58 }, { value: 65 }, { value: 70 }, 
            { value: 68 }, { value: 72 }, { value: 75 }, { value: 76 }
          ]
        : [
            { value: 65 }, { value: 68 }, { value: 70 }, { value: 72 }, 
            { value: 75 }, { value: 78 }, { value: 80 }, { value: 82 }
          ]
    },
    {
      title: '부정적 반응',
      value: timeFilter === 'month' ? '15' : '12',
      unit: '%',
      trend: timeFilter === 'month' ? '-3%' : '-5%',
      trendDirection: 'down',
      timeRange: timeFilter === 'month' ? '지난 30일 대비' : '지난 7일 대비',
      color: '#ef4444',
      icon: FiTrendingDown,
      chartData: timeFilter === 'month'
        ? [
            { value: 25 }, { value: 22 }, { value: 20 }, { value: 18 }, 
            { value: 19 }, { value: 17 }, { value: 18 }, { value: 16 }, 
            { value: 17 }, { value: 16 }, { value: 14 }, { value: 15 }
          ]
        : [
            { value: 20 }, { value: 18 }, { value: 16 }, { value: 15 }, 
            { value: 14 }, { value: 13 }, { value: 12 }, { value: 12 }
          ]
    },
    {
      title: '중립적 반응',
      value: timeFilter === 'month' ? '9' : '6',
      unit: '%',
      trend: timeFilter === 'month' ? '-9%' : '-4%',
      trendDirection: 'down',
      timeRange: timeFilter === 'month' ? '지난 30일 대비' : '지난 7일 대비',
      color: '#0ea5e9',
      icon: FiActivity,
      chartData: timeFilter === 'month'
        ? [
            { value: 35 }, { value: 33 }, { value: 30 }, { value: 27 }, 
            { value: 25 }, { value: 22 }, { value: 20 }, { value: 18 }, 
            { value: 15 }, { value: 12 }, { value: 10 }, { value: 9 }
          ]
        : [
            { value: 15 }, { value: 13 }, { value: 12 }, { value: 10 }, 
            { value: 9 }, { value: 8 }, { value: 7 }, { value: 6 }
          ]
    },
    {
      title: '월간 방문자',
      value: timeFilter === 'month' ? '12,459' : '3,852',
      trend: timeFilter === 'month' ? '+5.2%' : '+2.8%',
      trendDirection: 'up',
      timeRange: timeFilter === 'month' ? '이번 달' : '이번 주',
      color: '#10b981',
      icon: FiUser,
      chartData: timeFilter === 'month'
        ? [
            { value: 9500 }, { value: 10000 }, { value: 10200 }, { value: 10500 }, 
            { value: 10800 }, { value: 11000 }, { value: 11200 }, { value: 11500 }, 
            { value: 11700 }, { value: 12000 }, { value: 12200 }, { value: 12459 }
          ]
        : [
            { value: 3500 }, { value: 3600 }, { value: 3650 }, { value: 3700 }, 
            { value: 3750 }, { value: 3780 }, { value: 3820 }, { value: 3852 }
          ]
    },
    {
      title: '인기 제품군',
      value: timeFilter === 'month' ? '디저트' : '아이스크림',
      trend: timeFilter === 'month' ? '+8%' : '+12%',
      trendDirection: 'up',
      timeRange: timeFilter === 'month' ? '지난 달 대비' : '지난 주 대비',
      color: '#f59e0b',
      icon: FiShoppingBag,
      chartData: timeFilter === 'month'
        ? [
            { value: 60 }, { value: 58 }, { value: 62 }, { value: 65 }, 
            { value: 70 }, { value: 68 }, { value: 72 }, { value: 75 }, 
            { value: 78 }, { value: 82 }, { value: 85 }, { value: 90 }
          ]
        : [
            { value: 70 }, { value: 75 }, { value: 78 }, { value: 82 }, 
            { value: 85 }, { value: 88 }, { value: 92 }, { value: 95 }
          ]
    }
  ];

  // Animation variants
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        when: "beforeChildren",
        staggerChildren: 0.1,
        delayChildren: 0.3
      }
    }
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: { type: "spring", stiffness: 80 }
    }
  };

  // Simulate data loading
  React.useEffect(() => {
    setIsLoading(true);
    const loadTimer = setTimeout(() => {
      setIsLoading(false);
    }, 800);
    
    return () => clearTimeout(loadTimer);
  }, [timeFilter]);

  return (
    <div className="insight-demo-container">
      <motion.div 
        initial={{ opacity: 0, y: -10 }} 
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="insight-header"
      >
        <h2 className="insight-demo-title">인사이트 요약</h2>
        <div className="insight-filters">
          <button 
            className={timeFilter === 'week' ? 'active' : ''} 
            onClick={() => setTimeFilter('week')}
          >
            주간
          </button>
          <button 
            className={timeFilter === 'month' ? 'active' : ''} 
            onClick={() => setTimeFilter('month')}
          >
            월간
          </button>
        </div>
      </motion.div>
      
      {isLoading ? (
        <motion.div 
          className="insight-loading"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
        >
          <div className="insight-loading-spinner"></div>
          <p>데이터 로딩 중...</p>
        </motion.div>
      ) : (
        <motion.div 
          className="insight-cards-grid"
          variants={containerVariants}
          initial="hidden"
          animate="visible"
          key={timeFilter} // This forces re-render on filter change
        >
          {insightData.map((data, index) => (
            <motion.div key={index} variants={itemVariants}>
              <InsightCard
                title={data.title}
                value={data.value}
                unit={data.unit}
                trend={data.trend}
                trendDirection={data.trendDirection}
                chartData={data.chartData}
                timeRange={data.timeRange}
                color={data.color}
                icon={data.icon}
              />
            </motion.div>
          ))}
        </motion.div>
      )}
    </div>
  );
};

export default InsightCardDemo; 