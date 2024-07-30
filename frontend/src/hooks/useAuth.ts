import React from "react";

import { AuthContext } from "../contexts";

export const useAuth = () => React.useContext(AuthContext);
