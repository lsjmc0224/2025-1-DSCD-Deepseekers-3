import React, { useState, useEffect } from 'react';
import { ResponsiveLine } from '@nivo/line';
import analysisService from '../../services/analysisService';

/**
 * SentimentTrendChart를 위한 데모 컴포넌트
 * 
 * 다양한 시간 범위와 설정으로 감성 트렌드 차트를 테스트할 수 있는 데모 페이지
 */
const SentimentTrendChartDemo = () => {
  const [chartData, setChartData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [period, setPeriod] = useState(30); // 기본 30일
  
  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        
        // 실제 API에서 데이터 로드
        const trendsData = await analysisService.getSentimentTrends({ days: period });
        
        if (!trendsData || trendsData.length === 0) {
          setError('데이터가 존재하지 않습니다.');
          setChartData([]);
          return;
        }
        
        // 차트 데이터 포맷 변환
        const formattedData = [
          {
            id: '긍정',
            color: 'hsl(120, 70%, 50%)',
            data: trendsData.map(item => ({
              x: new Date(item.date).toISOString().split('T')[0],
              y: item.positivePercentage
            }))
          },
          {
            id: '중립',
            color: 'hsl(220, 70%, 50%)',
            data: trendsData.map(item => ({
              x: new Date(item.date).toISOString().split('T')[0],
              y: item.neutralPercentage
            }))
          },
          {
            id: '부정',
            color: 'hsl(0, 70%, 50%)',
            data: trendsData.map(item => ({
              x: new Date(item.date).toISOString().split('T')[0],
              y: item.negativePercentage
            }))
          }
        ];
        
        setChartData(formattedData);
        setError(null);
      } catch (err) {
        console.error('Failed to load sentiment trend data:', err);
        setError('데이터를 불러오는 중 오류가 발생했습니다.');
        setChartData([]);
      } finally {
        setLoading(false);
      }
    };
    
    loadData();
  }, [period]);
  
  // 기간 변경 핸들러
  const handlePeriodChange = (newPeriod) => {
    setPeriod(newPeriod);
  };
  
  // Nivo Line 차트 테마
  const theme = {
    axis: {
      ticks: {
        text: {
          fill: '#555',
          fontSize: 12
        }
      },
      legend: {
        text: {
          fill: '#333',
          fontSize: 14,
          fontWeight: 600
        }
      }
    },
    grid: {
      line: {
        stroke: '#eee',
        strokeWidth: 1
      }
    },
    legends: {
      text: {
        fill: '#333',
        fontSize: 12
      }
    },
    tooltip: {
      container: {
        background: '#fff',
        fontSize: 12,
        borderRadius: 4,
        boxShadow: '0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24)'
      }
    }
  };
  
  return (
    <div className="sentiment-trend-chart-container">
      <h2>감성 분석 트렌드</h2>
      
      <div className="chart-controls">
        <div className="period-selector">
          <button
            className={period === 7 ? 'active' : ''}
            onClick={() => handlePeriodChange(7)}
          >
            7일
          </button>
          <button
            className={period === 30 ? 'active' : ''}
            onClick={() => handlePeriodChange(30)}
          >
            30일
          </button>
          <button
            className={period === 90 ? 'active' : ''}
            onClick={() => handlePeriodChange(90)}
          >
            90일
          </button>
        </div>
      </div>
      
      <div className="chart-wrapper" style={{ height: '400px' }}>
        {loading ? (
          <div className="loading-indicator">데이터 로딩 중...</div>
        ) : error ? (
          <div className="error-message">{error}</div>
        ) : chartData.length > 0 ? (
          <ResponsiveLine
            data={chartData}
            margin={{ top: 20, right: 110, bottom: 50, left: 60 }}
            xScale={{ type: 'point' }}
            yScale={{ 
              type: 'linear', 
              min: 0, 
              max: 100,
              stacked: false
            }}
            axisTop={null}
            axisRight={null}
            axisBottom={{
              tickSize: 5,
              tickPadding: 5,
              tickRotation: -45,
              legend: '날짜',
              legendOffset: 40,
              legendPosition: 'middle'
            }}
            axisLeft={{
              tickSize: 5,
              tickPadding: 5,
              tickRotation: 0,
              legend: '백분율 (%)',
              legendOffset: -50,
              legendPosition: 'middle',
              format: value => `${value}%`
            }}
            colors={{ scheme: 'category10' }}
            pointSize={10}
            pointColor={{ theme: 'background' }}
            pointBorderWidth={2}
            pointBorderColor={{ from: 'serieColor' }}
            pointLabelYOffset={-12}
            useMesh={true}
            legends={[
              {
                anchor: 'bottom-right',
                direction: 'column',
                justify: false,
                translateX: 100,
                translateY: 0,
                itemsSpacing: 0,
                itemDirection: 'left-to-right',
                itemWidth: 80,
                itemHeight: 20,
                itemOpacity: 0.75,
                symbolSize: 12,
                symbolShape: 'circle',
                symbolBorderColor: 'rgba(0, 0, 0, .5)',
                effects: [
                  {
                    on: 'hover',
                    style: {
                      itemBackground: 'rgba(0, 0, 0, .03)',
                      itemOpacity: 1
                    }
                  }
                ]
              }
            ]}
            theme={theme}
            enableGridX={false}
            curve="monotoneX"
            enableSlices="x"
          />
        ) : (
          <div className="no-data-message">
            데이터가 없습니다.
          </div>
        )}
      </div>
    </div>
  );
};

export default SentimentTrendChartDemo; 