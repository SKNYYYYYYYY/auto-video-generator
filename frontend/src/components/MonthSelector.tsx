// components/MonthSelector.tsx
import { useState, useRef, useEffect } from "react";
import { createPortal } from "react-dom";
import { ChevronDown } from "lucide-react";

const MONTHS = [
  "January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December",
];

interface MonthSelectorProps {
  value: string;
  onChange: (month: string) => void;
  placeholder?: string;
  className?: string;
  onMonthChange?: (month: string) => void;
}

export const MonthSelector = ({ 
  value, 
  onChange, 
  placeholder = "Select month",
  className = "",
  onMonthChange
}: MonthSelectorProps) => {
  const [isOpen, setIsOpen] = useState(false);
  const [dropdownStyle, setDropdownStyle] = useState({});
  const buttonRef = useRef<HTMLButtonElement>(null);

  const handleMonthSelect = (month: string) => {
    onChange(month);
    if (onMonthChange) {
      onMonthChange(month);
    }
    setIsOpen(false);
  };

  // Calculate dropdown position when opened
  useEffect(() => {
    if (isOpen && buttonRef.current) {
      const rect = buttonRef.current.getBoundingClientRect();
      setDropdownStyle({
        position: 'fixed',
        top: rect.bottom + window.scrollY + 8,
        left: rect.left + window.scrollX,
        width: rect.width,
        zIndex: 99999,
      });
    }
  }, [isOpen]);

  // Close on escape key
  useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setIsOpen(false);
    };
    if (isOpen) {
      document.addEventListener('keydown', handleEsc);
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }
    return () => {
      document.removeEventListener('keydown', handleEsc);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  return (
    <div className={`relative ${className}`}>
      {/* Trigger button */}
      <button
        ref={buttonRef}
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="
          w-full px-4 py-3 bg-secondary border border-border
          rounded-xl text-left flex justify-between items-center
          hover:border-primary/40 transition-all relative z-10
        "
      >
        <span className={value ? "text-foreground" : "text-muted-foreground"}>
          {value || placeholder}
        </span>
        <ChevronDown className={`w-4 h-4 transition-transform duration-200 ${isOpen ? "rotate-180" : ""}`} />
      </button>

      {/* Dropdown rendered via Portal */}
      {isOpen && createPortal(
        <div>
          {/* Backdrop */}
          <div 
            className="fixed inset-0 bg-black/20 z-[99998]"
            onClick={() => setIsOpen(false)}
          />
          
          {/* Dropdown menu */}
          <div 
            className="bg-card border border-border rounded-xl shadow-xl animate-in fade-in zoom-in-95 duration-200"
            style={dropdownStyle}
          >
            <div className="p-3 max-h-[300px] overflow-y-auto">
              <div className="grid grid-cols-3 gap-2">
                {MONTHS.map((m) => (
                  <button
                    key={m}
                    type="button"
                    onClick={() => handleMonthSelect(m)}
                    className={`
                      px-2 py-2 rounded-lg text-sm border transition-all duration-150
                      ${value === m
                        ? "bg-primary text-white border-primary shadow-sm"
                        : "bg-secondary hover:border-primary/40 hover:bg-secondary/80"
                      }
                    `}
                  >
                    {m.slice(0, 3)}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>,
        document.body
      )}
    </div>
  );
};