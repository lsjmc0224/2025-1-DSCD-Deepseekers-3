
import React from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import { format } from "date-fns";
import { ko } from "date-fns/locale";
import { Search } from "lucide-react";

interface Comment {
  id: string;
  text: string;
  date: Date;
  sentiment: "positive" | "negative" | "neutral";
  source: "유튜브" | "커뮤니티" | "틱톡";
  attributes: string[];
  likes: number;
}

interface CommentsTableProps {
  comments: Comment[];
  onViewDetails: (id: string) => void;
}

const CommentsTable: React.FC<CommentsTableProps> = ({ comments, onViewDetails }) => {
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

  return (
    <div className="rounded-md border">
      <div className="relative overflow-x-auto">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>채널</TableHead>
              <TableHead className="w-[300px]">내용</TableHead>
              <TableHead>날짜</TableHead>
              <TableHead>감성</TableHead>
              <TableHead>속성</TableHead>
              <TableHead>좋아요</TableHead>
              <TableHead className="text-right">상세</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {comments.length > 0 ? (
              comments.map((comment) => (
                <TableRow key={comment.id}>
                  <TableCell>
                    <Badge variant="outline" className={cn(getSourceColor(comment.source))}>
                      {comment.source}
                    </Badge>
                  </TableCell>
                  <TableCell className="font-medium">
                    {comment.text.length > 50 
                      ? `${comment.text.substring(0, 50)}...` 
                      : comment.text}
                  </TableCell>
                  <TableCell>
                    {format(comment.date, "yyyy.MM.dd", { locale: ko })}
                  </TableCell>
                  <TableCell>
                    <Badge className={cn(getSentimentColor(comment.sentiment))}>
                      {comment.sentiment === "positive" ? "긍정" : 
                      comment.sentiment === "negative" ? "부정" : "중립"}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <div className="flex flex-wrap gap-1">
                      {comment.attributes.map((attr, index) => (
                        <Badge key={index} variant="outline" className="text-xs">
                          {attr}
                        </Badge>
                      ))}
                    </div>
                  </TableCell>
                  <TableCell>{comment.likes}</TableCell>
                  <TableCell className="text-right">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => onViewDetails(comment.id)}
                    >
                      <Search className="h-4 w-4" />
                    </Button>
                  </TableCell>
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={7} className="text-center py-8 text-muted-foreground">
                  표시할 결과가 없습니다
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>
      <div className="flex items-center justify-end p-4">
        <div className="text-muted-foreground text-sm">
          총 {comments.length}개 항목
        </div>
      </div>
    </div>
  );
};

export default CommentsTable;
