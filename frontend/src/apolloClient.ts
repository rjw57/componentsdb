import { ApolloClient, HttpLink, InMemoryCache } from "@apollo/client";

// A shared cache for all clients. Make sure to call client.resetStore() when changing user.
const cache = new InMemoryCache();

export interface MakeClientOptions {
  fetch?: (info: RequestInfo | URL, init?: RequestInit) => Promise<Response>;
}

export const makeClient = (options?: MakeClientOptions) => {
  const { fetch } = { ...(options ?? {}) };
  return new ApolloClient({
    cache,
    link: new HttpLink({
      uri: "/graphql",
      fetch,
    }),
  });
};

export const unauthenticatedClient = makeClient();
