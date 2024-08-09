import React from "react";

import { Card } from "flowbite-react";

export interface SearchResult {
  count: number;
  code: string;
  description?: string | null;
  drawerLabel: string;
  drawerCabinetName: string;
}

export interface SearchResultCardProps {
  result: SearchResult;
}

export const SearchResultCard: React.FC<SearchResultCardProps> = ({
  result: { count, code, description, drawerLabel, drawerCabinetName },
}) => (
  <Card>
    <div className="space-y-2">
      <div className="flex flex-row gap-4 items-start justify-between">
        <div className="truncate">
          <div className="text-xl font-medium text-gray-900 dark:text-white truncate">
            {count} &times; {code}
          </div>
          {description && (
            <div className="text-sm text-gray-500 dark:text-gray-400 truncate">{description}</div>
          )}
        </div>
        <div className="text-xl font-medium text-gray-900 dark:text-white text-right">
          {drawerLabel}
          <div className="text-sm text-gray-400 dark:text-gray-600">{drawerCabinetName}</div>
        </div>
      </div>
    </div>
  </Card>
);

export interface SearchResultsProps {
  results?: SearchResult[];
}

export const SearchResults: React.FC<SearchResultsProps> = ({ results = [] }) => {
  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
      {results.map((result, idx) => (
        <SearchResultCard key={idx} result={result} />
      ))}
    </div>
  );
};

export default SearchResults;
