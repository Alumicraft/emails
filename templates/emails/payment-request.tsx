import { Heading, Text, Section } from "@react-email/components";
import { Layout, InfoCard, InfoRow, InfoAmount, Button, Branding, toTitleCase } from "./shared";

export { Branding } from "./shared";

export interface PaymentRequestEmailProps {
  branding: Branding;
  reference_number?: string;
  due_date?: string;
  project_name?: string;
  customer_name?: string;
  amount_requested: string;
  stripe_payment_url?: string;
  custom_message?: string;
}

export const PaymentRequestEmail = ({
  branding,
  reference_number,
  due_date,
  project_name,
  customer_name,
  amount_requested,
  stripe_payment_url,
  custom_message,
}: PaymentRequestEmailProps) => {
  return (
    <Layout branding={branding}>
      <Heading
        className="email-heading"
        style={{ color: branding.text_color, marginTop: 0, fontSize: "24px", fontWeight: 500, lineHeight: "32px" }}
      >
        New Payment Request
      </Heading>

      <Text
        className="email-text"
        style={{ color: branding.text_color, fontSize: "15px", lineHeight: "24px" }}
      >
        Please review the attached PDF and submit payment at your earliest convenience.
      </Text>

      <InfoCard branding={branding}>
        {reference_number && <InfoRow branding={branding} label="Reference No." value={reference_number} />}
        {project_name && <InfoRow branding={branding} label="Project" value={project_name} />}
        {due_date && <InfoRow branding={branding} label="Due Date" value={due_date} />}
        <InfoAmount branding={branding} label="Amount" value={amount_requested} />
      </InfoCard>

      {custom_message && (
        <Text style={{ color: branding.text_color, fontSize: "16px", lineHeight: "1.6", marginBottom: "24px" }}>
          {custom_message}
        </Text>
      )}

      <Text
        style={{ color: branding.tertiary_color, fontSize: "15px", lineHeight: "24px" }}
      >
        <em>Thank you for your business!</em>
      </Text>

      {stripe_payment_url && (
        <Section style={{ marginTop: "32px", marginBottom: "32px" }}>
          <Button
            href={stripe_payment_url}
            color={branding.primary_color}
            textColor={branding.button_text_color}
          >
            Pay Invoice
          </Button>
        </Section>
      )}
    </Layout>
  );
};

// Preview with sample data
export default function PaymentRequestEmailPreview() {
  return (
    <PaymentRequestEmail
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
      reference_number="PR-2025-001"
      due_date="February 27, 2025"
      project_name="Website Redesign"
      customer_name="JOHN DOE"
      amount_requested="$500.00"
      stripe_payment_url="https://example.com/pay/123"
    />
  );
}
