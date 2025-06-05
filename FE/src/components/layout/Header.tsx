
import React, { useState } from 'react';
import { SidebarTrigger } from "@/components/ui/sidebar";
import { Button } from "@/components/ui/button";
import { Moon, Sun } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { Input } from "@/components/ui/input";

const Header: React.FC = () => {
  const { toast } = useToast();
  const [productSearch, setProductSearch] = useState("");

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

  return (
    <header className="bg-background border-b shadow-sm z-10">
      <div className="flex h-16 items-center px-4 md:px-6 justify-between">
        <div className="flex items-center">
          <SidebarTrigger className="mr-2 md:hidden" />
          <span className="md:hidden font-medium">SNATCH</span>
        </div>
        
        <div className="hidden md:flex justify-center flex-1 max-w-xs">
          <Input 
            type="text"
            placeholder="제품명을 입력하세요"
            value={productSearch}
            onChange={handleSearchChange}
            className="w-full"
          />
        </div>
        
        <div className="flex items-center gap-2">
          <Button variant="ghost" size="icon" onClick={handleThemeToggle}>
            <Sun className="h-5 w-5 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
            <Moon className="absolute h-5 w-5 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
            <span className="sr-only">테마 전환</span>
          </Button>
        </div>
      </div>
      
      {/* Mobile search bar for small screens */}
      <div className="md:hidden px-4 pb-4">
        <Input 
          type="text"
          placeholder="제품명을 입력하세요"
          value={productSearch}
          onChange={handleSearchChange}
          className="w-full"
        />
      </div>
    </header>
  );
};

export default Header;
