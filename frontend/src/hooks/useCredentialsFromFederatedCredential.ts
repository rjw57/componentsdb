import { graphql } from "../__generated__/gql";
import wrapApolloUseMutation from "./wrapApolloUseMutation";

const credentialsFromFederatedCredential = graphql(`
  mutation credentialsFromFederatedCredential($input: CredentialsFromFederatedCredentialInput!) {
    auth {
      credentialsFromFederatedCredential(input: $input) {
        __typename
        ... on UserCredentials {
          user {
            id
            displayName
            avatarUrl
            email
          }
          accessToken
          refreshToken
          expiresIn
        }
        ... on AuthError {
          error
          detail
        }
      }
    }
  }
`);

export const useCredentialsFromFederatedCredential = wrapApolloUseMutation(
  credentialsFromFederatedCredential,
);

export default useCredentialsFromFederatedCredential;
