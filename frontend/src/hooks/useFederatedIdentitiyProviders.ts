import { useQuery } from "@apollo/client";

import { graphql } from "../__generated__/gql";

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

export const useFederatedIdentitiyProviders = () => useQuery(federatedIdentityProviders);

export default useFederatedIdentitiyProviders;
