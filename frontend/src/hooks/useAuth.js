import { useContext } from "react";
import { AuthContext } from "../modules/auth/AuthProvider";

export default function useAuth() {
  return useContext(AuthContext);
}

