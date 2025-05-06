import React, { useState, useEffect } from 'react';
import {
  ResponsiveContainer,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  ScatterChart,
  Scatter,
  ZAxis,
  Cell,
  Rectangle
} from 'recharts';
import PropTypes from 'prop-types';
import analysisService from '../../services/analysisService';

// 히트맵 색상 설정
const COLOR_SCALE = {
  positive: ['#e6fff5', '#b2f5ea', '#81e6d9', '#4fd1c5', '#38b2ac'],
  neutral: ['#edf2f7', '#e2e8f0', '#cbd5e0', '#a0aec0', '#718096'],
  negative: ['#fff5f5', '#fed7d7', '#feb2b2', '#fc8181', '#f56565']
};

// 데이터 포인트 크기 스케일 설정
const SIZE_RANGE = [200, 800];

/**
 * 감성 분석 결과 히트맵 컴포넌트
 * 
 * 시간별, 카테고리별 감성 변화를 히트맵으로 시각화합니다.
 * Recharts의 ScatterChart를 활용하여 히트맵을 구현합니다.
 */
const SentimentHeatmap = ({
  startDate,
  endDate,
  period = 'day',
  categories = ['taste', 'price', 'packaging', 'place', 'repurchase'],
  sentiment = 'positive',
  height = 400
}) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [heatmapData, setHeatmapData] = useState([]);
  const [maxValue, setMaxValue] = useState(1);
  const [timeLabels, setTimeLabels] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);

        // 감성 분석 트렌드 데이터 가져오기
        const trendData = await analysisService.getSentimentTrends({
          period,
          startDate,
          endDate
        });

        if (!trendData || trendData.length === 0) {
          setHeatmapData([]);
          setTimeLabels([]);
          setMaxValue(1);
          return;
        }

        // 카테고리별 감성 데이터 가져오기
        // 이 예제에서는 가짜 데이터를 생성하지만, 실제로는 API에서 가져올 수 있습니다
        // 실제 API 구현 시 카테고리별로 데이터를 가져오는 API를 호출해야 합니다
        const categoryData = await generateCategoryData(trendData, categories);

        // 히트맵 데이터 포맷팅
        const formattedData = [];
        let max = 0;
        
        // 시간 라벨 추출
        const timestamps = trendData.map(item => item.period);
        setTimeLabels(timestamps);

        // 각 카테고리별, 시간별 데이터 포인트 생성
        for (let i = 0; i < categories.length; i++) {
          const category = categories[i];

          for (let j = 0; j < timestamps.length; j++) {
            const time = timestamps[j];
            const value = categoryData[category][j][`${sentiment}_ratio`] || 0;
            
            // 최대값 업데이트
            if (value > max) max = value;
            
            formattedData.push({
              x: j,  // x축 인덱스
              y: i,  // y축 인덱스
              z: value, // 값 (히트맵 색상 결정)
              value, // 실제 값 (툴팁 표시용)
              category,
              time,
              sentiment
            });
          }
        }

        setMaxValue(max);
        setHeatmapData(formattedData);
      } catch (err) {
        console.error('Error fetching heatmap data:', err);
        setError('데이터를 불러오는 중 오류가 발생했습니다');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [startDate, endDate, period, categories, sentiment]);

  // 히트맵 셀 커스텀 렌더링
  const CustomHeatmapCell = (props) => {
    const { x, y, width, height, value } = props;
    
    // 값에 따라 색상 인덱스 계산
    const colorIndex = Math.min(
      4, 
      Math.floor(value * 5 / maxValue || 0)
    );
    
    // 선택된 감성에 따라 색상 스케일 선택
    const colorScale = COLOR_SCALE[sentiment] || COLOR_SCALE.positive;
    const fill = colorScale[colorIndex];
    
    return <Rectangle x={x} y={y} width={width} height={height} fill={fill} />;
  };

  // 감성 값을 백분율로 포맷팅
  const formatSentimentValue = (value) => {
    return `${(value * 100).toFixed(1)}%`;
  };

  // 툴팁 커스터마이징
  const CustomTooltip = ({ active, payload }) => {
    if (!active || !payload || !payload[0]) return null;

    const data = payload[0].payload;
    
    return (
      <div className="custom-tooltip" style={{
        backgroundColor: '#fff',
        padding: '10px',
        border: '1px solid #ccc',
        borderRadius: '5px',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
      }}>
        <p style={{ margin: '0 0 5px', fontWeight: 'bold' }}>{data.category}</p>
        <p style={{ margin: '0 0 5px' }}>
          <span>시간: </span>
          <span>{new Date(data.time).toLocaleString()}</span>
        </p>
        <p style={{ margin: '0', color: getColorForSentiment(sentiment) }}>
          <span>{getSentimentLabel(sentiment)}: </span>
          <span>{formatSentimentValue(data.value)}</span>
        </p>
      </div>
    );
  };

  // 선택된 감성에 따른 라벨 반환
  const getSentimentLabel = (sentimentType) => {
    switch (sentimentType) {
      case 'positive': return '긍정';
      case 'neutral': return '중립';
      case 'negative': return '부정';
      default: return '긍정';
    }
  };

  // 선택된 감성에 따른 색상 반환
  const getColorForSentiment = (sentimentType) => {
    switch (sentimentType) {
      case 'positive': return '#38b2ac';
      case 'neutral': return '#718096';
      case 'negative': return '#e53e3e';
      default: return '#38b2ac';
    }
  };

  if (loading) {
    return <div className="chart-loading">데이터 로딩 중...</div>;
  }

  if (error) {
    return <div className="chart-error">{error}</div>;
  }

  if (heatmapData.length === 0) {
    return <div className="chart-empty">표시할 데이터가 없습니다</div>;
  }

  return (
    <div className="sentiment-heatmap-container">
      <div className="chart-title">
        <h3>카테고리별 {getSentimentLabel(sentiment)} 감성 변화</h3>
      </div>
      
      <ResponsiveContainer width="100%" height={height}>
        <ScatterChart
          margin={{ top: 20, right: 20, bottom: 20, left: 80 }}
        >
          <XAxis
            type="number"
            dataKey="x"
            name="시간"
            domain={[0, timeLabels.length - 1]}
            tickCount={Math.min(7, timeLabels.length)}
            tickFormatter={index => {
              if (index < 0 || index >= timeLabels.length) return '';
              
              const date = new Date(timeLabels[index]);
              let format;
              
              switch (period) {
                case 'hour':
                  format = date.getHours() + '시';
                  break;
                case 'day':
                  format = (date.getMonth() + 1) + '/' + date.getDate();
                  break;
                case 'week':
                  format = (date.getMonth() + 1) + '/' + date.getDate() + ' 주';
                  break;
                case 'month':
                  format = (date.getMonth() + 1) + '월';
                  break;
                default:
                  format = (date.getMonth() + 1) + '/' + date.getDate();
              }
              
              return format;
            }}
            tick={{ fontSize: 12 }}
          />
          
          <YAxis
            type="number"
            dataKey="y"
            name="카테고리"
            domain={[0, categories.length - 1]}
            tickCount={categories.length}
            tickFormatter={index => categories[index] || ''}
            tick={{ fontSize: 12 }}
          />
          
          <ZAxis
            type="number"
            dataKey="z"
            domain={[0, maxValue]}
            range={SIZE_RANGE}
          />
          
          <Tooltip content={<CustomTooltip />} />
          
          <Legend
            iconType="square"
            iconSize={10}
            formatter={(value) => getSentimentLabel(value)}
            wrapperStyle={{ bottom: 0 }}
          />
          
          <Scatter
            name={sentiment}
            data={heatmapData}
            fill={getColorForSentiment(sentiment)}
            shape={<CustomHeatmapCell />}
          />
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  );
};

