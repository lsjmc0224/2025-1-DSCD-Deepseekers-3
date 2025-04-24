import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend
} from 'recharts';

/**
 * 애플/스포티파이 스타일 감성 분석 시각화 컴포넌트
 * 
 * 선형 그라디언트와 미니멀한 디자인을 적용한 시간별 감성 분석 트렌드 차트
 */
const SentimentTrendChart = ({ 
  data = [], 
  timeRange = '1w',
  height = 400,
  withLegend = true,
  withTooltip = true,
  withGrid = true 
}) => {
  const [chartData, setChartData] = useState([]);
  const [activeType, setActiveType] = useState('all');

  useEffect(() => {
    if (data && data.length > 0) {
      setChartData(data);
    } else {
      // 예시 데이터 설정
      const sampleData = generateSampleData(timeRange);
      setChartData(sampleData);
    }
  }, [data, timeRange]);

  // 범례 클릭 이벤트 핸들러
  const handleLegendClick = (entry) => {
    setActiveType(activeType === entry.value ? 'all' : entry.value);
  };

  // 툴팁 커스텀 렌더러
  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      const positiveValue = payload[0].value.toFixed(2);
      const neutralValue = payload[1].value.toFixed(2);
      const negativeValue = payload[2].value.toFixed(2);
      
      return (
        <div className="custom-tooltip">
          <p className="tooltip-date">{label}</p>
          <div className="tooltip-item positive">
            <span className="tooltip-dot">●</span>
            <span className="tooltip-label">긍정: </span>
            <span className="tooltip-value">{positiveValue}</span>
          </div>
          <div className="tooltip-item neutral">
            <span className="tooltip-dot">●</span>
            <span className="tooltip-label">중립: </span>
            <span className="tooltip-value">{neutralValue}</span>
          </div>
          <div className="tooltip-item negative">
            <span className="tooltip-dot">●</span>
            <span className="tooltip-label">부정: </span>
            <span className="tooltip-value">{negativeValue}</span>
          </div>
        </div>
      );
    }
    return null;
  };

  // 날짜 형식 포맷터
  const formatXAxis = (tickItem) => {
    if (!tickItem) return '';
    
    // 시간 범위에 따라 다른 포맷 적용
    if (timeRange === '1d') {
      return tickItem.substring(11, 16); // HH:MM 형식
    } else if (timeRange === '1w') {
      return tickItem.substring(5, 10); // MM-DD 형식
    } else {
      return tickItem.substring(5, 10); // MM-DD 형식
    }
  };

  return (
    <div className="sentiment-trend-chart">
      <div className="chart-header">
        <h3>감성 트렌드 분석</h3>
        <div className="time-selector">
          <button className={timeRange === '1d' ? 'active' : ''} onClick={() => {}}>오늘</button>
          <button className={timeRange === '1w' ? 'active' : ''} onClick={() => {}}>주간</button>
          <button className={timeRange === '1m' ? 'active' : ''} onClick={() => {}}>월간</button>
        </div>
      </div>
      
      <ResponsiveContainer width="100%" height={height}>
        <AreaChart
          data={chartData}
          margin={{ top: 20, right: 30, left: 0, bottom: 20 }}
        >
          <defs>
            <linearGradient id="positiveGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#1DB954" stopOpacity={0.8} />
              <stop offset="95%" stopColor="#1DB954" stopOpacity={0.1} />
            </linearGradient>
            <linearGradient id="neutralGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#007AFF" stopOpacity={0.8} />
              <stop offset="95%" stopColor="#007AFF" stopOpacity={0.1} />
            </linearGradient>
            <linearGradient id="negativeGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#FF453A" stopOpacity={0.8} />
              <stop offset="95%" stopColor="#FF453A" stopOpacity={0.1} />
            </linearGradient>
          </defs>
          
          {withGrid && <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255, 255, 255, 0.1)" />}
          
          <XAxis 
            dataKey="date" 
            tickLine={false}
            axisLine={false}
            tickFormatter={formatXAxis}
            tick={{ fill: 'var(--text-secondary)' }}
            dy={10}
          />
          
          <YAxis 
            tickLine={false}
            axisLine={false}
            tick={{ fill: 'var(--text-secondary)' }}
            domain={[0, 1]}
            dx={-10}
          />
          
          {withTooltip && <Tooltip content={<CustomTooltip />} />}
          
          {withLegend && (
            <Legend 
              onClick={handleLegendClick} 
              iconType="circle"
              wrapperStyle={{ paddingTop: '20px' }}
            />
          )}
          
          <Area 
            type="monotone" 
            dataKey="positive" 
            name="긍정"
            stroke="#1DB954" 
            fill="url(#positiveGradient)" 
            strokeWidth={2}
            activeDot={{ r: 6 }}
            hide={activeType !== 'all' && activeType !== 'positive'}
          />
          
          <Area 
            type="monotone" 
            dataKey="neutral" 
            name="중립"
            stroke="#007AFF" 
            fill="url(#neutralGradient)" 
            strokeWidth={2}
            activeDot={{ r: 6 }}
            hide={activeType !== 'all' && activeType !== 'neutral'}
          />
          
          <Area 
            type="monotone" 
            dataKey="negative" 
            name="부정"
            stroke="#FF453A" 
            fill="url(#negativeGradient)" 
            strokeWidth={2}
            activeDot={{ r: 6 }}
            hide={activeType !== 'all' && activeType !== 'negative'}
          />
        </AreaChart>
      </ResponsiveContainer>
      
      <style jsx>{`
        .sentiment-trend-chart {
          background-color: var(--surface-color);
          border-radius: 12px;
          padding: 20px;
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }
        
        .chart-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 20px;
        }
        
        .chart-header h3 {
          font-size: 18px;
          font-weight: 600;
          color: var(--text-primary);
          margin: 0;
        }
        
        .time-selector {
          display: flex;
          gap: 10px;
        }
        
        .time-selector button {
          background: none;
          border: none;
          color: var(--text-secondary);
          padding: 6px 12px;
          border-radius: 20px;
          font-size: 14px;
          transition: all 0.2s;
        }
        
        .time-selector button:hover {
          background-color: rgba(255, 255, 255, 0.1);
          color: var(--text-primary);
        }
        
        .time-selector button.active {
          background-color: var(--primary-light-color);
          color: var(--primary-color);
        }
        
        .custom-tooltip {
          background-color: var(--surface-color);
          border-radius: 8px;
          padding: 12px;
          box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
          border: 1px solid var(--border-color);
        }
        
        .tooltip-date {
          font-weight: 600;
          margin-bottom: 10px;
          color: var(--text-primary);
        }
        
        .tooltip-item {
          display: flex;
          align-items: center;
          margin-bottom: 4px;
        }
        
        .tooltip-dot {
          margin-right: 6px;
          font-size: 10px;
        }
        
        .tooltip-item.positive .tooltip-dot {
          color: #1DB954;
        }
        
        .tooltip-item.neutral .tooltip-dot {
          color: #007AFF;
        }
        
        .tooltip-item.negative .tooltip-dot {
          color: #FF453A;
        }
        
        .tooltip-label {
          color: var(--text-secondary);
          margin-right: 4px;
        }
        
        .tooltip-value {
          font-weight: 500;
          color: var(--text-primary);
        }
        
        :global(.recharts-default-legend .recharts-legend-item) {
          cursor: pointer !important;
        }
      `}</style>
    </div>
  );
};

