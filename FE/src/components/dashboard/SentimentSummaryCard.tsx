
import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ArrowUp, ArrowDown, TrendingUp, TrendingDown } from "lucide-react";
import { cn } from "@/lib/utils";

interface SentimentSummaryCardProps {
  title: string;
  value: string;
  delta: string;
  deltaType: "increase" | "decrease";
  description: string;
}

const SentimentSummaryCard: React.FC<SentimentSummaryCardProps> = ({
  title,
  value,
  delta,
  deltaType,
  description
}) => {
  return (
    <Card className="shadow-sm h-full">
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        {deltaType === "increase" ? (
          <TrendingUp className="h-4 w-4 text-emerald-500" />
        ) : (
          <TrendingDown className="h-4 w-4 text-red-500" />
        )}
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
        <div className="flex items-center pt-2">
          {deltaType === "increase" ? (
            <ArrowUp className="h-4 w-4 text-emerald-500" />
          ) : (
            <ArrowDown className="h-4 w-4 text-red-500" />
          )}
          <span
            className={cn(
              "text-sm font-medium",
              deltaType === "increase" ? "text-emerald-500" : "text-red-500"
            )}
          >
            {delta}
          </span>
          <span className="text-sm text-muted-foreground ml-1">{description}</span>
        </div>
      </CardContent>
    </Card>
  );
};

export default SentimentSummaryCard;
