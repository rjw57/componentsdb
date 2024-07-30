import { graphql } from "../__generated__/gql";
import wrapApolloUseMutation from "./wrapApolloUseMutation";

const refreshCredentials = graphql(`
  mutation refreshCredentials($input: RefreshCredentialsInput!) {
    auth {
      refreshCredentials(input: $input) {
        __typename
        ... on UserCredentials {
          user {
            id
            displayName
            avatarUrl
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

export const useRefreshCredentials = wrapApolloUseMutation(refreshCredentials);

export default useRefreshCredentials;
