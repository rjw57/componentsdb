import "./App.css";
import "graphiql/graphiql.css";

import { GraphiQL } from "graphiql";
import { createGraphiQLFetcher } from "@graphiql/toolkit";

const fetcher = createGraphiQLFetcher({
  url: "/graphql",
});

function App() {
  return <GraphiQL fetcher={fetcher} />;
}

export default App;
