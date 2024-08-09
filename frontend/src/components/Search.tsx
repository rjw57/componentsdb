import React from "react";
import { TextInput } from "flowbite-react";
import { HiSearch as SearchIcon } from "react-icons/hi";
import { useDebounceValue } from "usehooks-ts";

import SearchResults from "./SearchResults";
import useComponentSearch from "../hooks/useComponentSearch";
import useApolloClient from "../hooks/useApolloClient";

export const Search: React.FC = () => {
  const [searchText, setSearchText] = React.useState<string>("");
  const [debouncedSearchText, setDebouncedSearchText] = useDebounceValue("", 500);
  const shouldSearch = debouncedSearchText.length >= 2;
  const client = useApolloClient();

  React.useEffect(() => {
    setDebouncedSearchText(searchText);
  }, [searchText, setDebouncedSearchText]);

  const { data } = useComponentSearch({
    client,
    variables: { search: debouncedSearchText },
    skip: !shouldSearch,
  });

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
      <TextInput
        shadow
        type="text"
        sizing="lg"
        autoFocus
        placeholder="Find something"
        icon={SearchIcon}
        value={searchText}
        onChange={({ target: { value } }) => {
          setSearchText(value);
        }}
      />

      <SearchResults results={results} />
    </div>
  );
};

export default Search;
