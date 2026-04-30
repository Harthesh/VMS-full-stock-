import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import LoadError from "../components/common/LoadError";
import LoadingSpinner from "../components/common/LoadingSpinner";
import { createRequest } from "../api/requests";
import { fetchDepartments, fetchUserDirectory } from "../api/admin";
import RequestForm from "../modules/requests/RequestForm";

export default function RequestCreatePage() {
  const navigate = useNavigate();
  const [departments, setDepartments] = useState([]);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [submitError, setSubmitError] = useState("");

  useEffect(() => {
    Promise.all([fetchDepartments(), fetchUserDirectory().catch(() => [])])
      .then(([departmentData, userData]) => {
        setDepartments(departmentData);
        setUsers(userData);
      })
      .catch((apiError) => setError(apiError.response?.data?.detail || "Unable to prepare the request form."))
      .finally(() => setLoading(false));
  }, []);

  async function handleSubmit(payload) {
    setSubmitting(true);
    setSubmitError("");
    try {
      const record = await createRequest(payload);
      navigate(`/requests/${record.id}`);
    } catch (apiError) {
      setSubmitError(apiError.response?.data?.detail || "Unable to save the request.");
    } finally {
      setSubmitting(false);
    }
  }

  if (loading) return <LoadingSpinner label="Preparing form..." />;
  if (error) return <LoadError title="Request form unavailable" message={error} />;

  return (
    <RequestForm
      title="Create Visitor Request"
      departments={departments}
      users={users}
      onSubmit={handleSubmit}
      submitting={submitting}
      submitError={submitError}
    />
  );
}
