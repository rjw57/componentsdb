import { MutationHookOptions, useMutation, OperationVariables } from "@apollo/client";
import { TypedDocumentNode } from "@graphql-typed-document-node/core";

export const wrapApolloUseMutation =
  <TData, TVariables extends OperationVariables>(query: TypedDocumentNode<TData, TVariables>) =>
  (options?: MutationHookOptions<TData, TVariables>) =>
    useMutation(query, options);

export default wrapApolloUseMutation;