SentimentHeatmap.propTypes = {
  startDate: PropTypes.oneOfType([PropTypes.string, PropTypes.instanceOf(Date)]),
  endDate: PropTypes.oneOfType([PropTypes.string, PropTypes.instanceOf(Date)]),
  period: PropTypes.oneOf(['hour', 'day', 'week', 'month']),
  categories: PropTypes.arrayOf(PropTypes.string),
  sentiment: PropTypes.oneOf(['positive', 'neutral', 'negative']),
  height: PropTypes.number
};

// 카테고리별 감성 데이터 생성 (실제로는 API에서 가져와야 함)
const generateCategoryData = async (trendData, categories) => {
  const result = {};
  
  // 각 카테고리별 시간 시리즈 데이터 생성
  categories.forEach(category => {
    result[category] = trendData.map(timepoint => {
      // 카테고리별로 약간의 변동성 추가
      const variability = Math.random() * 0.3 - 0.15;
      
      return {
        period: timepoint.period,
        positive_ratio: Math.max(0, Math.min(1, timepoint.positive_ratio + variability)),
        neutral_ratio: Math.max(0, Math.min(1, timepoint.neutral_ratio + variability)),
        negative_ratio: Math.max(0, Math.min(1, timepoint.negative_ratio + variability))
      };
    });
  });
  
  return result;
};

export default SentimentHeatmap; 