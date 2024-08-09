import React from "react";
import { TextInput, Button } from "flowbite-react";
import { HiSearch as SearchIcon } from "react-icons/hi";

import SearchResults from "./SearchResults";
import useComponentSearch from "../hooks/useComponentSearch";
import useApolloClient from "../hooks/useApolloClient";
import { useDebounceValue } from "usehooks-ts";

export const Search: React.FC = () => {
  const [searchText, setSearchText] = React.useState<string>("");
  const [currentSearch, setCurrentSearch] = React.useState<string>();
  const [debouncedLoading, setDebouncedLoading] = useDebounceValue(false, 200);
  const canSearch = searchText.length > 0;
  const client = useApolloClient();

  const { data, loading } = useComponentSearch({
    client,
    variables: { search: `${currentSearch}` },
    skip: !currentSearch,
  });

  React.useEffect(() => {
    setDebouncedLoading(loading);
  }, [loading, setDebouncedLoading]);

  const results = (data?.components.nodes ?? [])
    .map(({ code, description, collections }) =>
      collections.nodes
        .toSorted(({ count: countA }, { count: countB }) => countB - countA)
        .map(
          ({
            count,
            drawer: {
              label: drawerLabel,
              cabinet: { name: drawerCabinetName },
            },
          }) => ({
            code,
            description,
            count,
            drawerLabel,
            drawerCabinetName,
          }),
        ),
    )
    .flat();

  return (
    <div className="space-y-8">
      <form
        onSubmit={(e) => {
          if (canSearch) {
            setCurrentSearch(searchText);
          }
          e.preventDefault();
        }}
        className="flex flex-row gap-4"
      >
        <TextInput
          className="flex-1"
          shadow
          type="text"
          autoFocus
          placeholder="Find something"
          value={searchText}
          icon={SearchIcon}
          onChange={({ target: { value } }) => {
            setSearchText(value);
          }}
        />
        <Button
          type="submit"
          isProcessing={debouncedLoading}
          disabled={!canSearch || debouncedLoading}
        >
          Search
        </Button>
      </form>

      <SearchResults results={results} />
    </div>
  );
};

export default Search;
