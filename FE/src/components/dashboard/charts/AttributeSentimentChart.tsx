// charts/AttributeSentimentChart.tsx
import React from 'react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

interface AttributeSentimentChartProps {
  data: {
    name: string;
    긍정: number;
    부정: number;
    중립: number;
  }[];
}

const AttributeSentimentChart: React.FC<AttributeSentimentChartProps> = ({ data }) => {
  return (
    <Card className="shadow-sm h-full">
      <CardHeader>
        <CardTitle>속성별 감성 분포</CardTitle>
        <CardDescription>주요 속성에 따른 긍정/부정/중립 비율</CardDescription>
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
              contentStyle={{
                backgroundColor: 'white',
                borderRadius: '8px',
                border: '1px solid #e2e8f0',
              }}
              formatter={(value, name) => [`${value}`, name]}
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
