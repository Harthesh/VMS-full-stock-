from __future__ import annotations

import json
import time
import urllib.error
import urllib.request


BASE_URL = "http://127.0.0.1:8000/api/v1"
ADMIN_EMAIL = "admin@vms.example.com"
ADMIN_PASSWORD = "Admin@123"


class ApiClient:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.token = ""

    def request(self, method: str, path: str, payload: dict | None = None) -> dict | list:
        data = json.dumps(payload).encode("utf-8") if payload is not None else None
        request = urllib.request.Request(
            f"{self.base_url}{path}",
            data=data,
            method=method,
            headers={
                "Content-Type": "application/json",
                **({"Authorization": f"Bearer {self.token}"} if self.token else {}),
            },
        )
        try:
            with urllib.request.urlopen(request) as response:
                body = response.read().decode("utf-8")
                return json.loads(body) if body else {}
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8")
            raise RuntimeError(f"{method} {path} failed: {exc.code} {body}") from exc

    def login(self, email: str, password: str) -> dict:
        response = self.request("POST", "/auth/login", {"email": email, "password": password})
        self.token = response["access_token"]
        return response


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def create_test_payloads(admin_user_id: int, suffix: str, departments: list[dict]) -> tuple[dict, dict]:
    department_by_code = {item["code"]: item["id"] for item in departments}
    customer = {
        "visitor_type": "customer",
        "visit_date": "2026-04-05",
        "visit_time": "10:30:00",
        "department_id": department_by_code["SAL"],
        "host_user_id": admin_user_id,
        "visitor_name": f"Smoke Customer {suffix}",
        "company_name": "Acme Trading LLP",
        "mobile": f"90000{suffix[-5:]}",
        "email": f"smoke.customer.{suffix}@example.com",
        "id_proof_type": "Passport",
        "id_proof_number": f"P{suffix}",
        "purpose": "Customer product review meeting",
        "requires_security_clearance": True,
        "requires_it_access": False,
        "requires_hospitality": True,
        "remarks": "Front desk should guide visitor to conference room.",
        "hospitality": {
            "meal_required": True,
            "transport_required": True,
            "meeting_room": "Board Room 2",
            "escort_needed": True,
            "vip_notes": "Offer tea on arrival.",
            "remarks": "Keep projector ready.",
        },
        "panel_member_user_ids": [admin_user_id],
    }

    contractor = {
        "visitor_type": "contractor",
        "visit_date": "2026-04-06",
        "visit_time": "14:15:00",
        "department_id": department_by_code["INF"],
        "host_user_id": admin_user_id,
        "visitor_name": f"Smoke Contractor {suffix}",
        "company_name": "Infra Build Services",
        "mobile": f"91111{suffix[-5:]}",
        "email": f"smoke.contractor.{suffix}@example.com",
        "id_proof_type": "Aadhaar",
        "id_proof_number": f"A{suffix}",
        "purpose": "Server room maintenance and network audit",
        "requires_security_clearance": True,
        "requires_it_access": True,
        "requires_hospitality": True,
        "remarks": "Bring toolbox and laptop bag.",
        "hospitality": {
            "meal_required": False,
            "transport_required": False,
            "meeting_room": "IT Bay",
            "escort_needed": True,
            "vip_notes": "",
            "remarks": "Security escort required.",
        },
        "panel_member_user_ids": [admin_user_id],
    }
    return customer, contractor


