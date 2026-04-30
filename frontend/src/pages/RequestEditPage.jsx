import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import LoadError from "../components/common/LoadError";
import LoadingSpinner from "../components/common/LoadingSpinner";
import { fetchDepartments, fetchUserDirectory } from "../api/admin";
import { fetchRequest, updateRequest } from "../api/requests";
import RequestForm from "../modules/requests/RequestForm";

export default function RequestEditPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [request, setRequest] = useState(null);
  const [departments, setDepartments] = useState([]);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [submitError, setSubmitError] = useState("");

  useEffect(() => {
    Promise.all([fetchRequest(id), fetchDepartments(), fetchUserDirectory().catch(() => [])])
      .then(([requestData, departmentData, userData]) => {
        setRequest(requestData);
        setDepartments(departmentData);
        setUsers(userData);
      })
      .catch((apiError) => setError(apiError.response?.data?.detail || "Unable to load this request for editing."))
      .finally(() => setLoading(false));
  }, [id]);

  async function handleSubmit(payload) {
    setSubmitting(true);
    setSubmitError("");
    try {
      await updateRequest(id, payload);
      navigate(`/requests/${id}`);
    } catch (apiError) {
      setSubmitError(apiError.response?.data?.detail || "Unable to save the request.");
    } finally {
      setSubmitting(false);
    }
  }

  if (loading) return <LoadingSpinner label="Loading request..." />;
  if (error || !request) {
    return <LoadError title="Edit page unavailable" message={error || "Unable to load this request for editing."} />;
  }

  return (
    <RequestForm
      title="Edit Draft Request"
      initialValues={request}
      departments={departments}
      users={users}
      onSubmit={handleSubmit}
      submitting={submitting}
      submitError={submitError}
    />
  );
}
