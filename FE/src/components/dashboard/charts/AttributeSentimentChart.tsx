
import React from 'react';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend,
  ResponsiveContainer 
} from 'recharts';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

// 편의점 간식 속성별 감성 분포를 위한 목업 데이터
const data = [
  {
    name: '맛',
    긍정: 7,
    부정: 1,
    중립: 1,
  },
  {
    name: '식감',
    긍정: 5,
    부정: 2,
    중립: 2,
  },
  {
    name: '가격',
    긍정: 3,
    부정: 4,
    중립: 2,
  },
  {
    name: '주관적 평가',
    긍정: 6,
    부정: 1,
    중립: 2,
  },
  {
    name: '기타',
    긍정: 4,
    부정: 2,
    중립: 3,
  },
];

const AttributeSentimentChart = () => {
  return (
    <Card className="shadow-sm h-full">
      <CardHeader>
        <CardTitle>속성별 감성 분포</CardTitle>
        <CardDescription>편의점 간식의 주요 속성에 따른 긍정/부정/중립 비율</CardDescription>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart
            data={data}
            margin={{ top: 20, right: 30, left: 0, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip 
              contentStyle={{ backgroundColor: 'white', borderRadius: '8px', border: '1px solid #e2e8f0' }}
              formatter={(value, name) => [`${value}%`, `${name}`]}
              labelFormatter={(label) => `속성: ${label}`}
            />
            <Legend />
            <Bar dataKey="긍정" fill="#4ade80" barSize={30} />
            <Bar dataKey="부정" fill="#f87171" barSize={30} />
            <Bar dataKey="중립" fill="#60a5fa" barSize={30} />
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
};

export default AttributeSentimentChart;
