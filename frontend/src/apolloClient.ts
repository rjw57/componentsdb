import { ApolloClient, InMemoryCache } from "@apollo/client";

export interface MakeClientOptions {
  accessToken?: string;
}

export const makeClient = (options?: MakeClientOptions) => {
  const { accessToken } = { ...options };
  return new ApolloClient({
    cache: new InMemoryCache(),
    uri: "/graphql",
    headers: accessToken ? { Authorization: `Bearer ${accessToken}` } : {},
  });
};

export const unauthenticatedClient = makeClient();
