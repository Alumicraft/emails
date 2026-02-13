import { Heading, Text } from "@react-email/components";
import { Layout, InfoCard, InfoRow, InfoAmount, Branding, toTitleCase } from "./shared";

export { Branding } from "./shared";

export interface QuotationEmailProps {
  branding: Branding;
  quotation_number: string;
  quotation_date: string;
  valid_until: string;
  customer_name?: string;
  total_amount: string;
  custom_message?: string;
}

export const QuotationEmail = ({
  branding,
  quotation_number,
  quotation_date,
  valid_until,
  customer_name,
  total_amount,
  custom_message,
}: QuotationEmailProps) => {
  return (
    <Layout branding={branding}>
      <Heading
        className="text-[22px] font-medium"
        style={{ color: branding.text_color, marginTop: 0 }}
      >
        Hello {toTitleCase(customer_name) || "there"},
      </Heading>

      <Text
        className="text-sm leading-6"
        style={{ color: branding.text_color }}
      >
        Please review the attached quotation at your earliest convenience.
      </Text>

      <InfoCard>
        <InfoRow label="Quotation No." value={quotation_number} />
        <InfoRow label="Valid Until" value={valid_until} valueColor="#dc2626" />
        <InfoAmount label="Estimated Total" value={total_amount} />
      </InfoCard>

      {custom_message && (
        <Text style={{ color: branding.text_color, fontSize: "16px", lineHeight: "1.6", marginBottom: "24px" }}>
          {custom_message}
        </Text>
      )}

      <Text
        className="text-sm leading-6"
        style={{ color: branding.tertiary_color }}
      >
        <em>We look forward to working with you!</em>
      </Text>
    </Layout>
  );
};

// Preview with sample data
export default function QuotationEmailPreview() {
  return (
    <QuotationEmail
      branding={{
        company: "Alumicraft",
        logo_url: "https://example.com/logo.png",
        primary_color: "#000000",
        tertiary_color: "#6b7280",
        text_color: "#1f2937",
        background_color: "#f3f4f6",
        font_family: "Arial, Helvetica, sans-serif",
      }}
      quotation_number="QTN-2025-001"
      quotation_date="February 12, 2025"
      valid_until="February 27, 2025"
      customer_name="John"
      total_amount="$1,250.00"
    />
  );
}
