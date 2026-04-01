from __future__ import annotations

from dataclasses import dataclass

from app.core.enums import RoleKey, VisitorRequestStatus, VisitorType


@dataclass(frozen=True)
class WorkflowStepDefinition:
    step_key: str
    step_name: str
    role_key: RoleKey
    pending_status: VisitorRequestStatus


CREATOR_ROLE_RULES: dict[VisitorType, set[RoleKey]] = {
    VisitorType.SUPPLIER: {RoleKey.EMPLOYEE},
    VisitorType.CONTRACTOR: {RoleKey.EMPLOYEE},
    VisitorType.CANDIDATE: {RoleKey.HR},
    VisitorType.CUSTOMER: {RoleKey.BD_SALES},
    VisitorType.VIP_CUSTOMER: {RoleKey.BD_SALES},
}


def build_workflow(
    visitor_type: VisitorType,
    *,
    requires_it_access: bool,
    requires_hospitality: bool,
) -> list[WorkflowStepDefinition]:
    if visitor_type == VisitorType.SUPPLIER:
        return [
            WorkflowStepDefinition(
                step_key="manager_approval",
                step_name="Manager Approval",
                role_key=RoleKey.MANAGER,
                pending_status=VisitorRequestStatus.PENDING_MANAGER_APPROVAL,
            )
        ]
    if visitor_type == VisitorType.CONTRACTOR:
        steps = [
            WorkflowStepDefinition(
                step_key="hod_approval",
                step_name="HOD Approval",
                role_key=RoleKey.HOD,
                pending_status=VisitorRequestStatus.PENDING_HOD_APPROVAL,
            ),
            WorkflowStepDefinition(
                step_key="security_clearance",
                step_name="Security Clearance",
                role_key=RoleKey.SECURITY,
                pending_status=VisitorRequestStatus.PENDING_SECURITY_CLEARANCE,
            ),
        ]
        if requires_it_access:
            steps.append(
                WorkflowStepDefinition(
                    step_key="it_approval",
                    step_name="IT Approval",
                    role_key=RoleKey.IT,
                    pending_status=VisitorRequestStatus.PENDING_IT_APPROVAL,
                )
            )
        return steps
    if visitor_type == VisitorType.CUSTOMER:
        steps = [
            WorkflowStepDefinition(
                step_key="hod_approval",
                step_name="HOD Approval",
                role_key=RoleKey.HOD,
                pending_status=VisitorRequestStatus.PENDING_HOD_APPROVAL,
            )
        ]
        if requires_hospitality:
            steps.append(
                WorkflowStepDefinition(
                    step_key="logistics_confirmation",
                    step_name="Logistics Confirmation",
                    role_key=RoleKey.BD_SALES,
                    pending_status=VisitorRequestStatus.PENDING_LOGISTICS_CONFIRMATION,
                )
            )
        return steps
    if visitor_type == VisitorType.VIP_CUSTOMER:
        return [
            WorkflowStepDefinition(
                step_key="hod_approval",
                step_name="HOD Approval",
                role_key=RoleKey.HOD,
                pending_status=VisitorRequestStatus.PENDING_HOD_APPROVAL,
            ),
            WorkflowStepDefinition(
                step_key="ceo_office_approval",
                step_name="CEO Office Approval",
                role_key=RoleKey.CEO_OFFICE,
                pending_status=VisitorRequestStatus.PENDING_CEO_OFFICE_APPROVAL,
            ),
            WorkflowStepDefinition(
                step_key="logistics_confirmation",
                step_name="Logistics Confirmation",
                role_key=RoleKey.BD_SALES,
                pending_status=VisitorRequestStatus.PENDING_LOGISTICS_CONFIRMATION,
            ),
        ]
    return []

