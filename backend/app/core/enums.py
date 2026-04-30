from __future__ import annotations

try:
    from enum import StrEnum
except ImportError:
    from enum import Enum

    class StrEnum(str, Enum):
        def __str__(self) -> str:
            return self.value


class RoleKey(StrEnum):
    EMPLOYEE = "employee"
    HR = "hr"
    BD_SALES = "bd_sales"
    MANAGER = "manager"
    HOD = "hod"
    CEO_OFFICE = "ceo_office"
    SECURITY = "security"
    IT = "it"
    GATEKEEPER = "gatekeeper"
    ADMIN = "admin"


class VisitorType(StrEnum):
    SUPPLIER = "supplier"
    CANDIDATE = "candidate"
    CONTRACTOR = "contractor"
    CUSTOMER = "customer"
    VIP_CUSTOMER = "vip_customer"


class VisitorRequestStatus(StrEnum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    PENDING_MANAGER_APPROVAL = "pending_manager_approval"
    PENDING_HOD_APPROVAL = "pending_hod_approval"
    PENDING_CEO_OFFICE_APPROVAL = "pending_ceo_office_approval"
    PENDING_SECURITY_CLEARANCE = "pending_security_clearance"
    PENDING_IT_APPROVAL = "pending_it_approval"
    PENDING_LOGISTICS_CONFIRMATION = "pending_logistics_confirmation"
    APPROVED = "approved"
    REJECTED = "rejected"
    SENT_BACK = "sent_back"
    CANCELLED = "cancelled"
    CHECKED_IN = "checked_in"
    CHECKED_OUT = "checked_out"


class ApprovalStepStatus(StrEnum):
    QUEUED = "queued"
    ACTIVE = "active"
    APPROVED = "approved"
    REJECTED = "rejected"
    SENT_BACK = "sent_back"
    CANCELLED = "cancelled"
    SKIPPED = "skipped"


class ApprovalActionType(StrEnum):
    SUBMIT = "submit"
    APPROVE = "approve"
    REJECT = "reject"
    SEND_BACK = "send_back"
    CANCEL = "cancel"
    CHECK_IN = "check_in"
    CHECK_OUT = "check_out"
    SECURITY_ALERT = "security_alert"


class BadgeStatus(StrEnum):
    GENERATED = "generated"
    ISSUED = "issued"
    RETURNED = "returned"
    VOID = "void"


class GateAction(StrEnum):
    SCAN = "scan"
    CHECK_IN = "check_in"
    CHECK_OUT = "check_out"
    ACCESS_BLOCKED = "access_blocked"
    ACCESS_WARNING = "access_warning"


class BlacklistActionType(StrEnum):
    BLOCK = "block"
    ALERT = "alert"
    ALLOW_WITH_WARNING = "allow_with_warning"


class NotificationChannel(StrEnum):
    EMAIL = "email"
    SYSTEM = "system"
    SMS = "sms"
    WHATSAPP = "whatsapp"


class NotificationStatus(StrEnum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    READ = "read"


class EmergencyType(StrEnum):
    FIRE = "fire"
    MEDICAL = "medical"
    SECURITY = "security"
    DISASTER = "disaster"
    OTHER = "other"


class EmergencySeverity(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class EmergencyStatus(StrEnum):
    ACTIVE = "active"
    CONTAINED = "contained"
    RESOLVED = "resolved"


class MusterStatus(StrEnum):
    PENDING = "pending"
    ACCOUNTED_FOR = "accounted_for"
    UNACCOUNTED = "unaccounted"
    EVACUATED = "evacuated"


class InvitationStatus(StrEnum):
    PENDING = "pending"
    USED = "used"
    EXPIRED = "expired"
    CANCELLED = "cancelled"

