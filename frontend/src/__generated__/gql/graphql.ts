/* eslint-disable */
import type { TypedDocumentNode as DocumentNode } from '@graphql-typed-document-node/core';
export type Maybe<T> = T | null;
export type InputMaybe<T> = Maybe<T>;
export type Exact<T extends { [key: string]: unknown }> = { [K in keyof T]: T[K] };
export type MakeOptional<T, K extends keyof T> = Omit<T, K> & { [SubKey in K]?: Maybe<T[SubKey]> };
export type MakeMaybe<T, K extends keyof T> = Omit<T, K> & { [SubKey in K]: Maybe<T[SubKey]> };
export type MakeEmpty<T extends { [key: string]: unknown }, K extends keyof T> = { [_ in K]?: never };
export type Incremental<T> = T | { [P in keyof T]?: P extends ' $fragmentName' | '__typename' ? T[P] : never };
/** All built-in and custom scalars, mapped to their actual values */
export type Scalars = {
  ID: { input: string; output: string; }
  String: { input: string; output: string; }
  Boolean: { input: boolean; output: boolean; }
  Int: { input: number; output: number; }
  Float: { input: number; output: number; }
};

export type AuthCredentialsResponse = AuthError | UserCredentials;

export type AuthError = {
  __typename?: 'AuthError';
  detail: Scalars['String']['output'];
  error: AuthErrorType;
};

export enum AuthErrorType {
  InvalidCredential = 'INVALID_CREDENTIAL',
  InvalidFederatedCredential = 'INVALID_FEDERATED_CREDENTIAL',
  NoSuchFederatedIdentityProvider = 'NO_SUCH_FEDERATED_IDENTITY_PROVIDER',
  UserAlreadySignedUp = 'USER_ALREADY_SIGNED_UP',
  UserNotSignedUp = 'USER_NOT_SIGNED_UP'
}

export type AuthMutations = {
  __typename?: 'AuthMutations';
  credentialsFromFederatedCredential: AuthCredentialsResponse;
  refreshCredentials: AuthCredentialsResponse;
};


export type AuthMutationsCredentialsFromFederatedCredentialArgs = {
  input: CredentialsFromFederatedCredentialInput;
};


export type AuthMutationsRefreshCredentialsArgs = {
  input: RefreshCredentialsInput;
};

export type AuthQueries = {
  __typename?: 'AuthQueries';
  authenticatedUser?: Maybe<User>;
  federatedIdentityProviders: Array<FederatedIdentityProvider>;
};

export type Cabinet = {
  __typename?: 'Cabinet';
  drawers: DrawerConnection;
  id: Scalars['ID']['output'];
  name: Scalars['String']['output'];
};


export type CabinetDrawersArgs = {
  after?: InputMaybe<Scalars['String']['input']>;
  first?: InputMaybe<Scalars['Int']['input']>;
};

export type CabinetConnection = {
  __typename?: 'CabinetConnection';
  count: Scalars['Int']['output'];
  edges: Array<CabinetEdge>;
  nodes: Array<Cabinet>;
  pageInfo: PageInfo;
};

export type CabinetEdge = {
  __typename?: 'CabinetEdge';
  cursor: Scalars['String']['output'];
  node: Cabinet;
};

export type Collection = {
  __typename?: 'Collection';
  component: Component;
  count: Scalars['Int']['output'];
  drawer: Drawer;
  id: Scalars['ID']['output'];
};

export type CollectionConnection = {
  __typename?: 'CollectionConnection';
  count: Scalars['Int']['output'];
  edges: Array<CollectionEdge>;
  nodes: Array<Collection>;
  pageInfo: PageInfo;
};

export type CollectionEdge = {
  __typename?: 'CollectionEdge';
  cursor: Scalars['String']['output'];
  node: Collection;
};

export type Component = {
  __typename?: 'Component';
  code: Scalars['String']['output'];
  collections: CollectionConnection;
  datasheetUrl?: Maybe<Scalars['String']['output']>;
  description?: Maybe<Scalars['String']['output']>;
  id: Scalars['ID']['output'];
};


export type ComponentCollectionsArgs = {
  after?: InputMaybe<Scalars['String']['input']>;
  first?: InputMaybe<Scalars['Int']['input']>;
};

