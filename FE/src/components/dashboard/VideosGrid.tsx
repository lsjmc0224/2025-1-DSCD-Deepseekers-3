import React from 'react';
import VideoCard from './VideoCard';
import { 
  Select, 
  SelectContent, 
  SelectItem, 
  SelectTrigger, 
  SelectValue 
} from "@/components/ui/select";

interface Video {
  id: string;
  title: string;
  thumbnail_url: string;
  views: number;
  likes: number;
  comments: number;
  publish_date: string; // ISO string
  sentiments: {
    positive: number;
    negative: number;
    neutral: number;
  };
  is_short: boolean;
}

interface VideosGridProps {
  title: string;
  videos: Video[];
  isShorts?: boolean;
}

const VideosGrid: React.FC<VideosGridProps> = ({ title, videos, isShorts }) => {
  const [sorting, setSorting] = React.useState<string>("views");

  const sortedVideos = [...videos].sort((a, b) => {
    switch (sorting) {
      case "views":
        return b.views - a.views;
      case "likes":
        return b.likes - a.likes;
      case "comments":
        return b.comments - a.comments;
      case "positiveRate": {
        const totalA = a.sentiments.positive + a.sentiments.negative + a.sentiments.neutral;
        const totalB = b.sentiments.positive + b.sentiments.negative + b.sentiments.neutral;
        const rateA = totalA > 0 ? a.sentiments.positive / totalA : 0;
        const rateB = totalB > 0 ? b.sentiments.positive / totalB : 0;
        return rateB - rateA;
      }
      case "negativeRate": {
        const totalA = a.sentiments.positive + a.sentiments.negative + a.sentiments.neutral;
        const totalB = b.sentiments.positive + b.sentiments.negative + b.sentiments.neutral;
        const rateA = totalA > 0 ? a.sentiments.negative / totalA : 0;
        const rateB = totalB > 0 ? b.sentiments.negative / totalB : 0;
        return rateB - rateA;
      }
      default:
        return 0;
    }
  });

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-semibold">{title}</h2>
        <Select onValueChange={setSorting} defaultValue={sorting}>
          <SelectTrigger className="w-[160px]">
            <SelectValue placeholder="정렬 기준" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="views">조회수</SelectItem>
            <SelectItem value="likes">좋아요</SelectItem>
            <SelectItem value="comments">댓글 수</SelectItem>
            <SelectItem value="positiveRate">긍정 비율</SelectItem>
            <SelectItem value="negativeRate">부정 비율</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {sortedVideos.length === 0 ? (
        <p className="text-center text-sm text-muted-foreground py-8">
          해당 기간을 기준으로 수집된 영상이 없습니다.
        </p>
      ) : (
        <div className="grid gap-4 grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5">
          {sortedVideos.map((video) => (
            <VideoCard 
              key={video.id} 
              video={video} 
            />
          ))}
        </div>
      )}
    </div>
  );
};

export default VideosGrid;
