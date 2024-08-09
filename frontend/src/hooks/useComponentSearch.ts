import { graphql } from "../__generated__/gql";
import wrapApolloUseQuery from "./wrapApolloUseQuery";

const componentSearch = graphql(`
  query componentSearch($search: String!) {
    components(search: $search) {
      nodes {
        code
        description
        collections {
          nodes {
            count
            drawer {
              label
              cabinet {
                name
              }
            }
          }
        }
      }
    }
  }
`);

export const useComponentSearch = wrapApolloUseQuery(componentSearch);

export default useComponentSearch;
