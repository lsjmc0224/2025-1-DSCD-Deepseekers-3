
import React, { useState, useEffect } from 'react';
import { 
  Select, 
  SelectContent, 
  SelectItem, 
  SelectTrigger, 
  SelectValue 
} from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { Calendar } from "@/components/ui/calendar";
import { 
  Popover, 
  PopoverContent, 
  PopoverTrigger 
} from "@/components/ui/popover";
import { format } from "date-fns";
import { ko } from "date-fns/locale";
import { cn } from "@/lib/utils";
import { CalendarIcon } from "lucide-react";
import { Badge } from "@/components/ui/badge";

interface DateRange {
  from: Date;
  to?: Date;
}

interface DashboardFiltersProps {
  onChannelChange: (channel: string) => void;
  onPeriodChange: (period: string) => void;
  onDateChange: (dateRange: DateRange) => void;
  showChannelFilter?: boolean;
}

const DashboardFilters: React.FC<DashboardFiltersProps> = ({ 
  onChannelChange, 
  onPeriodChange, 
  onDateChange,
  showChannelFilter = true
}) => {
  const [date, setDate] = useState<DateRange | undefined>({
    from: new Date(new Date().setDate(new Date().getDate() - 7)),
    to: new Date()
  });
  
  const [selectedChannel, setSelectedChannel] = useState<string>("전체");
  const [selectedPeriod, setSelectedPeriod] = useState<string>("최근 7일");

  const handleChannelSelect = (value: string) => {
    setSelectedChannel(value);
    onChannelChange(value);
  };

  const handlePeriodSelect = (value: string) => {
    setSelectedPeriod(value);
    
    // 날짜 범위 설정
    const today = new Date();
    let fromDate = new Date();
    
    switch(value) {
      case "최근 7일":
        fromDate.setDate(today.getDate() - 7);
        break;
      case "최근 14일":
        fromDate.setDate(today.getDate() - 14);
        break;
      case "최근 30일":
        fromDate.setDate(today.getDate() - 30);
        break;
      default:
        // 사용자 지정인 경우 현재 날짜 범위 유지
        return;
    }
    
    const newRange = {
      from: fromDate,
      to: today
    };
    
    setDate(newRange);
    onDateChange(newRange);
    onPeriodChange(value);
  };

  const handleDateChange = (newDate: DateRange | undefined) => {
    if (newDate) {
      setDate(newDate);
      if (newDate.from) {
        // 사용자 지정 기간으로 설정
        setSelectedPeriod("사용자 지정");
        onPeriodChange("사용자 지정");
        onDateChange(newDate);
      }
    }
  };

  // 초기 로드 시 날짜 범위 전달
  useEffect(() => {
    if (date) {
      onDateChange(date);
    }
  }, []);

  return (
    <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between w-full">
      <div className="flex flex-col sm:flex-row gap-2 items-start sm:items-center">
        <h1 className="text-2xl font-bold">데이터 분석</h1>
        {selectedChannel && selectedChannel !== "전체" && showChannelFilter && (
          <Badge variant="outline" className="ml-2">
            {selectedChannel}
          </Badge>
        )}
      </div>
      
      <div className="flex flex-wrap gap-2 justify-end">
        {showChannelFilter && (
          <Select onValueChange={handleChannelSelect} defaultValue={selectedChannel}>
            <SelectTrigger className="w-[110px]">
              <SelectValue placeholder="채널 선택" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="전체">전체</SelectItem>
              <SelectItem value="유튜브">유튜브</SelectItem>
              <SelectItem value="틱톡">틱톡</SelectItem>
              <SelectItem value="커뮤니티">커뮤니티</SelectItem>
            </SelectContent>
          </Select>
        )}
        
        <Select onValueChange={handlePeriodSelect} defaultValue={selectedPeriod}>
          <SelectTrigger className="w-[130px]">
            <SelectValue placeholder="기간 선택" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="최근 7일">최근 7일</SelectItem>
            <SelectItem value="최근 14일">최근 14일</SelectItem>
            <SelectItem value="최근 30일">최근 30일</SelectItem>
            <SelectItem value="사용자 지정">사용자 지정</SelectItem>
          </SelectContent>
        </Select>
        
        <Popover>
          <PopoverTrigger asChild>
            <Button
              variant="outline"
              className="justify-start text-left w-[220px]"
            >
              <CalendarIcon className="mr-2 h-4 w-4" />
              {date?.from ? (
                date.to ? (
                  <>
                    {format(date.from, "yyyy.MM.dd", { locale: ko })} ~{" "}
                    {format(date.to, "yyyy.MM.dd", { locale: ko })}
                  </>
                ) : (
                  format(date.from, "yyyy.MM.dd", { locale: ko })
                )
              ) : (
                <span>날짜 선택</span>
              )}
            </Button>
          </PopoverTrigger>
          <PopoverContent className="w-auto p-0" align="end">
            <Calendar
              mode="range"
              locale={ko}
              selected={date}
              onSelect={handleDateChange}
              initialFocus
              className={cn("p-3 pointer-events-auto")}
            />
          </PopoverContent>
        </Popover>
      </div>
    </div>
  );
};

export default DashboardFilters;
