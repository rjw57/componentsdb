import React from "react";

//import { GoogleOAuthProvider } from "@react-oauth/google";
/*
    <GoogleOAuthProvider clientId={process.env.REACT_APP_GOOGLE_CLIENT_ID ?? ""}>
      <App />
    </GoogleOAuthProvider>
  */
console.log(`Google client id: ${process.env.REACT_APP_GOOGLE_CLIENT_ID}`);

export interface AuthState {}

export const AuthContext = React.createContext<AuthState | null>(null);

export default AuthContext;
