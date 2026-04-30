import { useState } from "react";
import { useNavigate } from "react-router-dom";
import Button from "../../components/common/Button";
import FormField from "../../components/common/FormField";
import useAuth from "../../hooks/useAuth";

export default function LoginForm() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [values, setValues] = useState({ email: "", password: "" });
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setSubmitting(true);
    setError("");
    try {
      await login(values);
      navigate("/dashboard");
    } catch (apiError) {
      if (!apiError.response) {
        setError("Cannot reach the server. Start the backend on port 8000 and try again.");
      } else {
        setError(apiError.response?.data?.detail || "Login failed");
      }
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form className="space-y-4" onSubmit={handleSubmit}>
      <FormField
        label="Email"
        type="email"
        value={values.email}
        onChange={(event) => setValues((current) => ({ ...current, email: event.target.value }))}
      />
      <FormField
        label="Password"
        type="password"
        value={values.password}
        onChange={(event) => setValues((current) => ({ ...current, password: event.target.value }))}
      />
      {error && <div className="rounded-xl bg-red-50 px-3 py-2 text-sm text-red-700">{error}</div>}
      <Button type="submit" className="w-full" disabled={submitting}>
        {submitting ? "Signing in..." : "Sign In"}
      </Button>
    </form>
  );
}
