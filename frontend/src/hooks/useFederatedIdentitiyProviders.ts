import { graphql } from "../__generated__/gql";
import wrapApolloUseQuery from "./wrapApolloUseQuery";

const federatedIdentityProviders = graphql(`
  query federatedIdentityProviders {
    auth {
      federatedIdentityProviders {
        name
        issuer
        audience
      }
    }
  }
`);

export const useFederatedIdentitiyProviders = wrapApolloUseQuery(federatedIdentityProviders);

export default useFederatedIdentitiyProviders;
