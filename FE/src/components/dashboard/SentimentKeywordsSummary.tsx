
import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

interface Keyword {
  text: string;
  size: "xs" | "sm" | "md" | "lg" | "xl";
  type: "positive" | "negative" | "neutral";
}

interface SentimentKeywordsSummaryProps {
  title: string;
  description: string;
  keywords: Keyword[];
}

const SentimentKeywordsSummary: React.FC<SentimentKeywordsSummaryProps> = ({
  title,
  description,
  keywords
}) => {
  const getSize = (size: string) => {
    switch (size) {
      case "xs": return "text-xs";
      case "sm": return "text-sm";
      case "md": return "text-base";
      case "lg": return "text-lg";
      case "xl": return "text-xl";
      default: return "text-sm";
    }
  };

  const getType = (type: string) => {
    switch (type) {
      case "positive": return "bg-green-100 text-green-800 hover:bg-green-200 border-[#4CAF50]";
      case "negative": return "bg-red-100 text-red-800 hover:bg-red-200 border-[#F06292]";
      case "neutral": return "bg-blue-100 text-blue-800 hover:bg-blue-200";
      default: return "";
    }
  };

  return (
    <Card className={cn(
      "shadow-sm h-full", 
      title.includes("긍정") ? "border-l-4 border-l-[#4CAF50]" : "border-l-4 border-l-[#F06292]"
    )}>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
        <CardDescription>{description}</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="flex flex-wrap gap-2">
          {keywords.map((keyword, index) => (
            <Badge
              key={index}
              variant="outline"
              className={cn(
                "px-2 py-1 rounded-full font-normal border",
                getSize(keyword.size),
                getType(keyword.type)
              )}
            >
              {keyword.text}
            </Badge>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};

export default SentimentKeywordsSummary;
