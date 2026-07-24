# Structured Tools Design

Changing transactional records should be read from a database or API instead of embedded as knowledge documents because they change frequently and may contain private user-specific information.

The first version must not execute unrestricted SQL, modify bookings automatically, cancel bookings automatically, issue refunds automatically, or change court availability automatically.

## Tool: get_booking_status

- Purpose: Read current booking status.
- Input schema: `{"booking_id":"BK-1001","user_id":"USR-001"}`
- Output schema: `{"booking_id":"BK-1001","status":"confirmed","court_id":"CRT-001","slot_start":"2026-08-01T18:00:00","amount_due":0}`
- Validation rules: Booking ID required; user must own booking or be authorized support/admin.
- Error cases: Not found, unauthorized, invalid ID.
- Authorization: Customer can read own booking; support/admin can read assigned cases.
- Example request: `{"booking_id":"BK-1001","user_id":"USR-001"}`
- Example response: `{"booking_id":"BK-1001","status":"confirmed","payment_status":"verified"}`
- Routes: `booking_status`, `booking_troubleshooting`.

## Tool: get_payment_status

- Purpose: Read current payment and verification state.
- Input schema: `{"payment_id":"PAY-2001","booking_id":"BK-1001","user_id":"USR-001"}`
- Output schema: `{"payment_id":"PAY-2001","status":"verified","amount":3000,"currency":"PKR","verified_at":"2026-07-20T10:15:00"}`
- Validation rules: Payment or booking ID required.
- Error cases: Not found, duplicate candidate, unauthorized.
- Authorization: Same as booking.
- Example request: `{"booking_id":"BK-1001","user_id":"USR-001"}`
- Example response: `{"payment_id":"PAY-2001","status":"verified","review_eta_minutes":0}`
- Routes: `payment_status`, `duplicate_payment`.

## Tool: get_notification_history

- Purpose: Read WhatsApp/SMS notification events.
- Input schema: `{"booking_id":"BK-1001","user_id":"USR-001"}`
- Output schema: `{"booking_id":"BK-1001","notifications":[{"type":"booking_confirmed","status":"delivered"}]}`
- Validation rules: Booking ID required.
- Error cases: No notifications, provider unavailable, unauthorized.
- Authorization: User must own booking or be support/admin.
- Example response: `{"notifications":[{"id":"NTF-3001","type":"payment_received","status":"delivered"}]}`
- Routes: `notification_history`, `missing_message`.

## Tool: get_court_availability

- Purpose: Read current available slots for a court.
- Input schema: `{"court_id":"CRT-001","date":"2026-08-01"}`
- Output schema: `{"court_id":"CRT-001","date":"2026-08-01","available_slots":["18:00","19:00"]}`
- Validation rules: Court ID and date required.
- Error cases: Court not found, invalid date.
- Authorization: Public for customer availability; owner/admin can see blocked reasons.
- Routes: `court_availability`.

## Tool: search_previous_tickets

- Purpose: Find authorized previous support tickets.
- Input schema: `{"user_id":"USR-001","booking_id":"BK-1001","query":"refund"}`
- Output schema: `{"tickets":[{"ticket_id":"TCK-4001","status":"open","summary":"Refund delay"}]}`
- Validation rules: At least one search key required.
- Error cases: Not found, unauthorized.
- Authorization: Customer owns ticket; support/admin has scoped access.
- Routes: `previous_ticket`, `human_escalation_context`.

