"use client";

import { useState } from "react";
import { Calendar, Filter, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { Badge } from "@/components/ui/badge";

export interface SearchFilters {
  type?: 'case' | 'statute' | 'document' | 'precedent';
  date_from?: string;
  date_to?: string;
  limit?: number;
  offset?: number;
}

interface SearchFiltersProps {
  filters: SearchFilters;
  onFiltersChange: (filters: SearchFilters) => void;
  onApplyFilters: () => void;
}

export function SearchFiltersComponent({
  filters,
  onFiltersChange,
  onApplyFilters
}: SearchFiltersProps) {
  const [isOpen, setIsOpen] = useState(false);

  const handleFilterChange = (key: keyof SearchFilters, value: any) => {
    onFiltersChange({
      ...filters,
      [key]: value || undefined,
    });
  };

  const clearFilters = () => {
    onFiltersChange({});
  };

  const hasActiveFilters = Object.keys(filters).some(key =>
    filters[key as keyof SearchFilters] !== undefined &&
    filters[key as keyof SearchFilters] !== ''
  );

  const getActiveFiltersCount = () => {
    return Object.keys(filters).filter(key =>
      filters[key as keyof SearchFilters] !== undefined &&
      filters[key as keyof SearchFilters] !== ''
    ).length;
  };

  return (
    <div className="flex items-center gap-2 mb-4">
      <Popover open={isOpen} onOpenChange={setIsOpen}>
        <PopoverTrigger asChild>
          <Button variant="outline" className="relative">
            <Filter className="h-4 w-4 mr-2" />
            Filters
            {hasActiveFilters && (
              <Badge
                variant="secondary"
                className="ml-2 h-5 w-5 p-0 flex items-center justify-center text-xs"
              >
                {getActiveFiltersCount()}
              </Badge>
            )}
          </Button>
        </PopoverTrigger>
        <PopoverContent className="w-80 p-4">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h4 className="font-medium">Search Filters</h4>
              {hasActiveFilters && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={clearFilters}
                  className="h-auto p-1 text-xs"
                >
                  Clear all
                </Button>
              )}
            </div>

            {/* Document Type Filter */}
            <div className="space-y-2">
              <Label>Document Type</Label>
              <Select
                value={filters.type || ''}
                onValueChange={(value) => handleFilterChange('type', value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="All types" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">All types</SelectItem>
                  <SelectItem value="case">Cases</SelectItem>
                  <SelectItem value="statute">Statutes</SelectItem>
                  <SelectItem value="document">Documents</SelectItem>
                  <SelectItem value="precedent">Precedents</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Date Range Filter */}
            <div className="space-y-2">
              <Label>Date Range</Label>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <Label htmlFor="date-from" className="text-xs text-gray-600">
                    From
                  </Label>
                  <Input
                    id="date-from"
                    type="date"
                    value={filters.date_from || ''}
                    onChange={(e) => handleFilterChange('date_from', e.target.value)}
                  />
                </div>
                <div>
                  <Label htmlFor="date-to" className="text-xs text-gray-600">
                    To
                  </Label>
                  <Input
                    id="date-to"
                    type="date"
                    value={filters.date_to || ''}
                    onChange={(e) => handleFilterChange('date_to', e.target.value)}
                  />
                </div>
              </div>
            </div>

            {/* Results Limit */}
            <div className="space-y-2">
              <Label>Results per page</Label>
              <Select
                value={filters.limit?.toString() || '20'}
                onValueChange={(value) => handleFilterChange('limit', parseInt(value))}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="10">10</SelectItem>
                  <SelectItem value="20">20</SelectItem>
                  <SelectItem value="50">50</SelectItem>
                  <SelectItem value="100">100</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="flex gap-2 pt-2">
              <Button
                onClick={() => {
                  onApplyFilters();
                  setIsOpen(false);
                }}
                className="flex-1 bg-black hover:bg-black/90 text-white"
              >
                Apply Filters
              </Button>
            </div>
          </div>
        </PopoverContent>
      </Popover>

      {/* Active Filters Display */}
      {hasActiveFilters && (
        <div className="flex flex-wrap gap-2">
          {filters.type && (
            <Badge variant="secondary" className="flex items-center gap-1">
              Type: {filters.type}
              <X
                className="h-3 w-3 cursor-pointer"
                onClick={() => handleFilterChange('type', undefined)}
              />
            </Badge>
          )}
          {filters.date_from && (
            <Badge variant="secondary" className="flex items-center gap-1">
              From: {new Date(filters.date_from).toLocaleDateString()}
              <X
                className="h-3 w-3 cursor-pointer"
                onClick={() => handleFilterChange('date_from', undefined)}
              />
            </Badge>
          )}
          {filters.date_to && (
            <Badge variant="secondary" className="flex items-center gap-1">
              To: {new Date(filters.date_to).toLocaleDateString()}
              <X
                className="h-3 w-3 cursor-pointer"
                onClick={() => handleFilterChange('date_to', undefined)}
              />
            </Badge>
          )}
          {filters.limit && filters.limit !== 20 && (
            <Badge variant="secondary" className="flex items-center gap-1">
              Limit: {filters.limit}
              <X
                className="h-3 w-3 cursor-pointer"
                onClick={() => handleFilterChange('limit', undefined)}
              />
            </Badge>
          )}
        </div>
      )}
    </div>
  );
}
