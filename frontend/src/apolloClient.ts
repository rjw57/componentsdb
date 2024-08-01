import { ApolloClient, HttpLink, InMemoryCache } from "@apollo/client";
import { graphQLUrl } from "./config";

export interface MakeClientOptions {
  fetch?: (info: RequestInfo | URL, init?: RequestInit) => Promise<Response>;
  useIndependentCache?: boolean;
}

const sharedCache = new InMemoryCache();

export const makeClient = (options?: MakeClientOptions) => {
  const { fetch, useIndependentCache = false } = { ...(options ?? {}) };
  return new ApolloClient({
    cache: useIndependentCache ? new InMemoryCache() : sharedCache,
    link: new HttpLink({
      uri: graphQLUrl,
      fetch,
    }),
  });
};

// An unauthenticated Apollo client which uses an independent cache.
export const unauthenticatedClient = makeClient({ useIndependentCache: true });
