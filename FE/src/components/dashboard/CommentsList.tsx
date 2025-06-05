
import React from 'react';
import { 
  Card, 
  CardContent, 
  CardDescription, 
  CardHeader, 
  CardTitle 
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import { format } from "date-fns";
import { ko } from "date-fns/locale";

interface Comment {
  id: string;
  text: string;
  date: Date;
  sentiment: "positive" | "negative" | "neutral";
  source: "유튜브" | "커뮤니티";
}

interface CommentsListProps {
  title: string;
  description: string;
  comments: Comment[];
}

const CommentsList: React.FC<CommentsListProps> = ({ title, description, comments }) => {
  const getSentimentColor = (sentiment: string) => {
    switch (sentiment) {
      case "positive": return "bg-green-100 text-green-800";
      case "negative": return "bg-red-100 text-red-800";
      case "neutral": return "bg-blue-100 text-blue-800";
      default: return "";
    }
  };

  const getSourceColor = (source: string) => {
    switch (source) {
      case "유튜브": return "bg-red-50 text-red-600";
      case "커뮤니티": return "bg-purple-50 text-purple-600";
      default: return "";
    }
  };

  return (
    <Card className="shadow-sm h-full">
      <CardHeader>
        <CardTitle>{title}</CardTitle>
        <CardDescription>{description}</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {comments.map((comment) => (
            <div key={comment.id} className="border rounded-md p-3">
              <div className="flex justify-between items-start mb-2">
                <div className="flex gap-2">
                  <Badge className={cn(getSentimentColor(comment.sentiment))}>
                    {comment.sentiment === "positive" ? "긍정" : 
                     comment.sentiment === "negative" ? "부정" : "중립"}
                  </Badge>
                  <Badge variant="outline" className={cn(getSourceColor(comment.source))}>
                    {comment.source}
                  </Badge>
                </div>
                <span className="text-xs text-muted-foreground">
                  {format(comment.date, "yyyy.MM.dd HH:mm", { locale: ko })}
                </span>
              </div>
              <p className="text-sm">{comment.text}</p>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};

export default CommentsList;
