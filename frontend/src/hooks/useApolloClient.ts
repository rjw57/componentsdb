import React from "react";

import { useAuth } from "./useAuth";
import { makeClient } from "../apolloClient";

export const useApolloClient = () => {
  const { user, credentials } = useAuth() ?? {};

  // The Apollo client is re-created when the access token changes.
  const client = React.useMemo(
    () =>
      makeClient({
        accessToken: credentials?.accessToken,
      }),
    [credentials?.accessToken],
  );

  // The client's cache is reset if the user changes.
  React.useEffect(() => {
    client.resetStore();
    // We disable the eslint warning because we *want* client to be able to change without
    // triggering the effect. We *only* want the effect to be triggered if the user changes.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user?.id]);

  return client;
};

export default useApolloClient;