export type ComponentConnection = {
  __typename?: 'ComponentConnection';
  count: Scalars['Int']['output'];
  edges: Array<ComponentEdge>;
  nodes: Array<Component>;
  pageInfo: PageInfo;
};

export type ComponentEdge = {
  __typename?: 'ComponentEdge';
  cursor: Scalars['String']['output'];
  node: Component;
};

export type CredentialsFromFederatedCredentialInput = {
  credential: Scalars['String']['input'];
  isNewUser?: Scalars['Boolean']['input'];
  provider: Scalars['String']['input'];
};

export type Drawer = {
  __typename?: 'Drawer';
  cabinet: Cabinet;
  collections: CollectionConnection;
  id: Scalars['ID']['output'];
  label: Scalars['String']['output'];
};


export type DrawerCollectionsArgs = {
  after?: InputMaybe<Scalars['String']['input']>;
  first?: InputMaybe<Scalars['Int']['input']>;
};

export type DrawerConnection = {
  __typename?: 'DrawerConnection';
  count: Scalars['Int']['output'];
  edges: Array<DrawerEdge>;
  nodes: Array<Drawer>;
  pageInfo: PageInfo;
};

export type DrawerEdge = {
  __typename?: 'DrawerEdge';
  cursor: Scalars['String']['output'];
  node: Drawer;
};

export type FederatedIdentityProvider = {
  __typename?: 'FederatedIdentityProvider';
  audience: Scalars['String']['output'];
  issuer: Scalars['String']['output'];
  name: Scalars['String']['output'];
};

export type Mutation = {
  __typename?: 'Mutation';
  auth: AuthMutations;
};

export type PageInfo = {
  __typename?: 'PageInfo';
  endCursor?: Maybe<Scalars['String']['output']>;
  hasNextPage: Scalars['Boolean']['output'];
  hasPreviousPage: Scalars['Boolean']['output'];
  startCursor?: Maybe<Scalars['String']['output']>;
};

export type Query = {
  __typename?: 'Query';
  auth: AuthQueries;
  cabinet?: Maybe<Cabinet>;
  cabinets: CabinetConnection;
  components: ComponentConnection;
};


export type QueryCabinetArgs = {
  id: Scalars['ID']['input'];
};


export type QueryCabinetsArgs = {
  after?: InputMaybe<Scalars['String']['input']>;
  first?: InputMaybe<Scalars['Int']['input']>;
};


export type QueryComponentsArgs = {
  after?: InputMaybe<Scalars['String']['input']>;
  first?: InputMaybe<Scalars['Int']['input']>;
  search?: InputMaybe<Scalars['String']['input']>;
};

export type RefreshCredentialsInput = {
  refreshToken: Scalars['String']['input'];
};

export type User = {
  __typename?: 'User';
  avatarUrl?: Maybe<Scalars['String']['output']>;
  displayName: Scalars['String']['output'];
  email?: Maybe<Scalars['String']['output']>;
  emailVerified: Scalars['Boolean']['output'];
  id: Scalars['ID']['output'];
};

export type UserCredentials = {
  __typename?: 'UserCredentials';
  accessToken: Scalars['String']['output'];
  expiresIn: Scalars['Int']['output'];
  refreshToken: Scalars['String']['output'];
  user: User;
};

export type ComponentSearchQueryVariables = Exact<{
  search: Scalars['String']['input'];
}>;


export type ComponentSearchQuery = { __typename?: 'Query', components: { __typename?: 'ComponentConnection', nodes: Array<{ __typename?: 'Component', code: string, description?: string | null, collections: { __typename?: 'CollectionConnection', nodes: Array<{ __typename?: 'Collection', count: number, drawer: { __typename?: 'Drawer', label: string, cabinet: { __typename?: 'Cabinet', name: string } } }> } }> } };

export type CredentialsFromFederatedCredentialMutationVariables = Exact<{
  input: CredentialsFromFederatedCredentialInput;
}>;


export type CredentialsFromFederatedCredentialMutation = { __typename?: 'Mutation', auth: { __typename?: 'AuthMutations', credentialsFromFederatedCredential: { __typename: 'AuthError', error: AuthErrorType, detail: string } | { __typename: 'UserCredentials', accessToken: string, refreshToken: string, expiresIn: number, user: { __typename?: 'User', id: string, displayName: string, avatarUrl?: string | null, email?: string | null } } } };

