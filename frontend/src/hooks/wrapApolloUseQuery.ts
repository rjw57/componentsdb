import { useQuery } from "@apollo/client";
import type { QueryHookOptions, OperationVariables } from "@apollo/client";
import type { TypedDocumentNode } from "@graphql-typed-document-node/core";

export const wrapApolloUseQuery =
  <TData, TVariables extends OperationVariables>(query: TypedDocumentNode<TData, TVariables>) =>
  (options?: QueryHookOptions<TData, TVariables>) =>
    useQuery(query, options);

export default wrapApolloUseQuery;
