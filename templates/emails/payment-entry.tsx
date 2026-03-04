import { Heading, Text } from "@react-email/components";
import { Layout, InfoCard, InfoRow, InfoAmount, Branding } from "./shared";

export { Branding } from "./shared";

export interface PaymentEntryEmailProps {
  branding: Branding;
  receipt_number: string;
  payment_date: string;
  mode_of_payment?: string;
  reference_no?: string;
  paid_amount: string;
  applied_to?: string;
  remarks?: string;
  custom_message?: string;
}

export const PaymentEntryEmail = ({
  branding,
  receipt_number,
  payment_date,
  mode_of_payment,
  reference_no,
  paid_amount,
  applied_to,
  remarks,
  custom_message,
}: PaymentEntryEmailProps) => {
  return (
    <Layout branding={branding}>
      <Heading
        className="text-[24px] font-medium email-heading"
        style={{ color: branding.text_color, marginTop: 0 }}
      >
        Payment Receipt
      </Heading>

      <Text
        className="text-[15px] leading-6 email-text"
        style={{ color: branding.text_color }}
      >
        Thank you for your payment. Please find your receipt details below.
      </Text>

      <InfoCard branding={branding}>
        <InfoRow branding={branding} label="Receipt No." value={receipt_number} />
        <InfoRow branding={branding} label="Date" value={payment_date} />
        {mode_of_payment && <InfoRow branding={branding} label="Payment Method" value={mode_of_payment} />}
        {reference_no && <InfoRow branding={branding} label="Reference No." value={reference_no} />}
        {applied_to && <InfoRow branding={branding} label="Applied To" value={applied_to} />}
        <InfoAmount branding={branding} label="Amount Paid" value={paid_amount} />
      </InfoCard>

      {remarks && (
        <Text style={{ color: branding.text_color, fontSize: "14px", lineHeight: "1.6", marginBottom: "16px" }}>
          <strong>Remarks:</strong> {remarks}
        </Text>
      )}

      {custom_message && (
        <Text style={{ color: branding.text_color, fontSize: "16px", lineHeight: "1.6", marginBottom: "24px" }}>
          {custom_message}
        </Text>
      )}

      <Text
        className="text-[15px] leading-6"
        style={{ color: branding.tertiary_color }}
      >
        <em>Thank you for your payment!</em>
      </Text>
    </Layout>
  );
};

// Preview with sample data
export default function PaymentEntryEmailPreview() {
  return (
    <PaymentEntryEmail
      branding={{
        company: "Alumicraft",
        logo_url: "https://example.com/logo.png",
        primary_color: "#006CFF",
        tertiary_color: "#9A9A9A",
        text_color: "#0f0f0f",
        background_color: "#f5f5f5",
        card_color: "#ffffff",
        border_color: "#e5e7eb",
        amount_bg_color: "#e5e7eb",
        primary_color_dark: "#4D8DFF",
        tertiary_color_dark: "#6B7280",
        text_color_dark: "#E5E7EB",
        background_color_dark: "#E5E7EB",
        card_color_dark: "#000000",
        border_color_dark: "#4b5563",
        amount_bg_color_dark: "#374151",
        font_family: "Arial, Helvetica, sans-serif",
      }}
      receipt_number="PE-2025-001"
      payment_date="February 12, 2025"
      mode_of_payment="Bank Transfer"
      reference_no="TXN-987654"
      paid_amount="$1,250.00"
      applied_to="SINV-2025-001, SINV-2025-002"
      remarks="Payment for January services"
    />
  );
}
