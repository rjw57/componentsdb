import { ApolloClient, InMemoryCache } from "@apollo/client";

// A shared cache for all clients. Make sure to call client.resetStore() when changing user.
const cache = new InMemoryCache();

export interface MakeClientOptions {
  accessToken?: string;
}

export const makeClient = (options?: MakeClientOptions) => {
  const { accessToken } = { ...options };
  return new ApolloClient({
    cache,
    uri: "/graphql",
    headers: accessToken ? { Authorization: `Bearer ${accessToken}` } : {},
  });
};

export const unauthenticatedClient = makeClient();
