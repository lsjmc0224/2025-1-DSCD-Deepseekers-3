
import React from 'react';
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { 
  CalendarIcon, 
  ChevronDown, 
  ChevronUp, 
  YoutubeIcon 
} from "lucide-react";
import { format } from "date-fns";
import { ko } from "date-fns/locale";
import { cn } from "@/lib/utils";

interface VideoCardProps {
  video: {
    id: string;
    title: string;
    thumbnailUrl: string;
    views: number;
    likes: number;
    comments: number;
    publishDate: Date;
    sentiments: {
      positive: number;
      negative: number;
      neutral: number;
    };
    isShort: boolean;
  };
}

// 간식 이모지 배열
const snackEmojis = ['🍫', '🍪', '🍭', '🍩', '🍰', '🥐', '🍦', '🌮', '🥤', '🥡', '🍙', '🍕', '🥨', '🥪', '🍿'];

const VideoCard: React.FC<VideoCardProps> = ({ video }) => {
  // 긍정 비율 계산
  const sentimentTotal = 
    video.sentiments.positive + video.sentiments.negative + video.sentiments.neutral;
  
  const positivePercent = sentimentTotal > 0 
    ? Math.round((video.sentiments.positive / sentimentTotal) * 100) 
    : 0;
  
  const negativePercent = sentimentTotal > 0 
    ? Math.round((video.sentiments.negative / sentimentTotal) * 100) 
    : 0;
  
  const neutralPercent = sentimentTotal > 0 
    ? Math.round((video.sentiments.neutral / sentimentTotal) * 100) 
    : 0;
  
  // 숫자 포맷팅
  const formatNumber = (num: number) => {
    if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + "M";
    } else if (num >= 1000) {
      return (num / 1000).toFixed(1) + "K";
    } else {
      return num.toString();
    }
  };

  // 썸네일 로딩 에러 핸들링
  const [imgError, setImgError] = React.useState(false);
  const randomEmoji = React.useMemo(() => 
    snackEmojis[Math.floor(Math.random() * snackEmojis.length)], 
    []
  );
  
  return (
    <Card className="overflow-hidden transition-all hover:shadow-md">
      <div className="aspect-video relative overflow-hidden bg-slate-100">
        {!imgError ? (
          <img 
            src={video.thumbnailUrl} 
            alt={video.title} 
            className="w-full h-full object-cover"
            onError={() => setImgError(true)}
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center bg-amber-100 text-4xl">
            {randomEmoji}
          </div>
        )}
        {video.isShort && (
          <Badge className="absolute top-2 right-2 bg-red-500">
            Short
          </Badge>
        )}
      </div>
      <CardContent className="p-4">
        <h3 className="font-medium mb-2 line-clamp-2" title={video.title}>
          {video.title}
        </h3>
        
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <YoutubeIcon className="h-4 w-4" />
            <span>{formatNumber(video.views)} 조회수</span>
          </div>
          <div className="flex items-center gap-1 text-sm text-muted-foreground">
            <CalendarIcon className="h-3 w-3" />
            <span>{format(video.publishDate, "yyyy.MM.dd", { locale: ko })}</span>
          </div>
        </div>
        
        <div className="grid grid-cols-3 gap-2 text-xs font-medium mb-2">
          <div className="flex items-center gap-1">
            <span className="h-2 w-2 rounded-full bg-chart-positive"></span>
            <span className="text-chart-positive">좋아요 {formatNumber(video.likes)}</span>
          </div>
          <div className="flex items-center gap-1">
            <span className="h-2 w-2 rounded-full bg-chart-neutral"></span>
            <span>댓글 {formatNumber(video.comments)}</span>
          </div>
          <div className="flex items-center gap-1">
            {positivePercent > negativePercent ? (
              <>
                <ChevronUp className="h-3 w-3 text-[#4CAF50]" />
                <span className="text-[#4CAF50]">{positivePercent}%</span>
              </>
            ) : (
              <>
                <ChevronDown className="h-3 w-3 text-[#F06292]" />
                <span className="text-[#F06292]">{negativePercent}%</span>
              </>
            )}
          </div>
        </div>
        
        <div className="w-full h-2 bg-secondary rounded-full overflow-hidden">
          <div className="flex h-full">
            <div 
              className="bg-[#4CAF50] h-full" 
              style={{ width: `${positivePercent}%` }}
            />
            <div 
              className="bg-chart-neutral h-full" 
              style={{ width: `${neutralPercent}%` }}
            />
            <div 
              className="bg-[#F06292] h-full" 
              style={{ width: `${negativePercent}%` }}
            />
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default VideoCard;
