import { Upload } from "lucide-react";

interface GenerationFieldsProps {
  generation: number;
  parentName: string;
  grandparentName: string;
  greatGrandparentName: string;
  onGenerationChange: (val: number) => void;
  onParentNameChange: (val: string) => void;
  onGrandparentNameChange: (val: string) => void;
  onGreatGrandparentNameChange: (val: string) => void;
}

export default function GenerationFields({
  generation,
  parentName,
  grandparentName,
  greatGrandparentName,
  onGenerationChange,
  onParentNameChange,
  onGrandparentNameChange,
  onGreatGrandparentNameChange,
}: GenerationFieldsProps) {
  return (
    <div className="space-y-4">
      <div>
        <label className="block text-xs font-medium uppercase tracking-widest text-muted-foreground mb-2">
          Generation
        </label>
        <select
          value={generation}
          onChange={(e) => onGenerationChange(Number(e.target.value))}
          className="w-full px-4 py-3 bg-secondary border border-border rounded-lg text-foreground font-body focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all"
        >
          {[1, 2, 3, 4, 5, 6].map((n) => (
            <option key={n} value={n}>
              {n}{n === 1 ? "st" : n === 2 ? "nd" : n === 3 ? "rd" : "th"} Generation
            </option>
          ))}
        </select>
      </div>

      {generation >= 3 && (
        <div className="panel-enter">
          <label className="block text-xs font-medium uppercase tracking-widest text-muted-foreground mb-2">
            Parent's Name
          </label>
          <input
            type="text"
            value={parentName}
            onChange={(e) => onParentNameChange(e.target.value)}
            placeholder="Enter parent's name"
            className="w-full px-4 py-3 bg-secondary border border-border rounded-lg text-foreground font-body placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all"
          />
        </div>
      )}

      {generation >= 4 && (
        <div className="panel-enter">
          <label className="block text-xs font-medium uppercase tracking-widest text-muted-foreground mb-2">
            Grandparent's Name
          </label>
          <input
            type="text"
            value={grandparentName}
            onChange={(e) => onGrandparentNameChange(e.target.value)}
            placeholder="Enter grandparent's name"
            className="w-full px-4 py-3 bg-secondary border border-border rounded-lg text-foreground font-body placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all"
          />
        </div>
      )}

      {generation >= 5 && (
        <div className="panel-enter">
          <label className="block text-xs font-medium uppercase tracking-widest text-muted-foreground mb-2">
            Great-Grandparent's Name
          </label>
          <input
            type="text"
            value={greatGrandparentName}
            onChange={(e) => onGreatGrandparentNameChange(e.target.value)}
            placeholder="Enter great-grandparent's name"
            className="w-full px-4 py-3 bg-secondary border border-border rounded-lg text-foreground font-body placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all"
          />
        </div>
      )}
    </div>
  );
}
