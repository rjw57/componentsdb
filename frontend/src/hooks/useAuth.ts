import React from "react";

import { AuthContext } from "../components/AuthProvider";

export const useAuth = () => React.useContext(AuthContext);
