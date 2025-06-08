import React from 'react';
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
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle
} from "@/components/ui/card";
import { format } from "date-fns";
import { ko } from "date-fns/locale";

interface SentimentTrendChartProps {
  dateRange: {
    from: Date;
    to?: Date;
  };
  platform?: string;
  data: {
    date: string;
    positive: number;
    negative: number;
    neutral: number;
  }[];
}

const SentimentTrendChart: React.FC<SentimentTrendChartProps> = ({
  dateRange,
  platform = "전체",
  data
}) => {
  const SENTIMENT_COLORS = {
    positive: "#A0E8AF",
    negative: "#F28B82",
    neutral: "#9FA8DA",
    total: "#D1C4E9"
  };

  const transformedData = data.map(item => {
    const total = item.positive + item.negative + item.neutral;
    return {
      date: item.date,
      긍정: item.positive,
      부정: item.negative,
      중립: item.neutral,
      전체: total
    };
  });

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
            data={transformedData}
            margin={{ top: 5, right: 30, left: 0, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip
              contentStyle={{ backgroundColor: 'white', borderRadius: '8px', border: '1px solid #e2e8f0' }}
              formatter={(value: number, name) => [`${value}개`, name]}
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
              strokeDasharray="5 5"
              dot={{ r: 3 }}
              activeDot={{ r: 5 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
};

export default SentimentTrendChart;
