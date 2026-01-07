import { Card, CardContent } from "@/components/ui/card";

interface StatsCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: React.ReactNode;
}

export function StatsCard({ title, value, subtitle, icon }: StatsCardProps) {
  return (
    <Card className="glass-card hover:scale-[1.02] transition-transform">
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-slate-500 mb-1">{title}</p>
            <p className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-gray-900 to-gray-700">
              {value}
            </p>
            {subtitle && <p className="text-xs text-slate-400 mt-2">{subtitle}</p>}
          </div>
          {icon && (
            <div className="p-3 bg-indigo-50 rounded-xl text-indigo-600">
              {icon}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}