// 샘플 데이터 생성 함수
const generateSampleData = (timeRange) => {
  const data = [];
  let startDate;
  let format;
  let points;
  
  switch(timeRange) {
    case '1d':
      startDate = new Date();
      startDate.setHours(0, 0, 0, 0);
      format = (date) => {
        return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:00`;
      };
      points = 24;
      break;
    case '1w':
      startDate = new Date();
      startDate.setDate(startDate.getDate() - 6);
      startDate.setHours(0, 0, 0, 0);
      format = (date) => {
        return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
      };
      points = 7;
      break;
    case '1m':
    default:
      startDate = new Date();
      startDate.setDate(1);
      startDate.setHours(0, 0, 0, 0);
      format = (date) => {
        return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
      };
      points = 30;
      break;
  }
  
  // 특정 패턴으로 데이터 생성
  for (let i = 0; i < points; i++) {
    const date = new Date(startDate);
    if (timeRange === '1d') {
      date.setHours(date.getHours() + i);
    } else if (timeRange === '1w') {
      date.setDate(date.getDate() + i);
    } else {
      date.setDate(date.getDate() + i);
    }
    
    // 요일 또는 시간에 따라 다른 패턴 생성
    const dayHour = timeRange === '1d' ? date.getHours() : date.getDay();
    
    // 아침에는 긍정적, 저녁에는 부정적 경향
    let positive = 0.5 + Math.sin(dayHour / (timeRange === '1d' ? 24 : 7) * Math.PI) * 0.2 + Math.random() * 0.15;
    let negative = 0.3 + Math.cos(dayHour / (timeRange === '1d' ? 12 : 3.5) * Math.PI) * 0.2 + Math.random() * 0.1;
    let neutral = 1 - positive - negative;
    
    // 값 보정
    positive = Math.max(0, Math.min(0.8, positive));
    negative = Math.max(0, Math.min(0.6, negative));
    neutral = Math.max(0.1, Math.min(0.5, neutral));
    
    // 합이 1이 되도록 정규화
    const sum = positive + negative + neutral;
    positive = positive / sum;
    negative = negative / sum;
    neutral = neutral / sum;
    
    data.push({
      date: format(date),
      positive: Number(positive.toFixed(3)),
      neutral: Number(neutral.toFixed(3)),
      negative: Number(negative.toFixed(3))
    });
  }
  
  return data;
};

SentimentTrendChart.propTypes = {
  data: PropTypes.arrayOf(
    PropTypes.shape({
      date: PropTypes.string.isRequired,
      positive: PropTypes.number.isRequired,
      neutral: PropTypes.number.isRequired,
      negative: PropTypes.number.isRequired
    })
  ),
  timeRange: PropTypes.oneOf(['1d', '1w', '1m']),
  height: PropTypes.number,
  withLegend: PropTypes.bool,
  withTooltip: PropTypes.bool,
  withGrid: PropTypes.bool
};

export default SentimentTrendChart; 