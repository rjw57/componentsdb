/* eslint-disable */
import * as types from './graphql';
import type { TypedDocumentNode as DocumentNode } from '@graphql-typed-document-node/core';

/**
 * Map of all GraphQL operations in the project.
 *
 * This map has several performance disadvantages:
 * 1. It is not tree-shakeable, so it will include all operations in the project.
 * 2. It is not minifiable, so the string of a GraphQL query will be multiple times inside the bundle.
 * 3. It does not support dead code elimination, so it will add unused operations.
 *
 * Therefore it is highly recommended to use the babel or swc plugin for production.
 */
const documents = {
    "\n  query componentSearch($search: String!) {\n    components(search: $search) {\n      nodes {\n        code\n        description\n        collections {\n          nodes {\n            count\n            drawer {\n              label\n              cabinet {\n                name\n              }\n            }\n          }\n        }\n      }\n    }\n  }\n": types.ComponentSearchDocument,
    "\n  mutation credentialsFromFederatedCredential($input: CredentialsFromFederatedCredentialInput!) {\n    auth {\n      credentialsFromFederatedCredential(input: $input) {\n        __typename\n        ... on UserCredentials {\n          user {\n            id\n            displayName\n            avatarUrl\n            email\n          }\n          accessToken\n          refreshToken\n          expiresIn\n        }\n        ... on AuthError {\n          error\n          detail\n        }\n      }\n    }\n  }\n": types.CredentialsFromFederatedCredentialDocument,
    "\n  query federatedIdentityProviders {\n    auth {\n      federatedIdentityProviders {\n        name\n        issuer\n        audience\n      }\n    }\n  }\n": types.FederatedIdentityProvidersDocument,
    "\n  mutation refreshCredentials($input: RefreshCredentialsInput!) {\n    auth {\n      refreshCredentials(input: $input) {\n        __typename\n        ... on UserCredentials {\n          user {\n            id\n            displayName\n            avatarUrl\n            email\n          }\n          accessToken\n          refreshToken\n          expiresIn\n        }\n        ... on AuthError {\n          error\n          detail\n        }\n      }\n    }\n  }\n": types.RefreshCredentialsDocument,
};

/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 *
 *
 * @example
 * ```ts
 * const query = graphql(`query GetUser($id: ID!) { user(id: $id) { name } }`);
 * ```
 *
 * The query argument is unknown!
 * Please regenerate the types.
 */
export function graphql(source: string): unknown;

/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "\n  query componentSearch($search: String!) {\n    components(search: $search) {\n      nodes {\n        code\n        description\n        collections {\n          nodes {\n            count\n            drawer {\n              label\n              cabinet {\n                name\n              }\n            }\n          }\n        }\n      }\n    }\n  }\n"): (typeof documents)["\n  query componentSearch($search: String!) {\n    components(search: $search) {\n      nodes {\n        code\n        description\n        collections {\n          nodes {\n            count\n            drawer {\n              label\n              cabinet {\n                name\n              }\n            }\n          }\n        }\n      }\n    }\n  }\n"];
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "\n  mutation credentialsFromFederatedCredential($input: CredentialsFromFederatedCredentialInput!) {\n    auth {\n      credentialsFromFederatedCredential(input: $input) {\n        __typename\n        ... on UserCredentials {\n          user {\n            id\n            displayName\n            avatarUrl\n            email\n          }\n          accessToken\n          refreshToken\n          expiresIn\n        }\n        ... on AuthError {\n          error\n          detail\n        }\n      }\n    }\n  }\n"): (typeof documents)["\n  mutation credentialsFromFederatedCredential($input: CredentialsFromFederatedCredentialInput!) {\n    auth {\n      credentialsFromFederatedCredential(input: $input) {\n        __typename\n        ... on UserCredentials {\n          user {\n            id\n            displayName\n            avatarUrl\n            email\n          }\n          accessToken\n          refreshToken\n          expiresIn\n        }\n        ... on AuthError {\n          error\n          detail\n        }\n      }\n    }\n  }\n"];
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "\n  query federatedIdentityProviders {\n    auth {\n      federatedIdentityProviders {\n        name\n        issuer\n        audience\n      }\n    }\n  }\n"): (typeof documents)["\n  query federatedIdentityProviders {\n    auth {\n      federatedIdentityProviders {\n        name\n        issuer\n        audience\n      }\n    }\n  }\n"];
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "\n  mutation refreshCredentials($input: RefreshCredentialsInput!) {\n    auth {\n      refreshCredentials(input: $input) {\n        __typename\n        ... on UserCredentials {\n          user {\n            id\n            displayName\n            avatarUrl\n            email\n          }\n          accessToken\n          refreshToken\n          expiresIn\n        }\n        ... on AuthError {\n          error\n          detail\n        }\n      }\n    }\n  }\n"): (typeof documents)["\n  mutation refreshCredentials($input: RefreshCredentialsInput!) {\n    auth {\n      refreshCredentials(input: $input) {\n        __typename\n        ... on UserCredentials {\n          user {\n            id\n            displayName\n            avatarUrl\n            email\n          }\n          accessToken\n          refreshToken\n          expiresIn\n        }\n        ... on AuthError {\n          error\n          detail\n        }\n      }\n    }\n  }\n"];

export function graphql(source: string) {
  return (documents as any)[source] ?? {};
}

export type DocumentType<TDocumentNode extends DocumentNode<any, any>> = TDocumentNode extends DocumentNode<  infer TType,  any>  ? TType  : never;