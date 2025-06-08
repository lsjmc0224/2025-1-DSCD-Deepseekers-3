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
  date: string; // ISO 8601 형식
  sentiment: "positive" | "negative";
  source: "유튜브" | "틱톡" | "커뮤니티";
  likes: number | null;
}

interface CommentsListProps {
  title: string;
  description?: string;
  comments: Comment[];
}

const CommentsList: React.FC<CommentsListProps> = ({ title, description, comments }) => {
  const getSentimentColor = (sentiment: string) => {
    switch (sentiment) {
      case "positive": return "bg-green-100 text-green-800";
      case "negative": return "bg-red-100 text-red-800";
      default: return "";
    }
  };

  const getSourceColor = (source: string) => {
    switch (source) {
      case "유튜브": return "bg-red-50 text-red-600";
      case "틱톡": return "bg-blue-50 text-blue-600";
      case "인스티즈": return "bg-purple-50 text-purple-600";
      default: return "";
    }
  };

  return (
    <Card className="shadow-sm h-full">
      <CardHeader>
        <CardTitle>{title}</CardTitle>
        {description && <CardDescription>{description}</CardDescription>}
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {comments.map((comment) => (
            <div key={comment.id} className="border rounded-md p-3">
              <div className="flex justify-between items-start mb-2">
                <div className="flex gap-2 flex-wrap">
                  <Badge className={cn(getSentimentColor(comment.sentiment))}>
                    {comment.sentiment === "positive" ? "긍정" : "부정"}
                  </Badge>
                  <Badge variant="outline" className={cn(getSourceColor(comment.source))}>
                    {comment.source}
                  </Badge>
                  {comment.likes !== null && (
                    <Badge variant="secondary" className="bg-gray-100 text-gray-800">
                      👍 {comment.likes}
                    </Badge>
                  )}
                </div>
                <span className="text-xs text-muted-foreground">
                  {format(new Date(comment.date), "yyyy.MM.dd HH:mm", { locale: ko })}
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
