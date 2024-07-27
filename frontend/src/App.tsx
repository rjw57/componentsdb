import "./App.css";
import "graphiql/graphiql.css";

import { GraphiQL } from "graphiql";
import { createGraphiQLFetcher } from "@graphiql/toolkit";
import { GoogleLogin } from "@react-oauth/google";

const fetcher = createGraphiQLFetcher({
  url: "/graphql",
});

function App() {
  return (
    <>
      <GoogleLogin
        onSuccess={(credentialResponse) => {
          console.log(credentialResponse);
        }}
        onError={() => {
          console.log("Login Failed");
        }}
        use_fedcm_for_prompt={true}
      />
      <GraphiQL fetcher={fetcher} />
    </>
  );
}

export default App;
