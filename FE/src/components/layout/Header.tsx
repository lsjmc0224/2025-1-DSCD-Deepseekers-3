import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { SidebarTrigger } from "@/components/ui/sidebar";
import { Button } from "@/components/ui/button";
import { Moon, Sun, Search } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { Input } from "@/components/ui/input";

const Header: React.FC = () => {
  const { toast } = useToast();
  const [productSearch, setProductSearch] = useState("");
  const navigate = useNavigate();

  const handleThemeToggle = () => {
    document.documentElement.classList.toggle('dark');
    toast({
      title: document.documentElement.classList.contains('dark')
        ? "다크 모드가 활성화되었습니다."
        : "라이트 모드가 활성화되었습니다.",
      duration: 2000,
    });
  };

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setProductSearch(e.target.value);
  };

  const handleSearch = () => {
    const trimmed = productSearch.trim();
    if (trimmed) {
      navigate(`/summary/${encodeURIComponent(trimmed)}`);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') handleSearch();
  };

  return (
    <header className="bg-background border-b shadow-sm z-10">
      <div className="flex h-16 items-center px-4 md:px-6 justify-between">
        <div className="flex items-center">
          <SidebarTrigger className="mr-2 md:hidden" />
          <span className="md:hidden font-medium">SNATCH</span>
        </div>

        {/* Desktop 검색창 */}
        <div className="hidden md:flex justify-center flex-1 max-w-md gap-2">
          <Input
            type="text"
            placeholder="제품명을 입력하세요"
            value={productSearch}
            onChange={handleSearchChange}
            onKeyDown={handleKeyPress}
            className="w-full"
          />
          <Button variant="outline" onClick={handleSearch}>
            <Search className="w-4 h-4 mr-1" />
            검색
          </Button>
        </div>

        <div className="flex items-center gap-2">
          <Button variant="ghost" size="icon" onClick={handleThemeToggle}>
            <Sun className="h-5 w-5 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
            <Moon className="absolute h-5 w-5 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
            <span className="sr-only">테마 전환</span>
          </Button>
        </div>
      </div>

      {/* Mobile 검색창 */}
      <div className="md:hidden px-4 pb-4 flex gap-2">
        <Input
          type="text"
          placeholder="제품명을 입력하세요"
          value={productSearch}
          onChange={handleSearchChange}
          onKeyDown={handleKeyPress}
          className="w-full"
        />
        <Button variant="outline" onClick={handleSearch}>
          <Search className="w-4 h-4" />
        </Button>
      </div>
    </header>
  );
};

export default Header;
