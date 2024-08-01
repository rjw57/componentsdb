import React from "react";

import { useSignIn } from "./useSignIn";
import { makeClient } from "../apolloClient";

export const useApolloClient = () => {
  const { authenticatedFetch, authenticatedUser } = useSignIn();

  // The Apollo client is re-created when the authenticated fetch function changes.
  const client = React.useMemo(
    () => makeClient({ fetch: authenticatedFetch }),
    [authenticatedFetch],
  );

  // The client's cache is reset if the user changes.
  React.useEffect(() => {
    client.resetStore();
  }, [authenticatedUser?.id]);

  return client;
};

export default useApolloClient;
