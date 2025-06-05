import React, { useEffect, useState } from 'react';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend,
  ResponsiveContainer 
} from 'recharts';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { format, eachDayOfInterval, startOfDay } from "date-fns";
import { ko } from "date-fns/locale";

interface SentimentTrendChartProps {
  dateRange: {
    from: Date;
    to?: Date;
  };
  platform?: string;
}

const SentimentTrendChart: React.FC<SentimentTrendChartProps> = ({ 
  dateRange,
  platform = "전체"
}) => {
  const [data, setData] = useState<any[]>([]);

  // Define sentiment colors according to specifications
  const SENTIMENT_COLORS = {
    positive: "#A0E8AF", // Light Green
    negative: "#F28B82", // Soft Red
    neutral: "#9FA8DA",  // Purple
    total: "#D1C4E9"     // Light Purple (for total line)
  };

  // Generate data based on date range and platform
  useEffect(() => {
    // Safely handle the dateRange prop to prevent "undefined" errors
    if (!dateRange || !dateRange.from) {
      // Default to last 7 days if dateRange is invalid
      const today = new Date();
      const sevenDaysAgo = new Date(today);
      sevenDaysAgo.setDate(today.getDate() - 7);
      
      generateChartData(sevenDaysAgo, today, platform);
      return;
    }

    // Generate data using the provided date range
    generateChartData(dateRange.from, dateRange.to || new Date(), platform);
  }, [dateRange, platform]);

  // Helper function to generate chart data
  const generateChartData = (startDate: Date, endDate: Date, selectedPlatform: string) => {
    // Get all days in the date range
    const days = eachDayOfInterval({
      start: startOfDay(startDate),
      end: startOfDay(endDate)
    });

    // Generate data for each day based on platform
    const newData = days.map(day => {
      const dateStr = format(day, 'M/d', { locale: ko });
      
      // Generate different data based on platform
      let positive, negative, neutral;
      
      switch(selectedPlatform) {
        case "유튜브":
          // YouTube typically has higher engagement
          positive = 6 + Math.floor(Math.random() * 2.5);
          negative = 2 + Math.floor(Math.random() * 1.5);
          neutral = 1.5 + Math.floor(Math.random() * 1);
          break;
        case "틱톡":
          // TikTok has more varied sentiment
          positive = 4.5 + Math.floor(Math.random() * 2);
          negative = 3 + Math.floor(Math.random() * 2);
          neutral = 2 + Math.floor(Math.random() * 1.5);
          break;
        case "커뮤니티":
          // Community platforms tend to have more critical discussions
          positive = 3.5 + Math.floor(Math.random() * 1.5);
          negative = 4 + Math.floor(Math.random() * 2);
          neutral = 2.5 + Math.floor(Math.random() * 1.5);
          break;
        default: // "전체"
          // Overall balanced data
          positive = 4.5 + Math.floor(Math.random() * 2);
          negative = 3 + Math.floor(Math.random() * 1.5);
          neutral = 2 + Math.floor(Math.random() * 1.5);
      }
      
      const total = positive + negative + neutral;
      
      return {
        date: dateStr,
        긍정: positive,
        부정: negative,
        중립: neutral,
        전체: total
      };
    });

    setData(newData);
  };

  return (
    <Card className="shadow-sm">
      <CardHeader>
        <CardTitle>시간별 트렌드</CardTitle>
        <CardDescription>
          편의점 간식 관련 댓글 수 추이 (감성별)
          {dateRange && dateRange.from && (
            <span className="ml-2 text-sm font-normal">
              ({format(dateRange.from, 'M/d', { locale: ko })} ~ 
               {dateRange.to ? format(dateRange.to, 'M/d', { locale: ko }) : format(new Date(), 'M/d', { locale: ko })})
            </span>
          )}
          {platform && platform !== "전체" && (
            <span className="ml-2 text-sm font-normal text-blue-600">
              - {platform}
            </span>
          )}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart
            data={data}
            margin={{ top: 5, right: 30, left: 0, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip 
              contentStyle={{ backgroundColor: 'white', borderRadius: '8px', border: '1px solid #e2e8f0' }}
              formatter={(value: number, name) => [`${value}개`, `${name}`]}
              labelFormatter={(label) => `${label} 일자`}
            />
            <Legend />
            <Line 
              type="linear" 
              dataKey="긍정" 
              stroke={SENTIMENT_COLORS.positive}
              strokeWidth={2} 
              dot={{ r: 3 }}
              activeDot={{ r: 5 }}
            />
            <Line 
              type="linear" 
              dataKey="부정" 
              stroke={SENTIMENT_COLORS.negative}
              strokeWidth={2} 
              dot={{ r: 3 }}
              activeDot={{ r: 5 }}
            />
            <Line 
              type="linear" 
              dataKey="중립" 
              stroke={SENTIMENT_COLORS.neutral}
              strokeWidth={2} 
              dot={{ r: 3 }}
              activeDot={{ r: 5 }}
            />
            <Line 
              type="linear" 
              dataKey="전체" 
              stroke={SENTIMENT_COLORS.total}
              strokeWidth={2}
              dot={{ r: 3 }}
              activeDot={{ r: 5 }}
              strokeDasharray="5 5"
            />
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
};

export default SentimentTrendChart;
