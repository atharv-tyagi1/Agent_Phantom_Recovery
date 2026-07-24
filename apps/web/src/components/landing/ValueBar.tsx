"use client";

export function ValueBar() {
  return (
    <div className="border-b border-[#524533]/20 bg-[#0e0e0e]/80 backdrop-blur-sm sticky top-16 z-40 overflow-x-auto hide-scrollbar">
      <div className="max-w-[1440px] mx-auto px-6 md:px-10 py-4 flex gap-8 items-center justify-start md:justify-center min-w-max">
        <div className="flex items-center gap-2 text-[#d7c4ac] font-mono text-xs">
          <span className="material-symbols-outlined text-[#ffb000] text-base">psychology</span>
          <span>Autonomous Planning</span>
        </div>
        <div className="w-1 h-1 rounded-full bg-[#524533]/50" />
        <div className="flex items-center gap-2 text-[#d7c4ac] font-mono text-xs">
          <span className="material-symbols-outlined text-[#ffb000] text-base">troubleshoot</span>
          <span>Repository Analysis</span>
        </div>
        <div className="w-1 h-1 rounded-full bg-[#524533]/50" />
        <div className="flex items-center gap-2 text-[#d7c4ac] font-mono text-xs">
          <span className="material-symbols-outlined text-[#ffb000] text-base">loop</span>
          <span>Verification Loop</span>
        </div>
        <div className="w-1 h-1 rounded-full bg-[#524533]/50" />
        <div className="flex items-center gap-2 text-[#d7c4ac] font-mono text-xs">
          <span className="material-symbols-outlined text-[#ffb000] text-base">security</span>
          <span>Rollback Safety</span>
        </div>
      </div>
    </div>
  );
}