def main() -> None:
    client = ApiClient(BASE_URL)
    login_response = client.login(ADMIN_EMAIL, ADMIN_PASSWORD)
    print("PASS login", login_response["user"]["email"])

    me = client.request("GET", "/auth/me")
    roles = client.request("GET", "/users/roles")
    departments = client.request("GET", "/users/departments")
    directory = client.request("GET", "/users/directory")
    assert_true(bool(roles), "Roles list is empty")
    assert_true(bool(departments), "Departments list is empty")
    assert_true(bool(directory), "User directory is empty")
    print("PASS reference data", len(roles), "roles", len(departments), "departments", len(directory), "users")

    suffix = str(int(time.time()))
    customer_payload, contractor_payload = create_test_payloads(me["id"], suffix, departments)

    customer = client.request("POST", "/visitor-requests", customer_payload)
    contractor = client.request("POST", "/visitor-requests", contractor_payload)
    assert_true(customer["visitor_name"] == customer_payload["visitor_name"], "Customer request was not created")
    assert_true(contractor["visitor_name"] == contractor_payload["visitor_name"], "Contractor request was not created")
    print("PASS create two requests", customer["request_no"], contractor["request_no"])

    updated_customer = client.request(
        "PATCH",
        f"/visitor-requests/{customer['id']}",
        {
            "purpose": "Customer product review meeting with hospitality and logistics confirmation",
            "remarks": "Updated through smoke test.",
            "meeting_room": None,
        },
    )
    assert_true("Updated through smoke test." in (updated_customer["remarks"] or ""), "Customer request update failed")
    print("PASS update request", updated_customer["request_no"])

    submitted_customer = client.request("POST", f"/visitor-requests/{customer['id']}/submit")
    submitted_contractor = client.request("POST", f"/visitor-requests/{contractor['id']}/submit")
    assert_true(submitted_customer["status"] == "pending_hod_approval", "Customer submit status mismatch")
    assert_true(submitted_contractor["status"] == "pending_hod_approval", "Contractor submit status mismatch")
    print("PASS submit requests")

    customer_after_hod = client.request(
        "POST",
        f"/approvals/{customer['id']}/actions",
        {"action": "approve", "remarks": "HOD approved during smoke test"},
    )
    assert_true(customer_after_hod["status"] == "pending_logistics_confirmation", "Customer HOD approval mismatch")

    customer_approved = client.request(
        "POST",
        f"/approvals/{customer['id']}/actions",
        {"action": "approve", "remarks": "Logistics confirmed during smoke test"},
    )
    assert_true(customer_approved["status"] == "approved", "Customer final approval mismatch")
    assert_true(bool(customer_approved.get("qr_code_value") or customer_approved.get("badge", {}).get("qr_code_value")), "QR not generated")
    print("PASS customer approval chain and QR generation")

    contractor_after_hod = client.request(
        "POST",
        f"/approvals/{contractor['id']}/actions",
        {"action": "approve", "remarks": "HOD approved contractor"},
    )
    assert_true(contractor_after_hod["status"] == "pending_security_clearance", "Contractor HOD approval mismatch")

    contractor_sent_back = client.request(
        "POST",
        f"/approvals/{contractor['id']}/actions",
        {"action": "send_back", "remarks": "Need revised contractor access notes"},
    )
    assert_true(contractor_sent_back["status"] == "sent_back", "Contractor send back failed")
    print("PASS contractor send-back flow")

    cancelled_contractor = client.request(
        "POST",
        f"/visitor-requests/{contractor['id']}/cancel",
        {"message": "Cancelled after send back in smoke test"},
    )
    assert_true(cancelled_contractor["status"] == "cancelled", "Contractor cancel failed")
    print("PASS contractor cancel flow")

    qr_value = customer_approved.get("badge", {}).get("qr_code_value") or customer_approved.get("qr_code_value")
    gate_lookup = client.request("POST", "/gate/lookup", {"qr_code_value": qr_value})
    assert_true(gate_lookup["can_check_in"] is True, "Gate lookup did not allow check-in")

    checked_in = client.request(
        "POST",
        f"/gate/{customer['id']}/check-in",
        {"gate_entry_point": "Main Gate", "remarks": "Smoke test check-in"},
    )
    assert_true(checked_in["status"] == "checked_in", "Check-in failed")

    checked_out = client.request(
        "POST",
        f"/gate/{customer['id']}/check-out",
        {"gate_entry_point": "Main Gate", "remarks": "Smoke test check-out"},
    )
    assert_true(checked_out["status"] == "checked_out", "Check-out failed")
    print("PASS gate lookup, check-in, and check-out")

    requests = client.request("GET", "/visitor-requests")
    pending = client.request("GET", "/approvals/pending")
    notifications = client.request("GET", "/notifications")
    dashboard = client.request("GET", "/dashboard/summary")
    assert_true(any(item["id"] == customer["id"] for item in requests), "Created customer request missing from list")
    assert_true(any(item["id"] == contractor["id"] for item in requests), "Created contractor request missing from list")
    assert_true(isinstance(pending, list), "Pending approvals endpoint failed")
    assert_true(isinstance(notifications, list), "Notifications endpoint failed")
    assert_true("total_requests_today" in dashboard, "Dashboard summary endpoint failed")
    print("PASS list/dashboard/notifications endpoints")

    print("DONE")
    print(json.dumps({"customer_request_no": customer["request_no"], "contractor_request_no": contractor["request_no"]}, indent=2))


if __name__ == "__main__":
    main()