export type FederatedIdentityProvidersQueryVariables = Exact<{ [key: string]: never; }>;


export type FederatedIdentityProvidersQuery = { __typename?: 'Query', auth: { __typename?: 'AuthQueries', federatedIdentityProviders: Array<{ __typename?: 'FederatedIdentityProvider', name: string, issuer: string, audience: string }> } };

export type RefreshCredentialsMutationVariables = Exact<{
  input: RefreshCredentialsInput;
}>;


export type RefreshCredentialsMutation = { __typename?: 'Mutation', auth: { __typename?: 'AuthMutations', refreshCredentials: { __typename: 'AuthError', error: AuthErrorType, detail: string } | { __typename: 'UserCredentials', accessToken: string, refreshToken: string, expiresIn: number, user: { __typename?: 'User', id: string, displayName: string, avatarUrl?: string | null, email?: string | null } } } };


export const ComponentSearchDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"componentSearch"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"search"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"components"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"search"},"value":{"kind":"Variable","name":{"kind":"Name","value":"search"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"nodes"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"code"}},{"kind":"Field","name":{"kind":"Name","value":"description"}},{"kind":"Field","name":{"kind":"Name","value":"collections"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"nodes"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"count"}},{"kind":"Field","name":{"kind":"Name","value":"drawer"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"label"}},{"kind":"Field","name":{"kind":"Name","value":"cabinet"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"name"}}]}}]}}]}}]}}]}}]}}]}}]} as unknown as DocumentNode<ComponentSearchQuery, ComponentSearchQueryVariables>;
export const CredentialsFromFederatedCredentialDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"credentialsFromFederatedCredential"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"input"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"CredentialsFromFederatedCredentialInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"auth"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"credentialsFromFederatedCredential"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"input"},"value":{"kind":"Variable","name":{"kind":"Name","value":"input"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"__typename"}},{"kind":"InlineFragment","typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"UserCredentials"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"user"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"displayName"}},{"kind":"Field","name":{"kind":"Name","value":"avatarUrl"}},{"kind":"Field","name":{"kind":"Name","value":"email"}}]}},{"kind":"Field","name":{"kind":"Name","value":"accessToken"}},{"kind":"Field","name":{"kind":"Name","value":"refreshToken"}},{"kind":"Field","name":{"kind":"Name","value":"expiresIn"}}]}},{"kind":"InlineFragment","typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"AuthError"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"error"}},{"kind":"Field","name":{"kind":"Name","value":"detail"}}]}}]}}]}}]}}]} as unknown as DocumentNode<CredentialsFromFederatedCredentialMutation, CredentialsFromFederatedCredentialMutationVariables>;
export const FederatedIdentityProvidersDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"federatedIdentityProviders"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"auth"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"federatedIdentityProviders"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"issuer"}},{"kind":"Field","name":{"kind":"Name","value":"audience"}}]}}]}}]}}]} as unknown as DocumentNode<FederatedIdentityProvidersQuery, FederatedIdentityProvidersQueryVariables>;
export const RefreshCredentialsDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"refreshCredentials"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"input"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"RefreshCredentialsInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"auth"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"refreshCredentials"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"input"},"value":{"kind":"Variable","name":{"kind":"Name","value":"input"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"__typename"}},{"kind":"InlineFragment","typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"UserCredentials"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"user"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"displayName"}},{"kind":"Field","name":{"kind":"Name","value":"avatarUrl"}},{"kind":"Field","name":{"kind":"Name","value":"email"}}]}},{"kind":"Field","name":{"kind":"Name","value":"accessToken"}},{"kind":"Field","name":{"kind":"Name","value":"refreshToken"}},{"kind":"Field","name":{"kind":"Name","value":"expiresIn"}}]}},{"kind":"InlineFragment","typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"AuthError"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"error"}},{"kind":"Field","name":{"kind":"Name","value":"detail"}}]}}]}}]}}]}}]} as unknown as DocumentNode<RefreshCredentialsMutation, RefreshCredentialsMutationVariables>;