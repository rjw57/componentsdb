import { ApolloClient, HttpLink, InMemoryCache } from "@apollo/client";

export interface MakeClientOptions {
  fetch?: (info: RequestInfo | URL, init?: RequestInit) => Promise<Response>;
}

export const makeClient = (options?: MakeClientOptions) => {
  const { fetch } = { ...(options ?? {}) };
  return new ApolloClient({
    cache: new InMemoryCache(),
    link: new HttpLink({
      uri: "/graphql",
      fetch,
    }),
  });
};

// An unauthenticated Apollo client which uses an independent cached.
export const unauthenticatedClient = makeClient();
