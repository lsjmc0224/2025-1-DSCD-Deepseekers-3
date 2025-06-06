import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

interface SentimentKeywordsSummaryProps {
  title: string;
  description: string;
  keywords: string[];  // ✅ string[]로 변경
}

const SentimentKeywordsSummary: React.FC<SentimentKeywordsSummaryProps> = ({
  title,
  description,
  keywords
}) => {
  const sizeLevels = ["xl", "lg", "md", "sm", "xs"] as const;

  const getSizeClass = (size: typeof sizeLevels[number]) => {
    switch (size) {
      case "xs": return "text-xs";
      case "sm": return "text-sm";
      case "md": return "text-base";
      case "lg": return "text-lg";
      case "xl": return "text-xl";
      default: return "text-sm";
    }
  };

  const typeStyle = title.includes("긍정")
    ? "bg-green-100 text-green-800 hover:bg-green-200 border-[#4CAF50]"
    : "bg-red-100 text-red-800 hover:bg-red-200 border-[#F06292]";

  const generateSizedKeywords = () => {
    const total = keywords.length;
    if (total === 0) return [];

    return keywords.map((text, index) => {
      const ratio = index / total;
      let size: typeof sizeLevels[number];

      if (ratio < 0.2) size = "xl";
      else if (ratio < 0.4) size = "lg";
      else if (ratio < 0.6) size = "md";
      else if (ratio < 0.8) size = "sm";
      else size = "xs";

      return { text, size };
    });
  };

  const sizedKeywords = generateSizedKeywords();

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
          {sizedKeywords.map((kw, index) => (
            <Badge
              key={index}
              variant="outline"
              className={cn(
                "px-2 py-1 rounded-full font-normal border",
                getSizeClass(kw.size),
                typeStyle
              )}
            >
              {kw.text}
            </Badge>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};

export default SentimentKeywordsSummary;
