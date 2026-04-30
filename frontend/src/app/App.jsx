import { BrowserRouter } from "react-router-dom";
import AuthProvider from "../modules/auth/AuthProvider";
import AppRouter from "../router";

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <AppRouter />
      </BrowserRouter>
    </AuthProvider>
  );
}

