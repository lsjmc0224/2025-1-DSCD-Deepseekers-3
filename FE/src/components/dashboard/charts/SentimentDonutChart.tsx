
import React from 'react';
import { PieChart, Pie, Tooltip, ResponsiveContainer, Cell, Legend } from 'recharts';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

interface SentimentDonutChartProps {
  title: string;
  description: string;
  data: {
    name: string;
    value: number;
    color: string;
  }[];
  hideHeader?: boolean;
  height?: number;
  emptyMessage?: string;
  showCount?: boolean;
}

const SentimentDonutChart: React.FC<SentimentDonutChartProps> = ({ 
  title, 
  description, 
  data,
  hideHeader = false,
  height = 300,
  emptyMessage = "데이터가 없습니다",
  showCount = false
}) => {
  // Get colors array for legend
  const colors = data.map(item => item.color);
  
  // Calculate total for percentage
  const total = data.reduce((acc, cur) => acc + cur.value, 0);
  
  return (
    <Card className="shadow-sm h-full">
      {!hideHeader && (
        <CardHeader>
          <CardTitle>{title}</CardTitle>
          <CardDescription>{description}</CardDescription>
        </CardHeader>
      )}
      <CardContent>
        {data.length > 0 ? (
          <div className="relative">
            <ResponsiveContainer width="100%" height={height}>
              <PieChart>
                <Pie 
                  data={data} 
                  cx="50%" 
                  cy="50%" 
                  innerRadius={60}
                  outerRadius={90} 
                  fill="#8884d8"
                  paddingAngle={2}
                  dataKey="value"
                  nameKey="name"
                  label={({ name, percent }) => 
                    showCount 
                      ? `${name} ${(percent * 100).toFixed(0)}%`
                      : `${name} ${(percent * 100).toFixed(0)}%`
                  }
                  labelLine={false}
                >
                  {data.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Legend 
                  layout="horizontal" 
                  verticalAlign="bottom" 
                  align="center"
                  formatter={(value, entry, index) => {
                    const item = data[index];
                    if (showCount && item) {
                      const percent = ((item.value / total) * 100).toFixed(1);
                      return `${value} ${percent}% (${item.value}건)`;
                    }
                    return value;
                  }}
                />
                <Tooltip 
                  formatter={(value: number, name) => [
                    showCount 
                      ? `${value}건 (${((value / total) * 100).toFixed(1)}%)`
                      : `${value}개 (${((value / total) * 100).toFixed(1)}%)`, 
                    `${name}`
                  ]}
                  contentStyle={{ 
                    backgroundColor: 'white', 
                    borderRadius: '8px', 
                    border: '1px solid #e2e8f0' 
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
            
            {/* No inner text/predominant sentiment text as requested */}
          </div>
        ) : (
          <div className="flex items-center justify-center h-[200px] text-muted-foreground">
            {emptyMessage}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default SentimentDonutChart;
