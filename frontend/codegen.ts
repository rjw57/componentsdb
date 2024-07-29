import { CodegenConfig } from "@graphql-codegen/cli";

const config: CodegenConfig = {
  schema: "../schema.gql",
  documents: ["src/**/*.{tsx,ts}"],
  ignoreNoDocuments: true, // for better experience with the watcher
  generates: {
    "./src/__generated__/": {
      preset: "client",
      plugins: [],
      presetConfig: {},
    },
  },
};

export default config;
