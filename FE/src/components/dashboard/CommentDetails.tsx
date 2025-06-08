import { Comment } from './tabs/CommentsTab';
import React from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { format } from "date-fns";
import { ko } from "date-fns/locale";
import { cn } from "@/lib/utils";
import { ScrollArea } from "@/components/ui/scroll-area";

interface CommentDetailsProps {
  comment: Comment | null;
  open: boolean;
  onClose: () => void;
}

const CommentDetails: React.FC<CommentDetailsProps> = ({ comment, open, onClose }) => {
  if (!comment) return null;

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
      case "틱톡": return "bg-cyan-50 text-cyan-600";
      default: return "";
    }
  };

  // JSON 형식으로 변환된 분석 결과
  const analysisJson = comment.analysis ? JSON.stringify(comment.analysis, null, 2) : "{}";

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-hidden flex flex-col">
        <DialogHeader>
          <DialogTitle>댓글 상세 분석</DialogTitle>
          <DialogDescription>
            ID: {comment.id}
          </DialogDescription>
        </DialogHeader>

        <ScrollArea className="flex-1 mt-4">
          <div className="space-y-6 pb-4">
            {/* 원본 댓글 */}
            <div className="border rounded-md p-4 bg-secondary/20">
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
              <p className="text-sm mt-2">{comment.text}</p>
              
              <div className="mt-4 flex flex-wrap gap-2">
                {comment.attributes.map((attr, index) => (
                  <Badge key={index} variant="outline">
                    {attr}
                  </Badge>
                ))}
              </div>
            </div>
            
            {/* 분석 결과 */}
            <div>
              <h3 className="text-lg font-medium mb-2">분석 결과</h3>
              <div className="rounded-md bg-muted p-4 overflow-x-auto">
                <pre className="text-xs">
                  {analysisJson}
                </pre>
              </div>
            </div>
          </div>
        </ScrollArea>
      </DialogContent>
    </Dialog>
  );
};

export default CommentDetails;
