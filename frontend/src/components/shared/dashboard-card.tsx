import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";

type DashboardCardProps = {
  title: string;
  description?: string;
  icon: React.ReactNode;
  children: React.ReactNode;
  className?: string;
  cardContentClassName?: string;
};

export function DashboardCard({ title, description, icon, children, className, cardContentClassName }: DashboardCardProps) {
  return (
    <Card className={cn(
        "bg-black/40 border-primary/30 backdrop-blur-sm transition-all duration-300 hover:border-accent",
        "flex flex-col",
        className
    )}>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2 px-3 sm:px-6">
        <div className="flex-1">
          <CardTitle className="text-sm sm:text-base font-headline font-medium text-primary-foreground/90 uppercase tracking-widest">{title}</CardTitle>
          {description && <CardDescription className="text-xs text-muted-foreground">{description}</CardDescription>}
        </div>
        <div className="text-accent h-5 w-5 sm:h-6 sm:w-6">{icon}</div>
      </CardHeader>
      <CardContent className={cn("flex-grow pt-3 sm:pt-4 px-3 sm:px-6", cardContentClassName)}>
        {children}
      </CardContent>
    </Card>
  );
}
